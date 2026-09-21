package com.athleticism.app;

import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.util.Base64;
import androidx.activity.result.ActivityResult;
import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.ActivityCallback;
import com.getcapacitor.annotation.CapacitorPlugin;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;

/*
 * Android's own "Save to" screen for the backup files.
 *
 * The page's export is a download of a blob: URL, and inside this app's
 * WebView a download has nowhere to go - nothing happens, while the page
 * believed it had worked. There is no share sheet in a WebView either. So the
 * page hands the file over here and the person picks where it goes: Downloads,
 * Drive, anything that shows up as a document provider.
 *
 * Two calls, not one. The request that waits on the picker is kept by
 * Capacitor, and written into the activity's saved state while the picker is
 * in front; a whole backup in there is past what that state may hold, and the
 * app would crash the moment the picker opened. So the file is written to the
 * app's cache by stage() first, and save() carries only the name.
 */
@CapacitorPlugin(name = "SaveFile")
public class SaveFilePlugin extends Plugin {

    private File staged() {
        return new File(getContext().getCacheDir(), "pending-save");
    }

    @PluginMethod
    public void stage(PluginCall call) {
        String text = call.getString("text");
        String base64 = call.getString("base64");
        if (text == null && base64 == null) {
            call.reject("Nothing to save");
            return;
        }
        try (OutputStream out = new FileOutputStream(staged(), false)) {
            out.write(text != null ? text.getBytes(StandardCharsets.UTF_8) : Base64.decode(base64, Base64.DEFAULT));
            call.resolve();
        } catch (Exception e) {
            call.reject("Could not prepare the file", e);
        }
    }

    @PluginMethod
    public void save(PluginCall call) {
        if (!staged().exists()) {
            call.reject("Nothing staged");
            return;
        }
        Intent intent = new Intent(Intent.ACTION_CREATE_DOCUMENT);
        intent.addCategory(Intent.CATEGORY_OPENABLE);
        intent.setType(call.getString("mime", "application/octet-stream"));
        intent.putExtra(Intent.EXTRA_TITLE, call.getString("filename", "athleticism-backup"));
        startActivityForResult(call, intent, "onPicked");
    }

    @ActivityCallback
    private void onPicked(PluginCall call, ActivityResult result) {
        if (call == null) return;
        JSObject ret = new JSObject();
        Intent data = result.getData();
        Uri uri = data == null ? null : data.getData();
        if (result.getResultCode() != Activity.RESULT_OK || uri == null) {
            staged().delete();
            ret.put("saved", false);
            call.resolve(ret);
            return;
        }
        try {
            copyTo(uri);
            ret.put("saved", true);
            call.resolve(ret);
        } catch (Exception e) {
            call.reject("Could not write the file", e);
        } finally {
            staged().delete();
        }
    }

    /* "wt" truncates, which is what a fresh document wants; not every
       provider accepts it, and those get plain "w". */
    private void copyTo(Uri uri) throws Exception {
        OutputStream out;
        try {
            out = getContext().getContentResolver().openOutputStream(uri, "wt");
        } catch (Exception e) {
            out = getContext().getContentResolver().openOutputStream(uri, "w");
        }
        if (out == null) throw new java.io.IOException("No output stream for " + uri);
        try (InputStream in = new FileInputStream(staged()); OutputStream o = out) {
            byte[] buf = new byte[64 * 1024];
            int n;
            while ((n = in.read(buf)) > 0) o.write(buf, 0, n);
            o.flush();
        }
    }
}

package com.athleticism.app;

import android.os.Bundle;
import android.webkit.WebView;
import androidx.activity.OnBackPressedCallback;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        registerPlugin(SaveFilePlugin.class);
        super.onCreate(savedInstanceState);

        /* Back closes whatever the page has open first - a pop-up, the
           exercise picker, a detail screen - the way it does in any Android
           app. Left to itself it closed the whole app, even mid-workout with
           Settings open. The page answers whether it closed something; only
           when it had nothing left does the app step aside, into the
           background where a running rest timer keeps its place. */
        getOnBackPressedDispatcher().addCallback(this, new OnBackPressedCallback(true) {
            @Override
            public void handleOnBackPressed() {
                WebView web = bridge == null ? null : bridge.getWebView();
                if (web == null) {
                    moveTaskToBack(true);
                    return;
                }
                web.evaluateJavascript(
                    "(function(){try{return !!(window.athleticismBack&&window.athleticismBack());}catch(e){return false;}})()",
                    handled -> {
                        if (!"true".equals(handled)) moveTaskToBack(true);
                    }
                );
            }
        });
    }
}

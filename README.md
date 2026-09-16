# Athleticism

A workout tracker that lives on your device. No account, no sync, no
subscription — your data is stored in the browser and never leaves it.

Built for a training mix that most apps can't describe: lifting, calisthenics,
skill holds, breakdance. Every exercise defines its own tracking fields
(weight, reps, measured time, RIR/RPE, or anything custom), so a bench press
and a handstand hold are the same kind of object.

**Live:** https://YOUR-USERNAME.github.io/athleticism/

---

## Repo layout

```
docs/                  the app. GitHub Pages serves this folder,
  index.html           and Capacitor bundles it into the APK.
  manifest.json        One source of truth, two consumers.
  sw.js
  icons/
tools/
  icon.py              regenerates the app icons from SVG
  legacy-build/        how index.html was originally generated (see below)
```

`docs/index.html` is a single self-contained file — all CSS, JavaScript, the
mascot artwork and the app icons are inline. It works opened straight off disk,
which is what makes the portable backup format possible.

### About `tools/legacy-build/`

The first version of this app was produced by a Python pipeline that patched a
base HTML file. That made sense while the app lived in chat attachments. It
does not make sense for a repo you maintain.

**`docs/index.html` is now the source of truth. Edit it directly.** The
`legacy-build/` folder is kept for reference only — it explains where things
came from and holds the original base file. Don't run it; it would overwrite
your changes.

`tools/icon.py` is the exception and is still live — run it when you want to
regenerate the icons.

---

## Deploying a change

1. Edit `docs/index.html`.
2. **Bump `CACHE_VERSION` in `docs/sw.js`** (`v1` → `v2`, and so on).
3. Commit and push. GitHub Pages redeploys in about a minute.

Step 2 matters. The service worker serves the cached copy first so the app
opens instantly with no signal, and fetches the update in the background. Skip
the bump and phones keep the old version. Even with the bump, the first open
after a deploy shows the old app and the second shows the new one — that trade
is deliberate, because the alternative is making every gym session wait on a
connection that might not be there.

### GitHub Pages settings

Settings → Pages → Source: *Deploy from a branch* → Branch: `main`, folder:
`/docs`.

---

## Android APK

The plan is Capacitor, which wraps `docs/` in a real Android app. The web files
ship inside the APK, so it works with no network from first launch and needs no
hosting at all.

```bash
npm init -y
npm install @capacitor/core @capacitor/cli @capacitor/android
npx cap init Athleticism com.yourname.athleticism --web-dir=docs
npx cap add android
npx cap sync
```

Then open `android/` in Android Studio and use Build → Build APK(s), or from
the command line:

```bash
cd android && ./gradlew assembleDebug
```

The APK lands in `android/app/build/outputs/apk/debug/`.

**Known gap before this is worth doing:** the fonts are still loaded from
Google Fonts. The service worker caches them after the first online load, so
the PWA is fine — but the APK has no service worker, so offline it would fall
back to a system font and look wrong. Download the Nunito and Baloo 2 woff2
files into `docs/fonts/`, swap the `<link>` in `index.html` for a local
`@font-face` block, and the last external dependency is gone for both.

---

## Where your data lives

Each install is its own island. Data is keyed to the exact origin it was
entered on:

| Where | Stored under |
|---|---|
| Laptop browser | `your-username.github.io` |
| iPhone home screen | same origin, same store as Safari |
| Android APK | the app's own WebView storage |

So the phone app and the laptop do **not** share data, and changing the site
address orphans anything already logged. Moving between them is what
Settings → Export is for: `.json` for a compact backup, or a portable `.html`
that is itself a full working copy of the app with the data baked in.

Browsers can evict local storage for sites you haven't opened in a while. Being
installed to the home screen makes that much less likely, but exporting a real
file now and then is the only actual guarantee.

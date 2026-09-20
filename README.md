# Athleticism

A workout tracker that lives on your device. No account, no sync, no
subscription — your data is stored in the browser and never leaves it.

Built for a training mix that most apps can't describe: lifting, calisthenics,
skill holds, breakdance. Every exercise defines its own tracking fields
(weight, reps, measured time, RIR/RPE, or anything custom), so a bench press
and a handstand hold are the same kind of object.

Progress photos live under **Progress → Photos**, tagged by angle (front, side,
back, or your own). When you crop a new one, the last shot in that angle is
laid over the frame so the months actually line up.

**Muscle coverage** sits at the top of **Progress → Sessions**: front and back
diagrams coloured by how much each muscle was worked over the last 7 days, and
the same pair inside each plan showing what that session emphasises. It counts
*sets*, not exercises — five sets of pull-ups should outweigh one set of curls.
The weekly view scores against a target rather than against your own best
muscle, so the ones you keep skipping stay grey instead of being normalised up
into colour. It shows volume, not strength; the load and 1RM charts are still
their own thing.

**Live:** https://neirko.github.io/athleticism/

---

## Repo layout

```
docs/                  the app. GitHub Pages serves this folder,
  index.html           and Capacitor bundles it into the APK.
  manifest.json        One source of truth, two consumers.
  sw.js
  fonts/               Nunito + Baloo 2, self-hosted (SIL OFL)
  icons/
android/               Capacitor's Android project
capacitor.config.json
package.json
tools/
  icon.py              regenerates the app icons from SVG
  legacy-build/        how index.html was originally generated (see below)
  muscle-map-kit/      the body diagrams, as shipped (MIT). Reference only —
                       the renderer and geometry are inlined into index.html
```

`docs/index.html` is a single self-contained file — all CSS, JavaScript, the
mascot artwork and the app icons are inline. The one exception is the fonts,
which sit in `docs/fonts/`. It works opened straight off disk, which is what
makes the portable backup format possible. A portable backup has no `fonts/`
folder beside it, so the export points its copy at Google Fonts instead: the
rounded type when it's opened online, the system font when it isn't.

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

Capacitor wraps `docs/` in a real Android app (app ID `com.athleticism.app`,
set in `capacitor.config.json`). The web files ship inside the APK, so it works
with no network from first launch and needs no hosting at all.

Android Studio isn't needed. The build needs JDK 21 and the Android SDK in
`~/Library/Android/sdk`. Gradle finds the SDK through `android/local.properties`,
which is untracked; on a fresh clone, recreate it with
`echo "sdk.dir=$HOME/Library/Android/sdk" > android/local.properties`.

```bash
brew install openjdk@21
npm install
```

After any change to `docs/`, rebuild with:

```bash
npm run apk
```

That copies `docs/` into the Android project and runs `./gradlew assembleDebug`.
It uses Homebrew's JDK 21 unless `JAVA_HOME` is already set. The APK lands in
`android/app/build/outputs/apk/debug/`.

---

## Where your data lives

Each install is its own island. Data is keyed to the exact origin it was
entered on:

| Where | Stored under |
|---|---|
| Laptop browser | `neirko.github.io` |
| iPhone home screen | same origin, same store as Safari |
| Android APK | the app's own WebView storage |

Progress photos are the one exception to "it's all one blob". Everything else
is a single JSON string in `localStorage`, which `save()` rewrites every time
you tick off a set — fine for text, hopeless for images, and `localStorage`
tops out around 5MB anyway. So photo **metadata** (date, angle, note) stays in
that blob, and the JPEGs themselves go in **IndexedDB** under
`athleticism_photos`, where the quota is far larger. Two consequences:

- A `.json` or portable `.html` backup **skips photos** unless you switch
  *Settings → Include Progress Photos* on, which inlines them as base64. Off is
  the default, because on turns a backup you can email into one you can't.
- *Settings → Export Progress Photos* writes a `.zip` of dated `.jpg` files.
  That one is an archive for your photo library — the app does not read it back.

So the phone app and the laptop do **not** share data, and changing the site
address orphans anything already logged. Moving between them is what
Settings → Export is for: `.json` for a compact backup, or a portable `.html`
that is itself a full working copy of the app with the data baked in.

Browsers can evict local storage for sites you haven't opened in a while. Being
installed to the home screen makes that much less likely, but exporting a real
file now and then is the only actual guarantee.

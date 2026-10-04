# Hanzi Arcade: web, desktop, Android

`www/index.html` is the whole app (single file, works offline, audio embedded).

## Adding Levels 5 and 6
Download both decks from AnkiWeb in a browser (Download button), then:
```
python3 tools/apkg_to_level.py ~/Downloads/<level-5-deck>.apkg data/level5.json
python3 tools/apkg_to_level.py ~/Downloads/<level-6-deck>.apkg data/level6.json
npm run build:web
```
(`ffmpeg` on PATH shrinks the audio to match Levels 1-4; without it the audio is embedded as-is, so the app is bigger.)
The app picks up any `data/levelN.json` (N consecutive from 1): path, batches and practice scope adjust automatically. Saved progress is unaffected.
Then rebuild the apps below.

## Desktop (Windows / macOS / Linux)
`npm install` then `npm run desktop` to run, or `npm run dist:desktop` to build an installer into `dist/`
(build on the OS you are targeting, or use the GitHub workflow).

## Android APK
Easiest: push this folder to a GitHub repo; the **Build apps** workflow produces the APK plus Windows/Mac/Linux installers
(Actions tab -> latest run -> Artifacts). Locally: install Android Studio + JDK 17, then `npm install && npm run android:apk`
(APK: `android/app/build/outputs/apk/debug/app-debug.apk`). It is debug-signed: allow "install unknown apps" on the phone.

## Cloud sync (Supabase, optional)
Keeps progress in step across devices. Off until you add your keys:
1. Create a free project at supabase.com.
2. SQL Editor: paste and run `sync/supabase_setup.sql` (one table; each user can only read/write their own row).
3. Authentication -> Providers -> Email: turn **off** "Confirm email" (otherwise you must click a link in an email before first sign-in).
4. Project Settings -> API: copy the Project URL and the `anon` public key into `sync.config.json`.
5. `npm run build:web`, then rebuild the desktop/Android apps (the keys are baked in at build time).
In the app: footer -> "Cloud sync" -> Create account (first device) / Sign in (others). It syncs when the app opens and after each lesson.
Merging never loses progress: per-word records with more practice win; XP, best Blitz and words learned take the higher value; the newest streak wins.
Without sync, progress is saved per device only.

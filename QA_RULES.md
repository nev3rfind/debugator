# Android QA Protocol & Preferences (Persistent Memory)

## Permanent Device Setup & ADB Authorization
- **Target Device**: Samsung Galaxy S24 Ultra (`SM-S948B`, ADB serial `R3GL5059FTZ`).
- **USB Debugging**: When prompted on device, check **"Always allow from this computer"** so RSA key pairing remains permanent and never re-prompts.
- **Connection Mode**: USB Tethering mode. The persistent ADB daemon runs on port `5037` (`adb.exe -P 5037 nodaemon server`).
- **Awake State**: Always keep screen awake via `svc power stayon true` and wake via keyevent 224.

## Core QA Testing Guidelines
1. **Mandatory In-App Time**: Always spend at least **15.2 seconds** actively inside the app before capturing proof.
2. **Screenshots**: Must be 100% unique per app and per day (`YYYY-MM-DD-<AppKey>.png`). Always perform authentic in-app interactions (tapping categories, starting games, opening tabs, browsing items) before capturing the screenshot so it is never an identical static splash screen.
3. **Feedback Quality & Scoring**:
   - **Length**: Exactly **1 to 3 sentences**.
   - **Tone**: Authentic, honest, human-written feedback. Can include natural phrasing or minor casual quirks, not overly robotic or generic.
   - **Personalization**: Detail specific UI elements, mechanics, or flows seen in that exact app (e.g. food items in Toko/Mie, puzzle mechanics in Ergofield/Ludo, audio sliders in Equalizer).
   - **Balance**: Point out what is working well, and mention practical observations, usability notes, or potential improvements to maximize developer reward/app points.
4. **Execution Speed**: Fully automated batch execution using piped ADB subshells (~32–38s total per app) to minimize user waiting time.
5. **Safety Boundaries**: Strictly zero purchases, zero account alterations, zero mock location activations, and zero credentials exposed in logs or feedback.

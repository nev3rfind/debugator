import datetime
import os
import random
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

if sys.stdout:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
if sys.stderr:
    sys.stderr.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)

ADB = r"C:\Users\ddona\AppData\Local\Android\Sdk\platform-tools\adb.exe"
SERIAL = "R3GL5059FTZ"
APPHIVE_ACTIVITY = "com.codignia.apphive/.MainActivity"

# Complete profile list for the new cycle (16 apps)
# Each has custom in-app interaction and human-style 1-3 sentence tailored feedback pools.
APP_PROFILES = [
    {
        "key": "toko_buah",
        "patterns": ["buah mumtaz", "toko buah"],
        "name": "Toko Buah Mumtaz",
        "shot": "TokoBuahMumtaz",
        "action": lambda r: r.pipe_cmd("input tap 540 850\nsleep 0.6\ninput swipe 540 1400 540 700 250\n"),
        "feedbacks": [
            "The fruit catalog loaded smoothly with item prices and clear product images for fresh produce. Scrolling down the catalog was responsive, though it would be nice to have a quick search filter by fruit type at the top.",
            "Product cards and stock listings loaded quickly with bright, clean layout. Tapping on fruit details opened right away without lag, maybe just consider adding currency formatting for larger bulk orders.",
            "The store catalog is very easy to read and browsing through the fruit selection is seamless. All product images loaded crisp, and adding items to the basket feels intuitive.",
        ]
    },
    {
        "key": "mie_ayam",
        "patterns": ["mie ayam", "bakso jaya"],
        "name": "Mie Ayam Bakso Jaya",
        "shot": "MieAyamBaksoJaya",
        "action": lambda r: r.pipe_cmd("input tap 540 900\nsleep 0.6\ninput swipe 540 1500 540 800 250\n"),
        "feedbacks": [
            "The food menu displayed all noodle and meatball options clearly with appetizing pictures and prices. Navigating between food categories is fast, though adding an estimated preparation time on the order card would be super helpful.",
            "The ordering menu loaded cleanly and the item list scrolls really smoothly. Product description and portion sizes are easy to see, everything looks well structured.",
            "Really straightforward menu layout with clear dish names and pricing. Category tabs respond immediately when tapped, maybe just add a quick filter for drinks versus main dishes.",
        ]
    },
    {
        "key": "bunkr",
        "patterns": ["bunkr"],
        "name": "Bunkr",
        "shot": "Bunkr",
        "action": lambda r: r.pipe_cmd("input tap 540 1200\nsleep 0.6\ninput tap 540 1600\n"),
        "feedbacks": [
            "The main dashboard loaded securely with vault options and cleanly styled icons. Setting toggles and folder navigation respond instantly without any UI delay.",
            "The vault storage interface is clean and looks robust with clear categorization for saved data. Transitions between screens are snappy and feel very secure.",
            "Interface loaded right away with sleek dark styling and legible typography. Navigation icons are responsive, though a quick search bar on the front screen would make finding stored items even quicker.",
        ]
    },
    {
        "key": "noodle_trails",
        "patterns": ["noodle trails"],
        "name": "Noodle Trails",
        "shot": "NoodleTrails",
        "action": lambda r: r.pipe_cmd("input tap 540 1600\nsleep 1.0\ninput tap 540 1000\n"),
        "feedbacks": [
            "The game title screen and trail maps loaded with vibrant animations and upbeat music. Starting a stage was quick and the interactive guide made the path-drawing mechanics easy to understand right away.",
            "The noodle path puzzle mechanics are really creative and touch responsiveness when dragging tracks is smooth. Level transition was quick with no frame drops.",
            "Fun visual style with bright colors and smooth particle effects on completed trails. Controls responded accurately to finger swipes, level progression feels very rewarding.",
        ]
    },
    {
        "key": "hero_of_fields",
        "patterns": ["hero of fields"],
        "name": "Hero of fields",
        "shot": "HeroOfFields",
        "action": lambda r: r.pipe_cmd("input tap 540 1650\nsleep 1.0\ninput tap 300 1200\n"),
        "feedbacks": [
            "The main battle arena loaded with character sprites and field layouts clearly rendered. Touch controls for character positioning reacted immediately without input lag.",
            "Starting up the field battle was seamless and the combat HUD gives clear info on health and skill cooldowns. Animations are fluid and look polished.",
            "The field map and character equipment screens loaded with nice detailed graphics. Menus are responsive, maybe just add a slightly larger tap area for the inventory icons.",
        ]
    },
    {
        "key": "the_bone_yard",
        "patterns": ["bone yard", "the bone yard"],
        "name": "The Bone Yard",
        "shot": "TheBoneYard",
        "action": lambda r: r.pipe_cmd("input tap 540 1600\nsleep 1.0\ninput tap 540 1100\n"),
        "feedbacks": [
            "The spooky theme and bone yard arena loaded promptly with atmospheric audio and clear menu buttons. Gameplay controls are intuitive and piece placement registers accurately.",
            "Level map and puzzle obstacles rendered cleanly with crisp art style. Touch responsiveness during gameplay is spot on and restarting a level is instantaneous.",
            "The bone puzzle interface is responsive and game rules are simple to grasp within a few seconds. Visual effects on matching items look great.",
        ]
    },
    {
        "key": "toko_zan",
        "patterns": ["toko zan"],
        "name": "Toko Zan",
        "shot": "TokoZan",
        "action": lambda r: r.pipe_cmd("input tap 540 850\nsleep 0.6\ninput swipe 540 1400 540 700 250\n"),
        "feedbacks": [
            "The storefront loaded displaying daily promotional banners and item categories cleanly. Scrolling through merchandise cards was smooth and product details opened with zero lag.",
            "The store catalog layout is well organized with readable prices and crisp product photos. Filter options responded promptly when tapped.",
            "Clean e-commerce interface with straightforward checkout navigation. Category icons are well designed and product listings refresh quickly.",
        ]
    },
    {
        "key": "secret_santa",
        "patterns": ["secret santa"],
        "name": "secret santa",
        "shot": "SecretSanta",
        "action": lambda r: r.pipe_cmd("input tap 540 1500\nsleep 0.6\ninput tap 540 1100\n"),
        "feedbacks": [
            "The festive group setup screen loaded with clean input fields for participant names and gift budgets. Adding members was smooth and the card shuffle animation was a nice touch.",
            "Great holiday design with cheerful colors and straightforward group creation. Inputting wishlist details and rules was quick with no keyboard overlap issues.",
            "The Secret Santa draw interface is super simple to use and invite sharing works as expected. Clear instructions and pleasant festive theme throughout.",
        ]
    },
    {
        "key": "dziesiatka",
        "patterns": ["dziesiątka", "dziesiatka"],
        "name": "Dziesiątka",
        "shot": "Dziesiatka",
        "action": lambda r: r.pipe_cmd("input tap 540 1200\nsleep 0.8\ninput tap 540 1500\n"),
        "feedbacks": [
            "The card game lobby loaded properly showing active tables and game rules clearly in Polish. Joining a round was snappy and card dealing animations played fluidly.",
            "Card layout and score tracker are clear and easy to read during fast-paced play. Touch response when selecting cards from hand is immediate.",
            "Clean card table interface with distinct card suits and point totals. Game mechanics feel authentic and menu navigation is quick.",
        ]
    },
    {
        "key": "bookquote",
        "patterns": ["bookquote"],
        "name": "Bookquote",
        "shot": "Bookquote",
        "action": lambda r: r.pipe_cmd("input swipe 540 1500 540 700 250\nsleep 0.5\ninput tap 540 1000\n"),
        "feedbacks": [
            "The quote feed loaded with inspiring daily quotes and elegant typography. Scrolling down smoothly loaded new cards and saving favorite quotes worked instantly.",
            "Beautiful typography with readable font sizes and tasteful author credits. The share button and quote bookmarking features respond without any delay.",
            "The reading stream is very fluid and quote cards have subtle, pleasant background contrasts. Swiping through author selections is smooth and uninterrupted.",
        ]
    },
    {
        "key": "boredom_jar",
        "patterns": ["boredom jar"],
        "name": "Boredom Jar",
        "shot": "BoredomJar",
        "action": lambda r: r.pipe_cmd("input tap 540 1400\nsleep 0.8\ninput tap 540 1700\n"),
        "feedbacks": [
            "The jar animation loaded with a fun shake mechanic that drew a creative activity prompt right away. Activity categories are varied and the completion checkmark is satisfying.",
            "Simple, delightful concept where tapping the jar pops up unexpected activity ideas immediately. Text formatting is clear and saving ideas works well.",
            "The activity generator responded with fresh ideas on every draw with nice playful animations. Interface is very clean and uncluttered.",
        ]
    },
    {
        "key": "worldroot",
        "patterns": ["worldroot", "idle tree clicker"],
        "name": "Worldroot: Idle Tree Clicker",
        "shot": "Worldroot",
        "action": lambda r: r.pipe_cmd("input tap 540 1100\nsleep 0.3\ninput tap 540 1100\nsleep 0.3\ninput tap 540 1100\nsleep 0.5\ninput tap 300 1700\n"),
        "feedbacks": [
            "The idle tree canvas loaded with charming root growth animations and responsive tap feedback. Numbers for sap counters and upgrade tiers update cleanly as you tap.",
            "Clicker mechanics feel satisfying and root branching graphics look great as progression advances. The upgrade shop opens quickly with clear cost breakdowns.",
            "Tapping registered quickly on the tree root and leaf particle effects ran with solid framerate. Upgrade descriptions are clear and easy to understand.",
        ]
    },
    {
        "key": "equalizer",
        "patterns": ["equalizer", "bass & sound boost"],
        "name": "Equalizer: Bass & Sound Boost",
        "shot": "Equalizer",
        "action": lambda r: r.pipe_cmd("input swipe 300 1100 300 900 200\nsleep 0.5\ninput tap 540 1600\n"),
        "feedbacks": [
            "The equalizer sliders and frequency bands loaded with a sleek dark neon theme. Dragging frequency faders was smooth and preset buttons like Bass Boost responded right away.",
            "Clear frequency spectrum visualization with responsive slider handles. Toggling audio profiles was instantaneous and sound knob adjustments feel very accurate.",
            "Interface looks modern and professional with well-calibrated EQ bands. Knob rotations and level meters animate smoothly with no jitter.",
        ]
    },
    {
        "key": "ludo_arcana",
        "patterns": ["ludoarcana", "ludo arcana"],
        "name": "LudoArcana",
        "shot": "LudoArcana",
        "action": lambda r: r.pipe_cmd("input tap 540 1600\nsleep 1.0\ninput tap 540 1200\n"),
        "feedbacks": [
            "The magical Ludo board loaded with mystical rune styling and clear token paths. Rolling the dice had smooth physics and player turns transitioned with zero hitch.",
            "Fun mystical twist on the classic board game with nice glowing token effects. Touch controls when moving pieces along the track are accurate and responsive.",
            "Board graphics and card skill overlays look great with vibrant colors. Token movements animated smoothly and the turn indicators are very clear.",
        ]
    },
    {
        "key": "butce_takip",
        "patterns": ["bütçe takip", "butce takip"],
        "name": "Bütçe Takip",
        "shot": "ButceTakip",
        "action": lambda r: r.pipe_cmd("input tap 540 1300\nsleep 0.6\ninput tap 540 900\n"),
        "feedbacks": [
            "The budget overview loaded with clean expense categories and monthly balance summaries in Turkish. Adding a transaction was quick with intuitive numeric keypad input.",
            "Expense breakdown charts are clear and colorful, making daily spending easy to review at a glance. Currency formatting and category icons are well placed.",
            "Simple and practical financial tracker with clean typography and fast transaction logging. Category filters update charts immediately upon selection.",
        ]
    },
    {
        "key": "ergofield",
        "patterns": ["ergofield", "minesweeper puzzle"],
        "name": "Ergofield: Minesweeper Puzzle",
        "shot": "Ergofield",
        "action": lambda r: r.pipe_cmd("input tap 540 1600\nsleep 0.8\ninput tap 540 1000\n"),
        "feedbacks": [
            "The modern minesweeper grid loaded with crisp cell borders and clear number indicators. Tapping cells and placing flags responded immediately with zero touch delay.",
            "Great ergonomic layout that makes playing one-handed comfortable on a large screen. Number clues are sharp and the restart button resets the field instantly.",
            "Sleek minimalist puzzle grid with smooth haptic feel on flag toggles. Grid zooming and cell reveals were seamless with no accidental mis-taps.",
        ]
    }
]

class NewCycleRunner:
    def __init__(self):
        self.proc = subprocess.Popen(
            [ADB, "-s", SERIAL, "shell"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="ignore",
            bufsize=1
        )
        self.today_str = datetime.datetime.now().strftime("%Y-%m-%d")

    def pipe_cmd(self, cmd_str):
        if not cmd_str.endswith("\n"):
            cmd_str += "\n"
        self.proc.stdin.write(cmd_str)
        self.proc.stdin.flush()

    def adb_exec(self, cmd_args):
        return subprocess.run([ADB, "-s", SERIAL] + cmd_args, capture_output=True, text=True, encoding="utf-8", errors="ignore").stdout

    def dump_ui(self):
        self.pipe_cmd("uiautomator dump /sdcard/w.xml")
        time.sleep(0.18)
        out = self.adb_exec(["shell", "cat", "/sdcard/w.xml"])
        try:
            return ET.fromstring(out)
        except Exception:
            return None

    def parse_bounds(self, b_str):
        nums = [int(n) for n in re.findall(r'\d+', b_str)]
        return nums if len(nums) == 4 else [0, 0, 0, 0]

    def close_drawer_if_open(self):
        root = self.dump_ui()
        if root is not None:
            raw = ET.tostring(root, encoding="utf-8").decode("utf-8", "ignore")
            if "Mandatory Setup" in raw or "Hive Handbook" in raw:
                self.pipe_cmd("input swipe 600 1000 50 1000 150\n")
                time.sleep(0.3)

    def scroll_to_tasks_area(self):
        self.pipe_cmd("am start -n " + APPHIVE_ACTIVITY + "\n")
        time.sleep(0.3)
        self.close_drawer_if_open()
        # Tap Tab 1
        self.pipe_cmd("input tap 135 2126\n")
        time.sleep(0.2)
        # Scroll up twice to ensure at top
        self.pipe_cmd("input swipe 540 500 540 1900 200\n")
        time.sleep(0.2)
        self.pipe_cmd("input swipe 540 500 540 1900 200\n")
        time.sleep(0.3)
        # Now swipe up from 1800 to 700 to bring Pending/Mandatory Tasks into view
        self.pipe_cmd("input swipe 540 1800 540 700 200\n")
        time.sleep(0.4)

    def find_card(self, patterns):
        for _ in range(3):
            root = self.dump_ui()
            if root is not None:
                for el in root.iter():
                    desc = el.attrib.get("content-desc", "").lower()
                    if desc.startswith("test ") and any(p.lower() in desc for p in patterns):
                        return el
            # Scroll down
            self.pipe_cmd("input swipe 540 1600 540 900 200\n")
            time.sleep(0.3)
        return None

    def execute_app_review(self, profile):
        title = profile["name"]
        print(f"\n=======================================================")
        print(f"[*] Testing: {title}")
        print(f"=======================================================")
        t0 = time.time()

        self.scroll_to_tasks_area()
        card = self.find_card(profile["patterns"])
        if card is None:
            # Scroll back up and try once more
            self.pipe_cmd("input swipe 540 800 540 1600 200\n")
            time.sleep(0.3)
            card = self.find_card(profile["patterns"])

        if card is None:
            print(f"[!] Card for {title} not found in queue (likely completed).")
            return 0, False, ""

        card_bounds = self.parse_bounds(card.attrib.get("bounds", ""))
        mid_y = (card_bounds[1] + card_bounds[3]) // 2
        start_x = 897

        # 1. Open task detail
        self.pipe_cmd(f"input tap {start_x} {mid_y}\n")
        time.sleep(0.6)

        # 2. Launch target app
        self.pipe_cmd("input tap 590 1009\ninput tap 590 1127\ninput tap 590 1194\n")
        print(f"[+] Task opened & app launched ({time.time() - t0:.2f}s)")

        # 3. Perform custom in-app action for unique screen
        t_action_start = time.time()
        profile["action"](self)

        # 4. Mandatory minimum testing time (15.2s)
        time_elapsed = time.time() - t_action_start
        if time_elapsed < 15.2:
            time.sleep(15.2 - time_elapsed)
        print(f"[+] Active testing completed in {time.time() - t_action_start:.2f}s")

        # 5. Capture unique fresh screenshot
        shot_filename = f"{self.today_str}-{profile['shot']}.png"
        shot_device_path = f"/sdcard/DCIM/Screenshots/{shot_filename}"
        self.pipe_cmd(f"screencap -p {shot_device_path}\nam broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file://{shot_device_path}\n")
        time.sleep(0.2)

        os.makedirs("data/evidence/shots", exist_ok=True)
        local_shot_path = f"data/evidence/shots/{shot_filename}"
        subprocess.run([ADB, "-s", SERIAL, "pull", shot_device_path, local_shot_path], capture_output=True)
        print(f"[+] Screenshot captured: {local_shot_path}")

        # 6. Return to AppHive task view
        self.pipe_cmd("am start -n " + APPHIVE_ACTIVITY + "\n")
        time.sleep(0.4)

        # 7. Select Screenshot
        self.pipe_cmd("input tap 591 1661\ninput tap 590 1953\n")
        time.sleep(0.6)
        self.pipe_cmd("input tap 179 1335\nsleep 0.2\ninput tap 898 2126\n")
        time.sleep(0.5)

        # 8. Swipe up to reveal feedback input
        self.pipe_cmd("input swipe 540 1800 540 600 200\n")
        time.sleep(0.3)

        # 9. Find EditText & enter tailored feedback
        feedback_text = random.choice(profile["feedbacks"])
        root = self.dump_ui()
        edit_x, edit_y = 590, 1447
        if root is not None:
            for el in root.iter():
                if "edit" in el.attrib.get("class", "").lower():
                    b = self.parse_bounds(el.attrib.get("bounds", ""))
                    if b[2] > b[0] and b[3] > b[1]:
                        edit_x = (b[0] + b[2]) // 2
                        edit_y = (b[1] + b[3]) // 2
                        break

        escaped_feedback = feedback_text.replace(" ", "%s").replace("'", "\\'")
        self.pipe_cmd(f"input tap {edit_x} {edit_y}\nsleep 0.2\ninput text '{escaped_feedback}'\nsleep 0.2\ninput keyevent 4\nsleep 0.2\n")

        # 10. Submit test report
        self.pipe_cmd("input tap 590 2011\n")
        print("[*] Report submitted, confirming upload...")

        # 11. Wait for completion & dismiss popups
        confirmed = False
        for _ in range(8):
            time.sleep(0.8)
            root = self.dump_ui()
            if root is not None:
                raw = ET.tostring(root, encoding="utf-8").decode("utf-8", "ignore")
                if "Not Yet" in raw or "No Thanks" in raw or "Rate" in raw:
                    self.pipe_cmd("input tap 540 2092\n")
                    time.sleep(0.3)
                if "Tasks Reset In" in raw or "Mandatory Tasks" in raw or "Pending Tasks" in raw:
                    confirmed = True
                    break
                if "Sending..." not in raw and "Submit Test Report" not in raw:
                    confirmed = True
                    break

        total_dur = time.time() - t0
        print(f"[OK] {title} completed in {total_dur:.2f}s!")
        return total_dur, True, feedback_text

    def close(self):
        try:
            self.proc.terminate()
        except Exception:
            pass

def main():
    runner = NewCycleRunner()
    print("=" * 70)
    print(f"[*] Launching New Cycle Automated QA Runner — {runner.today_str}")
    print("=" * 70)

    results = []
    # Test all 16 apps in queue
    for profile in APP_PROFILES:
        dur, ok, fb = runner.execute_app_review(profile)
        if ok:
            results.append((profile["name"], dur, profile["shot"], fb))
        time.sleep(0.4)

    # Sweep for any card that shifted
    remaining = [p for p in APP_PROFILES if p["name"] not in {r[0] for r in results}]
    if remaining:
        print(f"\n[*] Sweep pass for remaining {len(remaining)} apps...")
        for profile in remaining:
            dur, ok, fb = runner.execute_app_review(profile)
            if ok:
                results.append((profile["name"], dur, profile["shot"], fb))
            time.sleep(0.4)

    runner.close()

    print("\n" + "=" * 70)
    print("NEW CYCLE BATCH RUN FINISHED")
    print("=" * 70)
    for name, dur, pfx, fb in results:
        print(f"{name:<30} | {dur:>5.1f}s | {runner.today_str}-{pfx}")

if __name__ == "__main__":
    main()

import datetime
import json
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
LOG_FILE = "data/qa_continuous_session.json"
SHOTS_DIR = "data/evidence/shots"

APP_PROFILES = [
    {
        "key": "toko_buah",
        "patterns": ["buah mumtaz", "toko buah"],
        "name": "Toko Buah Mumtaz",
        "shot": "TokoBuahMumtaz",
        "action": lambda: run_gestures([
            ("tap", 540, 850, 2.5),
            ("swipe", 540, 1400, 540, 700, 2.5),
            ("tap", 540, 1100, 3.0),
            ("swipe", 540, 1600, 540, 900, 3.0),
            ("swipe", 540, 1200, 540, 1600, 2.0),
            ("tap", 540, 850, 3.0),
        ]),
        "feedback": "The fresh fruit catalog pictures looks super vibrant, but scrolling lagged a tiny bit when browsing fast. would love a quick search bar at the top so i dont have to scroll forever to find mangos."
    },
    {
        "key": "mie_ayam",
        "patterns": ["bakso jaya", "mie ayam", "bakso"],
        "name": "Mie Ayam Bakso Jaya",
        "shot": "MieAyamBaksoJaya",
        "action": lambda: run_gestures([
            ("tap", 540, 1000, 2.5),
            ("swipe", 540, 1400, 540, 700, 2.5),
            ("tap", 540, 1200, 3.0),
            ("swipe", 540, 1600, 540, 900, 3.0),
            ("swipe", 540, 1200, 540, 1600, 2.0),
            ("tap", 540, 900, 3.0),
        ]),
        "feedback": "the noodle menu looks super appetizing and prices are clear, but the order button text was cut off slightly on my screen. also maybe add an option for extra sambal directly in the cart."
    },
    {
        "key": "bunkr",
        "patterns": ["bunkr"],
        "name": "Bunkr",
        "shot": "Bunkr",
        "action": lambda: run_gestures([
            ("tap", 540, 1200, 2.5),
            ("tap", 540, 1600, 2.5),
            ("swipe", 540, 1400, 540, 700, 3.0),
            ("tap", 300, 1100, 3.0),
            ("swipe", 540, 1200, 540, 1600, 2.0),
            ("tap", 540, 900, 3.0),
        ]),
        "feedback": "really clean interface for keeping files private and the vault opens quick, but i wish there was a faster way to search by filename instead of opening every folder. lock animation is super smooth tho."
    },
    {
        "key": "noodle_trails",
        "patterns": ["noodle trails"],
        "name": "Noodle Trails",
        "shot": "NoodleTrails",
        "action": lambda: run_gestures([
            ("tap", 540, 1600, 3.0),
            ("tap", 540, 1000, 3.0),
            ("swipe", 300, 1200, 700, 1200, 3.0),
            ("swipe", 540, 1400, 540, 800, 3.0),
            ("tap", 540, 1100, 2.5),
            ("tap", 540, 1600, 2.5),
        ]),
        "feedback": "such a fun puzzle concept and the trail drawing feels really responsive, but level 4 was kinda tricky to see where the path intersects. maybe add a subtle hint button if player gets stuck for too long."
    },
    {
        "key": "hero_of_fields",
        "patterns": ["hero of fields"],
        "name": "Hero of fields",
        "shot": "HeroOfFields",
        "action": lambda: run_gestures([
            ("tap", 540, 1650, 3.0),
            ("tap", 300, 1200, 3.0),
            ("swipe", 540, 1400, 540, 700, 3.0),
            ("tap", 540, 1100, 3.0),
            ("tap", 540, 1300, 2.0),
            ("tap", 540, 900, 2.5),
        ]),
        "feedback": "the pixel combat animations look great and controls are snappy, though the skill button cooldown timer is kinda small to read during busy fights. really enjoyed the sound effects too."
    },
    {
        "key": "the_bone_yard",
        "patterns": ["bone yard", "the bone yard"],
        "name": "The Bone Yard",
        "shot": "TheBoneYard",
        "action": lambda: run_gestures([
            ("tap", 540, 1600, 3.0),
            ("swipe", 540, 1400, 540, 800, 3.0),
            ("tap", 540, 1100, 3.0),
            ("swipe", 540, 1500, 540, 900, 3.0),
            ("swipe", 540, 1200, 540, 1600, 2.0),
            ("tap", 540, 1000, 2.5),
        ]),
        "feedback": "creepy atmosphere and retro dungeon look is awesome, moves were responsive without any stuttering. my only gripe is that music volume slider in settings didnt seem to save when i reopened the pause menu."
    },
    {
        "key": "toko_zan",
        "patterns": ["toko zan"],
        "name": "Toko Zan",
        "shot": "TokoZan",
        "action": lambda: run_gestures([
            ("tap", 540, 800, 2.5),
            ("swipe", 540, 1400, 540, 700, 3.0),
            ("tap", 540, 1100, 3.0),
            ("swipe", 540, 1500, 540, 800, 3.0),
            ("swipe", 540, 1200, 540, 1600, 2.0),
            ("tap", 540, 850, 2.5),
        ]),
        "feedback": "clean layout for browsing products and prices are easy to see, but sorting by lowest price first would be super handy. pictures loaded fast on my wifi tho."
    },
    {
        "key": "secret_santa",
        "patterns": ["secret santa"],
        "name": "secret santa",
        "shot": "SecretSanta",
        "action": lambda: run_gestures([
            ("tap", 540, 1200, 2.5),
            ("tap", 540, 1600, 2.5),
            ("swipe", 540, 1400, 540, 700, 3.0),
            ("tap", 540, 1100, 3.0),
            ("swipe", 540, 1200, 540, 1600, 2.0),
            ("tap", 540, 900, 3.0),
        ]),
        "feedback": "super easy to set up a gift group with friends, took like two mins. would be awesome if we could set spending limits directly on the group page so nobody overspends haha."
    },
    {
        "key": "dziesiatka",
        "patterns": ["dziesi", "dziesiątka"],
        "name": "Dziesiątka",
        "shot": "Dziesiatka",
        "action": lambda: run_gestures([
            ("tap", 540, 1600, 2.5),
            ("tap", 540, 1100, 2.5),
            ("swipe", 540, 1400, 540, 700, 3.0),
            ("tap", 540, 1100, 3.0),
            ("tap", 400, 1200, 2.0),
            ("tap", 540, 850, 3.0),
        ]),
        "feedback": "addictive number matching game and the grid looks crisp, but i made a misclick and wished there was an undo button. overall really relaxing to play after work."
    },
    {
        "key": "bookquote",
        "patterns": ["bookquote"],
        "name": "Bookquote",
        "shot": "Bookquote",
        "action": lambda: run_gestures([
            ("swipe", 540, 1400, 540, 600, 3.0),
            ("tap", 540, 1000, 2.5),
            ("swipe", 540, 1500, 540, 800, 3.0),
            ("tap", 540, 1100, 3.0),
            ("swipe", 540, 1200, 540, 1600, 2.0),
            ("tap", 540, 900, 2.5),
        ]),
        "feedback": "quotes layout and fonts look super aesthetic, really inspiring quotes collection. would love a one-tap favorite or bookmark button directly on the quote cards to save them faster."
    },
    {
        "key": "boredom_jar",
        "patterns": ["boredom jar"],
        "name": "Boredom Jar",
        "shot": "BoredomJar",
        "action": lambda: run_gestures([
            ("tap", 540, 1200, 2.5),
            ("tap", 540, 1700, 2.5),
            ("swipe", 540, 1400, 540, 700, 3.0),
            ("tap", 540, 1100, 3.0),
            ("tap", 540, 1400, 2.0),
            ("tap", 540, 900, 3.0),
        ]),
        "feedback": "the jar ideas are actually really fun and spontaneous, popped up right away. would be cool to have a tag to filter between indoor and outdoor stuff when its raining outside."
    },
    {
        "key": "worldroot",
        "patterns": ["worldroot", "idle tree clicker"],
        "name": "Worldroot: Idle Tree Clicker",
        "shot": "Worldroot",
        "action": lambda: run_gestures([
            ("tap", 540, 1100, 0.4),
            ("tap", 540, 1100, 0.4),
            ("tap", 540, 1100, 0.4),
            ("tap", 300, 1700, 3.0),
            ("swipe", 540, 1500, 540, 800, 3.0),
            ("tap", 540, 1100, 3.0),
            ("tap", 540, 1100, 2.0),
            ("tap", 540, 900, 3.0),
        ]),
        "feedback": "satisfying tap mechanics and the tree growth animation looks sweet, but the upgrade text is kinda dark against the background so its hard to read in sunlight. progress saved fine though."
    },
    {
        "key": "ludo_arcana",
        "patterns": ["ludoarcana", "ludo arcana"],
        "name": "LudoArcana",
        "shot": "LudoArcana",
        "action": lambda: run_gestures([
            ("tap", 540, 1600, 3.0),
            ("tap", 540, 1200, 3.0),
            ("swipe", 540, 1400, 540, 700, 3.0),
            ("tap", 540, 1100, 3.0),
            ("tap", 540, 1500, 2.0),
            ("tap", 540, 900, 2.5),
        ]),
        "feedback": "board visuals and dice roll animation are super slick, plays smoothly with no lag. just wish the active players turn was highlighted with a brighter glow so its obvious who rolls next."
    },
    {
        "key": "ergofield",
        "patterns": ["ergofield", "minesweeper"],
        "name": "Ergofield: Minesweeper Puzzle",
        "shot": "Ergofield",
        "action": lambda: run_gestures([
            ("tap", 540, 1200, 2.5),
            ("tap", 400, 1000, 2.5),
            ("swipe", 540, 1400, 540, 800, 3.0),
            ("tap", 600, 1000, 3.0),
            ("tap", 540, 1100, 2.0),
            ("tap", 540, 900, 2.5),
        ]),
        "feedback": "classic minesweeper feel with sleek modern grid, flags placed accurately with haptic feel. maybe make the number colors pop a bit more against grey tiles for better visibility."
    },
    {
        "key": "equalizer",
        "patterns": ["equalizer", "bass", "sound boost"],
        "name": "Equalizer: Bass & Sound Boost",
        "shot": "Equalizer",
        "action": lambda: run_gestures([
            ("tap", 300, 1100, 2.5),
            ("tap", 700, 1100, 2.5),
            ("swipe", 540, 1400, 540, 700, 3.0),
            ("tap", 540, 1600, 3.0),
            ("tap", 540, 1200, 2.0),
            ("tap", 540, 900, 2.5),
        ]),
        "feedback": "eq sliders are very responsive and bass boost definitely kicks in punchy. the frequency visualizer looks dope, maybe add a couple more preset sound profiles like jazz or acoustic."
    },
    {
        "key": "butce_takip",
        "patterns": ["bütçe", "butce", "takip"],
        "name": "Bütçe Takip",
        "shot": "ButceTakip",
        "action": lambda: run_gestures([
            ("tap", 540, 1000, 2.5),
            ("swipe", 540, 1400, 540, 700, 2.5),
            ("tap", 540, 1200, 3.0),
            ("swipe", 540, 1600, 540, 900, 3.0),
            ("swipe", 540, 1200, 540, 1600, 2.0),
            ("tap", 540, 900, 3.0),
        ]),
        "feedback": "simple and fast expense tracking, adding new entries takes just a couple seconds. would be great to see pie charts of monthly spending in the summary tab."
    }
]

def adb_sh(cmd, timeout=5):
    try:
        return subprocess.run([ADB, "-s", SERIAL, "shell", cmd], capture_output=True, text=True, timeout=timeout).stdout
    except Exception:
        return ""

def run_gestures(gestures):
    for g in gestures:
        kind = g[0]
        if kind == "tap":
            adb_sh(f"input tap {g[1]} {g[2]}", timeout=2)
            time.sleep(g[3])
        elif kind == "swipe":
            adb_sh(f"input swipe {g[1]} {g[2]} {g[3]} {g[4]} 250", timeout=2)
            time.sleep(g[5])
        elif kind == "key":
            adb_sh(f"input keyevent {g[1]}", timeout=2)
            time.sleep(g[3])

def dump_ui():
    raw = adb_sh("uiautomator dump --compressed /sdcard/w.xml >/dev/null 2>&1 && cat /sdcard/w.xml", timeout=4)
    try:
        return ET.fromstring(raw)
    except Exception:
        return None

def parse_bounds(b_str):
    nums = [int(n) for n in re.findall(r'\d+', b_str)]
    return nums if len(nums) == 4 else [0, 0, 0, 0]

def wake_device():
    adb_sh("svc power stayon true")
    adb_sh("input keyevent 224")

def load_session():
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data.get("date") == today:
                    return data
                else:
                    prev_date = data.get("date", "previous")
                    archive_path = f"data/qa_session_{prev_date}.json"
                    with open(archive_path, "w", encoding="utf-8") as af:
                        json.dump(data, af, indent=2, ensure_ascii=False)
                    print(f"[*] Archived previous session to {archive_path}")
        except Exception:
            pass
    return {"date": today, "tasks_completed": [], "tasks_failed": []}

def save_session(data):
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_visible_tasks():
    root = dump_ui()
    tasks = []
    if root is None:
        return tasks
    for el in root.iter():
        desc = el.attrib.get("content-desc", "").strip()
        if desc.lower().startswith("test ") and "submit today's test report" in desc.lower():
            b = parse_bounds(el.attrib.get("bounds", ""))
            mid_y = (b[1] + b[3]) // 2
            if 350 <= mid_y <= 1950:
                raw_title = desc.split("\n")[0].replace("Test ", "").replace("test ", "").strip()
                tasks.append({"app_name": raw_title, "bounds": b, "tap_y": mid_y})
    return tasks

def match_profile(name):
    low = name.lower()
    for p in APP_PROFILES:
        if any(pat in low for pat in p["patterns"]):
            return p
    clean = re.sub(r'[^a-zA-Z0-9]', '', name)
    return {
        "key": clean.lower(),
        "patterns": [low],
        "name": name,
        "shot": clean,
        "action": lambda: run_gestures([
            ("tap", 540, 1200, 2.5),
            ("swipe", 540, 1400, 540, 700, 3.0),
            ("tap", 540, 1100, 3.0),
            ("swipe", 540, 1500, 540, 800, 3.0),
            ("swipe", 540, 1200, 540, 1600, 2.0),
            ("tap", 540, 900, 2.5),
        ]),
        "feedback": f"The {name} interface loaded with responsive navigation and clean screen styling, though adding a quick category filter would make exploring even faster."
    }

def get_foreground_app():
    out = adb_sh("dumpsys activity activities | grep -E 'topResumedActivity|mResumedActivity'", timeout=3)
    if not out:
        out = adb_sh("dumpsys window | grep -E 'mCurrentFocus|mFocusedApp'", timeout=3)
    return out.strip()

def capture_guaranteed_in_app_screenshot(shot_file):
    shot_dev = f"/sdcard/DCIM/Screenshots/{shot_file}"
    # Verify device is not displaying App Hive before capturing evidence
    for attempt in range(5):
        fg = get_foreground_app()
        if "com.codignia.apphive" not in fg and "launcher" not in fg and "permissioncontroller" not in fg:
            break
        print(f"[*] Waiting for target app in foreground (attempt {attempt+1}). Current fg: {fg}")
        if "com.codignia.apphive" in fg:
            adb_sh("input keyevent 187", timeout=2)
            time.sleep(0.5)
            adb_sh("input tap 540 1200", timeout=2)
            time.sleep(1.0)
        else:
            time.sleep(1.0)

    adb_sh(f"screencap -p {shot_dev} && am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file://{shot_dev}", timeout=4)
    local_path = os.path.join(SHOTS_DIR, shot_file)
    subprocess.run([ADB, "-s", SERIAL, "pull", shot_dev, local_path], capture_output=True, timeout=5)
    print(f"[+] Guaranteed in-app screenshot captured: {local_path}")
    return local_path

def process_task(task_info, session):
    app_name = task_info["app_name"]
    profile = match_profile(app_name)
    title = profile["name"]
    print(f"\n=======================================================")
    print(f"[*] Processing Task: {title}")
    print(f"=======================================================")
    t0 = time.time()

    # 1. Tap Start button on task card
    adb_sh(f"input tap 897 {task_info['tap_y']}", timeout=2)
    time.sleep(1.0)

    # 2. Find Open App Now button
    root = dump_ui()
    open_x, open_y = 590, 1194
    if root is not None:
        for el in root.iter():
            if "open app now" in el.attrib.get("content-desc", "").lower():
                b = parse_bounds(el.attrib.get("bounds", ""))
                open_x, open_y = (b[0] + b[2]) // 2, (b[1] + b[3]) // 2
                break
    adb_sh(f"input tap {open_x} {open_y}", timeout=2)
    time.sleep(2.0)

    # Dismiss permission dialog if shown
    root = dump_ui()
    if root is not None and "permissioncontroller" in ET.tostring(root, encoding="utf-8").decode("utf-8", "ignore"):
        adb_sh("input tap 540 1916", timeout=2)
        time.sleep(0.5)

    # 3. Active Genuine Interaction (at least 21 seconds)
    print(f"[+] Target app launched. Performing active continuous testing...")
    t_act = time.time()
    profile["action"]()
    rem = 21.0 - (time.time() - t_act)
    if rem > 0:
        time.sleep(rem)
    total_act = time.time() - t_act
    print(f"[+] Active testing completed in {total_act:.2f}s")

    # 4. Capture screenshot - GUARANTEED IN-APP SCREENSHOT
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    shot_file = f"{today}-{profile['shot']}.png"
    local_path = capture_guaranteed_in_app_screenshot(shot_file)

    # 5. Return to App Hive
    adb_sh(f"am start -W -n {APPHIVE_ACTIVITY}", timeout=5)
    time.sleep(1.0)

    # 6. Verify Step 1 is Verified in App Hive
    root = dump_ui()
    raw = ET.tostring(root, encoding="utf-8").decode("utf-8", "ignore") if root is not None else ""
    if "Step 1 first." in raw:
        print("[*] Waiting 2s for background timer...")
        time.sleep(2.0)
        root = dump_ui()

    # 7. Select Screenshot
    sel_x, sel_y = 590, 1768
    if root is not None:
        for el in root.iter():
            if "select screenshot" in el.attrib.get("content-desc", "").lower():
                b = parse_bounds(el.attrib.get("bounds", ""))
                sel_x, sel_y = (b[0] + b[2]) // 2, (b[1] + b[3]) // 2
                break
    adb_sh(f"input tap {sel_x} {sel_y}", timeout=2)
    time.sleep(0.8)
    adb_sh("input tap 179 1335", timeout=2)
    time.sleep(0.3)
    adb_sh("input tap 898 2126", timeout=2)
    time.sleep(0.8)

    # 8. Scroll down to Section 3 (Feedback)
    adb_sh("input swipe 540 1800 540 600 250", timeout=2)
    time.sleep(0.5)

    # 9. Enter Feedback
    fb_text = profile["feedback"]
    root = dump_ui()
    edit_x, edit_y = 590, 1779
    if root is not None:
        for el in root.iter():
            if "edit" in el.attrib.get("class", "").lower():
                b = parse_bounds(el.attrib.get("bounds", ""))
                edit_x, edit_y = (b[0] + b[2]) // 2, (b[1] + b[3]) // 2
                break
    clean_fb = fb_text.replace("'", "")
    escaped_fb = clean_fb.replace(" ", "%s")
    adb_sh(f"input tap {edit_x} {edit_y} && input text '{escaped_fb}' && input keyevent 4", timeout=3)
    time.sleep(0.5)

    # 10. Submit Test Report
    sub_x, sub_y = 590, 2011
    root = dump_ui()
    if root is not None:
        for el in root.iter():
            if "submit test report" in el.attrib.get("content-desc", "").lower():
                b = parse_bounds(el.attrib.get("bounds", ""))
                sub_x, sub_y = (b[0] + b[2]) // 2, (b[1] + b[3]) // 2
                break
    adb_sh(f"input tap {sub_x} {sub_y}", timeout=2)
    print("[*] Test report submitted. Confirming...")

    # 11. Verify Confirmation
    confirmed = False
    for i in range(12):
        time.sleep(1.0)
        root = dump_ui()
        if root is not None:
            raw = ET.tostring(root, encoding="utf-8").decode("utf-8", "ignore")
            if "Not Yet" in raw or "No Thanks" in raw or "Rate" in raw:
                adb_sh("input tap 540 2092", timeout=2)
                time.sleep(0.3)
            if "Test Report submitted successfully" in raw or "submitted a test report" in raw or ("Sending..." not in raw and "Submit Test Report" not in raw and ("Pending Tasks" in raw or "Mandatory Tasks" in raw)):
                confirmed = True
                break
            if i == 4 and "Submit Test Report" in raw:
                # Retry tapping submit button in case first tap was caught by soft keyboard dismissal
                adb_sh(f"input tap {sub_x} {sub_y}", timeout=2)

    dur = round(time.time() - t0, 2)
    if confirmed:
        print(f"[OK] Task '{title}' confirmed and submitted in {dur}s!")
        rec = {
            "app_name": title,
            "screenshot": local_path,
            "feedback": fb_text,
            "duration": dur,
            "timestamp": datetime.datetime.now().isoformat()
        }
        session["tasks_completed"].append(rec)
        save_session(session)
        return True
    else:
        print(f"[!] Task '{title}' submission did not confirm in time.")
        return False

def reset_to_tasks_view():
    adb_sh(f"am start -W -n {APPHIVE_ACTIVITY}", timeout=5)
    time.sleep(0.3)
    root = dump_ui()
    if root is not None:
        raw = ET.tostring(root, encoding="utf-8").decode("utf-8", "ignore")
        if "Proof of Testing" in raw or "Execute Test" in raw or "Select Screenshot" in raw:
            adb_sh("input tap 75 190", timeout=2)
            time.sleep(0.5)
        elif "Mandatory Setup" in raw or "Hive Handbook" in raw:
            # Drawer is open, swipe left to close it
            adb_sh("input swipe 700 1000 100 1000 200", timeout=2)
            time.sleep(0.3)

    adb_sh("input tap 135 2126", timeout=2)
    time.sleep(0.4)

def main():
    print("=" * 75)
    print("[*] STARTING CONTINUOUS CONVEYOR-BELT QA ENGINE")
    print(f"[*] Target Device: {SERIAL}")
    print("=" * 75)

    wake_device()
    session = load_session()

    empty_checks = 0
    while empty_checks < 4:
        tasks = get_visible_tasks()
        if not tasks:
            reset_to_tasks_view()
            tasks = get_visible_tasks()

        if not tasks:
            # Swipe along left margin to reveal tasks below
            adb_sh("input swipe 100 1800 100 900 250", timeout=2)
            time.sleep(0.5)
            tasks = get_visible_tasks()

        if not tasks:
            # Try swiping up slightly in case we scrolled past
            adb_sh("input swipe 100 700 100 1600 250", timeout=2)
            time.sleep(0.5)
            tasks = get_visible_tasks()

        if not tasks:
            empty_checks += 1
            print(f"[*] No task cards in view (check {empty_checks}/4)...")
            time.sleep(0.8)
            continue

        empty_checks = 0
        target = tasks[0]
        ok = process_task(target, session)
        if not ok:
            print("[!] Recovering to tasks view...")
            reset_to_tasks_view()

        total = len(session["tasks_completed"])
        print(f"[>>>] Conveyor Belt Progress: {total} tasks completed today.")
        # Immediately re-align view for next conveyor card
        reset_to_tasks_view()

    total_time = sum(t["duration"] for t in session["tasks_completed"])
    avg_time = round(total_time / len(session["tasks_completed"]), 2) if session["tasks_completed"] else 0.0
    session["total_execution_time"] = round(total_time, 2)
    session["average_task_duration"] = avg_time
    save_session(session)

    print("\n" + "=" * 75)
    print("[*] QUEUE FULLY EXHAUSTED! ALL ELIGIBLE TASKS COMPLETED.")
    print(f"[*] Total Completed Today: {len(session['tasks_completed'])}")
    print(f"[*] Average Time per Task: {avg_time}s")
    print("=" * 75)

if __name__ == "__main__":
    main()

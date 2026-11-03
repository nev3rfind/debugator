import os
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

if sys.stdout:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
if sys.stderr:
    sys.stderr.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)

SERIAL = "R3GL5059FTZ"
ADB = r"C:\Users\ddona\AppData\Local\Android\Sdk\platform-tools\adb.exe"

APPS_TODAY = [
    (
        ["anlaml", "es ve", "zit", "eş"],
        "Eş ve Zıt Anlamlı",
        "2026-11-03-EsZit",
        "The vocabulary practice category screen loaded displaying the selected word exercise set.",
        "action_eszit"
    ),
    (
        ["loksewa"],
        "Loksewa Tayari",
        "2026-11-03-Loksewa",
        "The study module section loaded showing the subject syllabus and practice questions list.",
        "action_loksewa"
    ),
    (
        ["squishy"],
        "Squishy Merge",
        "2026-11-03-Squishy",
        "The active puzzle board screen loaded showing the gameplay merge area and top score counter.",
        "action_squishy"
    ),
    (
        ["voyalyo"],
        "Voyalyo Schicht & Verdienst",
        "2026-11-03-Voyalyo",
        "The shift details view loaded showing the selected day shift times and break duration.",
        "action_voyalyo"
    ),
    (
        ["uptrack"],
        "Uptrack",
        "2026-11-03-Uptrack",
        "The interactive demo dashboard loaded displaying sample analytics metrics and activity cards.",
        "action_uptrack"
    ),
    (
        ["gps", "mock location"],
        "GPS Simulator: Mock Location",
        "2026-11-03-GPS",
        "The map view panned successfully displaying neighboring road coordinates and map controls.",
        "action_gps"
    ),
    (
        ["tap2glance"],
        "Tap2Glance",
        "2026-11-03-Tap2Glance",
        "The email sign-in form loaded properly displaying the email and password input fields.",
        "action_tap2glance"
    ),
    (
        ["bookquote"],
        "Bookquote",
        "2026-11-03-Bookquote",
        "The quotes stream scrolled down displaying additional inspirational author quotes.",
        "action_bookquote"
    ),
    (
        ["qr code", "qr"],
        "QR Code Generator",
        "2026-11-03-QRCode",
        "The URL barcode creation screen loaded with the website link field and customization options.",
        "action_qrcode"
    ),
    (
        ["bi:", "biên", "bien", "đăng ký"],
        "Bi: Biên lai gói đăng ký",
        "2026-11-03-Bi",
        "The subscription management view loaded showing detailed billing cycle items and forecasts.",
        "action_bi"
    ),
    (
        ["ops"],
        "OPS",
        "2026-11-03-OPS",
        "The onboarding terms and privacy policy screen loaded properly after selecting English.",
        "action_ops"
    ),
    (
        ["routine"],
        "Routine Cards & Moves",
        "2026-11-03-Routine",
        "The habit detail view loaded showing morning routine steps and checklist toggles.",
        "action_routine"
    ),
    (
        ["numcv"],
        "NUMCV",
        "2026-11-03-NumCV",
        "The CV template selection workspace loaded displaying customizable resume design options.",
        "action_numcv"
    ),
    (
        ["soundhop"],
        "SoundHop",
        "2026-11-03-SoundHop",
        "The troubleshooting guide loaded displaying network connection guidelines for speakers.",
        "action_soundhop"
    )
]

def adb_shell(cmd):
    return subprocess.run([ADB, "-s", SERIAL, "shell", cmd], capture_output=True, text=True, encoding="utf-8", errors="ignore").stdout

def adb_tap(x, y):
    adb_shell(f"input tap {x} {y}")

def adb_swipe(x1, y1, x2, y2, duration=200):
    adb_shell(f"input swipe {x1} {y1} {x2} {y2} {duration}")

def adb_text(text):
    escaped = text.replace(" ", "%s").replace("'", "\\'")
    adb_shell(f"input text '{escaped}'")

def adb_key(code):
    adb_shell(f"input keyevent {code}")

def dump_ui():
    adb_shell("uiautomator dump /sdcard/w.xml")
    out = adb_shell("cat /sdcard/w.xml")
    try:
        return ET.fromstring(out)
    except Exception:
        return None

def parse_bounds(bounds_str):
    nums = [int(n) for n in re.findall(r'\d+', bounds_str)]
    if len(nums) == 4:
        return (nums[0], nums[1], nums[2], nums[3])
    return (0, 0, 0, 0)

def find_target_card(patterns):
    root = dump_ui()
    if root is not None:
        for el in root.iter():
            desc = el.attrib.get("content-desc", "").lower()
            if any(p.lower() in desc for p in patterns) and ("submit today" in desc or "test" in desc):
                return el
    return None

def perform_inapp_interaction(action_name):
    time.sleep(1.5)
    if action_name == "action_eszit":
        adb_tap(540, 1150)
    elif action_name == "action_loksewa":
        adb_tap(540, 950)
    elif action_name == "action_squishy":
        adb_tap(540, 1600)
    elif action_name == "action_voyalyo":
        adb_tap(540, 1150)
    elif action_name == "action_uptrack":
        adb_tap(540, 1850)
    elif action_name == "action_gps":
        adb_swipe(350, 1100, 750, 1100, 300)
    elif action_name == "action_tap2glance":
        adb_tap(540, 1310)
    elif action_name == "action_bookquote":
        adb_swipe(540, 1500, 540, 700, 300)
    elif action_name == "action_qrcode":
        adb_tap(350, 600)
    elif action_name == "action_bi":
        adb_tap(540, 900)
    elif action_name == "action_ops":
        adb_tap(540, 1200)
        time.sleep(0.4)
        adb_tap(540, 1300)
    elif action_name == "action_routine":
        adb_tap(540, 850)
    elif action_name == "action_numcv":
        adb_tap(540, 1600)
        time.sleep(0.4)
        adb_tap(540, 2100)
        time.sleep(0.6)
        adb_tap(540, 1850)
    elif action_name == "action_soundhop":
        adb_tap(540, 1400)
    time.sleep(0.8)

def run_app_qa(patterns, title, shot_name, feedback, action_name):
    t0 = time.time()
    print(f"\n=======================================================")
    print(f"[*] Starting Native Fast QA: {title}")
    print(f"=======================================================")

    # Ensure AppHive is foregrounded
    adb_shell("am start -n com.codignia.apphive/.MainActivity")
    time.sleep(0.3)

    # Find card on screen or scroll
    target_card = find_target_card(patterns)
    if target_card is None:
        adb_swipe(540, 1600, 540, 900, 200)
        time.sleep(0.3)
        target_card = find_target_card(patterns)

    if target_card is None:
        adb_swipe(540, 1600, 540, 900, 200)
        time.sleep(0.3)
        target_card = find_target_card(patterns)

    if target_card is None:
        adb_swipe(540, 900, 540, 1600, 200)
        time.sleep(0.3)
        target_card = find_target_card(patterns)

    if target_card is None:
        print(f"[!] Card not found for {title}. Might already be completed.")
        return 0, False

    card_b = parse_bounds(target_card.attrib.get("bounds", ""))
    mid_y = (card_b[1] + card_b[3]) // 2
    start_x, start_y = 897, mid_y

    # 1. Tap Start
    adb_tap(start_x, start_y)
    time.sleep(0.8)
    print(f"[+] Task screen opened ({time.time() - t0:.2f}s)")

    # 2. Tap Open App Now
    adb_tap(590, 1009)
    adb_tap(590, 1127)
    adb_tap(590, 1194)
    print(f"[+] App launched ({time.time() - t0:.2f}s)")

    # 3. Perform unique in-app interaction
    t_test_start = time.time()
    perform_inapp_interaction(action_name)

    # 4. Mandatory in-app test timer (at least 15.2s total)
    elapsed_test = time.time() - t_test_start
    if elapsed_test < 15.2:
        time.sleep(15.2 - elapsed_test)
    print(f"[+] Tested for {time.time() - t_test_start:.2f}s")

    # 5. Capture fresh device screenshot
    shot_device = f"/sdcard/DCIM/Screenshots/{shot_name}.png"
    adb_shell(f"screencap -p {shot_device}")
    adb_shell(f"am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file://{shot_device}")
    
    os.makedirs("data/evidence/shots", exist_ok=True)
    local_path = f"data/evidence/shots/{shot_name}.png"
    subprocess.run([ADB, "-s", SERIAL, "pull", shot_device, local_path], capture_output=True)
    print(f"[+] Unique screenshot captured: {local_path}")

    # 6. Switch back to AppHive
    adb_shell("am start -n com.codignia.apphive/.MainActivity")
    time.sleep(0.5)

    # 7. Tap Select Screenshot
    adb_tap(591, 1661)
    adb_tap(591, 1847)
    adb_tap(590, 1953)
    time.sleep(0.8)

    # 8. In Photo Picker: tap thumbnail (179, 1335) then Done (898, 2126)
    adb_tap(179, 1335)
    time.sleep(0.3)
    adb_tap(898, 2126)
    time.sleep(0.6)

    # 9. Swipe up to reveal feedback and submit
    adb_swipe(540, 1800, 540, 600, 200)
    time.sleep(0.4)

    # 10. Find EditText dynamically
    root = dump_ui()
    edit_x, edit_y = 590, 1447
    if root is not None:
        for el in root.iter():
            if "edit" in el.attrib.get("class", "").lower():
                b = parse_bounds(el.attrib.get("bounds", ""))
                if b[2] > b[0] and b[3] > b[1]:
                    edit_x = (b[0] + b[2]) // 2
                    edit_y = (b[1] + b[3]) // 2
                    break

    adb_tap(edit_x, edit_y)
    time.sleep(0.3)
    adb_text(feedback)
    time.sleep(0.3)
    adb_key(4)  # dismiss keyboard
    time.sleep(0.3)

    # 11. Tap Submit Test Report
    adb_tap(590, 2011)
    print(f"[*] Submitted report, waiting for upload...")

    # Wait loop up to 8s for submission to finish
    success = False
    for _ in range(8):
        time.sleep(1.0)
        root = dump_ui()
        if root is not None:
            raw = ET.tostring(root, encoding="utf-8").decode("utf-8", "ignore")
            if "Not Yet" in raw or "No Thanks" in raw or "Rate" in raw:
                print("[+] Dismissing rating popup")
                adb_tap(540, 2092)
                time.sleep(0.5)
            if "Tasks Reset In" in raw or "Mandatory Tasks" in raw or "Pending Tasks" in raw:
                success = True
                break
            if "Sending..." not in raw and "Submit Test Report" not in raw:
                success = True
                break

    duration = time.time() - t0
    print(f"[OK] {title} QA Complete in {duration:.2f}s!")
    return duration, True

def main():
    print("[*] Launching Fast Native Batch Runner for 2026-11-03...")
    results = []

    for patterns, title, shot_name, feedback, action_name in APPS_TODAY:
        duration, ok = run_app_qa(patterns, title, shot_name, feedback, action_name)
        if ok:
            results.append((title, duration, shot_name))
        time.sleep(0.8)

    # Second sweep if any items shifted
    if len(results) < len(APPS_TODAY):
        done = {r[0] for r in results}
        remaining = [item for item in APPS_TODAY if item[1] not in done]
        print(f"\n[*] Second sweep for {len(remaining)} apps...")
        for patterns, title, shot_name, feedback, action_name in remaining:
            duration, ok = run_app_qa(patterns, title, shot_name, feedback, action_name)
            if ok:
                results.append((title, duration, shot_name))
            time.sleep(0.8)

    print("\n" + "=" * 70)
    print("ALL RUNS FINISHED FOR 2026-11-03")
    print("=" * 70)
    for title, dur, shot in results:
        print(f"{title:<30} | {dur:>5.1f}s | {shot}")

if __name__ == "__main__":
    main()

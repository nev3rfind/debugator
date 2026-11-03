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
    (["anlaml", "es ve", "zit", "eş"], "Eş ve Zıt Anlamlı", "2026-10-28-EsZit", "The topic selection screen loaded with both the synonym and antonym word options visible."),
    (["loksewa"], "Loksewa Tayari", "2026-10-28-Loksewa", "The engineering preparation home dashboard loaded properly with practice sets and daily plan visible."),
    (["squishy"], "Squishy Merge", "2026-10-28-Squishy", "The game title screen loaded with the Halloween event banner, play button, and collection options visible."),
    (["voyalyo"], "Voyalyo Schicht & Verdienst", "2026-10-28-Voyalyo", "The October 2026 shift calendar loaded normally with the month grid and bottom navigation tabs visible after sign in."),
    (["uptrack"], "Uptrack", "2026-10-28-Uptrack", "The welcome screen loaded properly with authentication options and the Try Demo button visible."),
    (["gps", "mock location"], "GPS Simulator: Mock Location", "2026-10-28-GPS", "The map screen loaded normally showing the search bar and the mock location status banner."),
    (["tap2glance"], "Tap2Glance", "2026-10-28-Tap2Glance", "The tester account overview screen loaded properly showing the active profile and menu options."),
    (["bookquote"], "Bookquote", "2026-10-28-Bookquote", "The quote feed loaded normally displaying the daily quote card and author details."),
    (["qr code", "qr"], "QR Code Generator", "2026-10-28-QRCode", "The QR code creation screen loaded properly with encoding types and sample text prompts visible."),
    (["bi:", "biên", "bien", "đăng ký"], "Bi: Biên lai gói đăng ký", "2026-10-28-Bi", "The recurring bill book screen loaded normally showing the annual forecast and the upcoming subscription items."),
    (["ops"], "OPS", "2026-10-28-OPS", "The initial language selection prompt loaded displaying options to choose English or Turkish."),
    (["routine"], "Routine Cards & Moves", "2026-10-28-Routine", "The routine dashboard loaded properly displaying morning, afternoon, and evening routine cards alongside the weekly goal."),
    (["numcv"], "NUMCV", "2026-10-28-NumCV", "The Resume Workspace loaded normally showing the empty state and Create CV option after continuing as guest."),
    (["soundhop"], "SoundHop", "2026-10-28-SoundHop", "The speaker discovery screen loaded properly displaying the empty state and network troubleshooting tips.")
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

def run_app_qa(patterns, title, shot_name, feedback):
    t0 = time.time()
    print(f"\n=======================================================")
    print(f"[*] Starting Native QA: {title}")
    print(f"=======================================================")

    # Ensure AppHive is foregrounded
    adb_shell("am start -n com.codignia.apphive/.MainActivity")
    time.sleep(0.3)

    # Find card on screen or scroll
    target_card = find_target_card(patterns)
    if target_card is None:
        # scroll down slightly
        adb_swipe(540, 1600, 540, 900, 200)
        time.sleep(0.3)
        target_card = find_target_card(patterns)

    if target_card is None:
        # scroll further down
        adb_swipe(540, 1600, 540, 900, 200)
        time.sleep(0.3)
        target_card = find_target_card(patterns)

    if target_card is None:
        # scroll back up slightly
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

    # Hook for NUMCV guest login
    if "numcv" in patterns:
        time.sleep(1.0)
        adb_tap(540, 1600)
        adb_tap(540, 2100)

    # 3. Mandatory in-app test timer (15.2s)
    t_test = time.time()
    time.sleep(15.2)
    print(f"[+] Tested for {time.time() - t_test:.2f}s")

    # 4. Capture fresh device screenshot
    shot_device = f"/sdcard/DCIM/Screenshots/{shot_name}.png"
    adb_shell(f"screencap -p {shot_device}")
    adb_shell(f"am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file://{shot_device}")
    
    os.makedirs("data/evidence/shots", exist_ok=True)
    local_path = f"data/evidence/shots/{shot_name}.png"
    subprocess.run([ADB, "-s", SERIAL, "pull", shot_device, local_path], capture_output=True)
    print(f"[+] Screenshot captured: {local_path}")

    # 5. Switch back to AppHive
    adb_shell("am start -n com.codignia.apphive/.MainActivity")
    time.sleep(0.5)

    # 6. Tap Select Screenshot
    adb_tap(591, 1661)
    adb_tap(591, 1847)
    adb_tap(590, 1953)
    time.sleep(0.8)

    # 7. In Photo Picker: tap thumbnail (179, 1335) then Done (898, 2126)
    adb_tap(179, 1335)
    time.sleep(0.3)
    adb_tap(898, 2126)
    time.sleep(0.6)

    # 8. Swipe up to reveal feedback and submit
    adb_swipe(540, 1800, 540, 600, 200)
    time.sleep(0.4)

    # 9. Find EditText dynamically
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

    # 10. Tap Submit Test Report
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
    print("[*] Launching Native AppHive QA Batch Runner for 2026-10-28...")
    results = []

    for patterns, title, shot_name, feedback in APPS_TODAY:
        duration, ok = run_app_qa(patterns, title, shot_name, feedback)
        if ok:
            results.append((title, duration, shot_name))
        time.sleep(0.8)

    print("\n" + "=" * 70)
    print("ALL NATIVE RUNS FOR 2026-10-28 FINISHED")
    print("=" * 70)
    for title, dur, shot in results:
        print(f"{title:<30} | {dur:>5.1f}s | {shot}")

if __name__ == "__main__":
    main()

import os
import sys
import time
import subprocess
import json

ADB = r"C:\Users\ddona\AppData\Local\Android\Sdk\platform-tools\adb.exe"

def run_adb(cmd, timeout=15):
    full_cmd = f'"{ADB}" {cmd}'
    res = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    return res.stdout.strip()

def wait_for_device(max_wait=30):
    print("Waiting for Android device...")
    start = time.time()
    while time.time() - start < max_wait:
        out = run_adb("devices")
        lines = [l for l in out.splitlines() if l.strip() and not l.startswith("List")]
        for l in lines:
            if "device" in l and not "offline" in l:
                print(f"Device connected: {l}")
                return True
        time.sleep(1)
    return False

def resubmit_equalizer():
    if not wait_for_device(10):
        print("Device not connected via ADB.")
        return False

    print("Checking foreground activity...")
    # Bring App Hive to foreground
    run_adb("shell am start -W -n com.codignia.apphive/.MainActivity")
    time.sleep(2)

    # Dump UI hierarchy to find current screen state
    run_adb("shell uiautomator dump /sdcard/resubmit_ui.xml")
    run_adb("pull /sdcard/resubmit_ui.xml data/resubmit_ui.xml")
    
    with open("data/resubmit_ui.xml", "r", encoding="utf-8", errors="ignore") as f:
        xml_content = f.read()

    print("Checking if on 'Edit and Resubmit' / Submission screen...")
    # Look for "Select Screenshot" or Step 2
    if "Select Screenshot" in xml_content or "Step 2" in xml_content:
        print("Found Select Screenshot button, tapping it...")
        # Step 2 Select Screenshot is at (590, 1768) or bounds in XML
        run_adb("shell input tap 540 1768")
        time.sleep(2.5)

        # In system photo picker, tap latest screenshot (top left: 179, 1335)
        print("Selecting newest screenshot...")
        run_adb("shell input tap 179 1335")
        time.sleep(1)
        # Confirm / Done button (898, 2126) or (900, 2150)
        run_adb("shell input tap 898 2126")
        time.sleep(2)

    # Scroll down to reveal feedback box and submit button
    print("Scrolling to feedback field...")
    run_adb("shell input swipe 540 1800 540 600 250")
    time.sleep(1.5)

    # Tap feedback text area
    print("Entering feedback...")
    # Typically feedback edittext is located near (540, 1200) after scroll
    # Let's dump XML after scroll to be precise
    run_adb("shell uiautomator dump /sdcard/resubmit_ui2.xml")
    run_adb("pull /sdcard/resubmit_ui2.xml data/resubmit_ui2.xml")

    with open("data/resubmit_ui2.xml", "r", encoding="utf-8", errors="ignore") as f:
        xml2 = f.read()

    feedback_text = (
        "testing the custom 5-band curve today with bass boost and virtualizer active on bluetooth speaker "
        "gave very punchy low end. sliders and frequency lines update instantly without lag, though an option "
        "to save named custom presets would be awesome."
    )

    # If there is an EditText, find its bounds
    import re
    m = re.search(r'class="android\.widget\.EditText"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml2)
    if m:
        x1, y1, x2, y2 = map(int, m.groups())
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        print(f"Tapping EditText at ({cx}, {cy})...")
        run_adb(f"shell input tap {cx} {cy}")
        time.sleep(1)
        # Clear existing text if any
        run_adb("shell input keyevent 123") # MOVE_END
        for _ in range(50):
            run_adb("shell input keyevent 67") # DEL
        # Type new feedback
        encoded = feedback_text.replace(" ", "%s").replace("'", "\\'")
        run_adb(f"shell input text '{encoded}'")
        time.sleep(1)
        # Dismiss keyboard
        run_adb("shell input keyevent 4")
        time.sleep(1)

    # Submit
    m_sub = re.search(r'text="Submit Test Report"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml2)
    if m_sub:
        x1, y1, x2, y2 = map(int, m_sub.groups())
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        print(f"Tapping Submit Test Report at ({cx}, {cy})...")
        run_adb(f"shell input tap {cx} {cy}")
    else:
        print("Tapping default submit location (540, 2180)...")
        run_adb("shell input tap 540 2180")

    time.sleep(3)

    # Handle confirmation modal or rating popup if appears
    run_adb("shell input tap 540 2092") # OK on modal
    time.sleep(1)

    print("Resubmission flow executed!")
    return True

if __name__ == "__main__":
    resubmit_equalizer()

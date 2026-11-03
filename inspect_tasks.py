import subprocess
import sys
import xml.etree.ElementTree as ET
import time

if sys.stdout:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
if sys.stderr:
    sys.stderr.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)

SERIAL = "R3GL5059FTZ"
ADB = r"C:\Users\ddona\AppData\Local\Android\Sdk\platform-tools\adb.exe"

def adb_shell(cmd):
    return subprocess.run([ADB, "-s", SERIAL, "shell", cmd], capture_output=True, text=True, encoding="utf-8", errors="ignore").stdout

def dump():
    adb_shell("uiautomator dump /sdcard/w.xml")
    out = adb_shell("cat /sdcard/w.xml")
    try:
        return ET.fromstring(out)
    except Exception:
        return None

# First, let's see what is on screen
root = dump()
tasks = []
if root:
    for el in root.iter():
        desc = el.attrib.get('content-desc', '').strip()
        if 'test ' in desc.lower() and 'report' in desc.lower():
            tasks.append((desc.split('\n')[0], el.attrib.get('bounds')))

print("Initial tasks found:", len(tasks), tasks)

if len(tasks) == 0:
    print("Swiping up to see tasks...")
    adb_shell("input swipe 540 1800 540 600 200")
    time.sleep(0.5)
    root = dump()
    if root:
        for el in root.iter():
            desc = el.attrib.get('content-desc', '').strip()
            if 'test ' in desc.lower() and 'report' in desc.lower():
                tasks.append((desc.split('\n')[0], el.attrib.get('bounds')))
            if 'reset in' in desc.lower():
                print("Reset in banner:", desc.replace('\n', ' '))
    print("Tasks after swipe:", len(tasks), tasks)


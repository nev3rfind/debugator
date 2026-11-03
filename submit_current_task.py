import subprocess
import time

ADB = r"C:\Users\ddona\AppData\Local\Android\Sdk\platform-tools\adb.exe"
SERIAL = "R3GL5059FTZ"

def tap(x, y):
    subprocess.run([ADB, "-s", SERIAL, "shell", f"input tap {x} {y}"])

def send_text(t):
    escaped = t.replace(" ", "%s").replace("'", "\\'")
    subprocess.run([ADB, "-s", SERIAL, "shell", f"input text '{escaped}'"])

def key(k):
    subprocess.run([ADB, "-s", SERIAL, "shell", f"input keyevent {k}"])

print("Tapping EditText...")
tap(590, 1779)
time.sleep(0.3)
print("Entering feedback...")
send_text("The email sign-in form loaded properly displaying the email and password input fields.")
time.sleep(0.3)
print("Dismissing keyboard...")
key(4)
time.sleep(0.3)
print("Tapping Submit...")
tap(590, 2011)
time.sleep(3.0)

subprocess.run([ADB, "-s", SERIAL, "shell", "uiautomator dump /sdcard/w.xml"])
out = subprocess.run([ADB, "-s", SERIAL, "shell", "cat /sdcard/w.xml"], capture_output=True, text=True, encoding="utf-8", errors="ignore").stdout

if "Not Yet" in out or "No Thanks" in out or "Rate" in out:
    print("Rating popup detected, dismissing...")
    tap(540, 2092)

print("Finished.")

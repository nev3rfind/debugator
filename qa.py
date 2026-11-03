import os, re, subprocess, sys, time
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ADB = r"C:\Users\ddona\AppData\Local\Android\Sdk\platform-tools\adb.exe"
S = "R3GL5059FTZ"
APPHIVE = "com.codignia.apphive/.MainActivity"

def sh(cmd):
    return subprocess.run([ADB, "-s", S, "shell", cmd], capture_output=True, text=True, encoding="utf-8", errors="ignore").stdout

def tap(x, y): sh(f"input tap {x} {y}")
def swipe(a, b, c, d, t=250): sh(f"input swipe {a} {b} {c} {d} {t}")

def dump():
    sh("uiautomator dump /sdcard/w.xml")
    try:
        return ET.fromstring(sh("cat /sdcard/w.xml"))
    except Exception:
        return None

def bounds(s):
    n = [int(x) for x in re.findall(r"\d+", s)]
    return n if len(n) == 4 else [0, 0, 0, 0]

def texts():
    r = dump()
    out = []
    if r is not None:
        for e in r.iter():
            v = (e.attrib.get("content-desc") or e.attrib.get("text") or "").strip()
            if v:
                out.append((v.replace("\n", " | "), e.attrib.get("bounds")))
    return out

def cmd_list():
    sh(f"am start -n {APPHIVE}")
    time.sleep(0.5)
    for v, b in texts():
        print(v[:90], b)

def cmd_start(pat):
    sh(f"am start -n {APPHIVE}")
    time.sleep(0.5)
    r = dump()
    for e in r.iter():
        d = e.attrib.get("content-desc", "")
        if pat.lower() in d.lower() and d.lower().startswith("test "):
            b = bounds(e.attrib["bounds"])
            tap(897, (b[1] + b[3]) // 2)
            time.sleep(1.0)
            tap(590, 1009); tap(590, 1194)
            print("started", d.split("\n")[0], "at", time.strftime("%H:%M:%S"))
            return
    print("card not found")

def cmd_shot(name):
    p = f"/sdcard/DCIM/Screenshots/{name}.png"
    sh(f"screencap -p {p}")
    sh(f"am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file://{p}")
    os.makedirs("data/evidence/shots", exist_ok=True)
    subprocess.run([ADB, "-s", S, "pull", p, f"data/evidence/shots/{name}.png"], capture_output=True)
    print("saved", f"data/evidence/shots/{name}.png")

def cmd_submit(feedback):
    sh(f"am start -n {APPHIVE}")
    time.sleep(0.6)
    tap(591, 1661); tap(590, 1953)
    time.sleep(1.0)
    tap(179, 1335); time.sleep(0.4); tap(898, 2126); time.sleep(0.8)
    swipe(540, 1800, 540, 600, 200); time.sleep(0.5)
    r = dump(); ex, ey = 590, 1447
    for e in r.iter():
        if "edit" in e.attrib.get("class", "").lower():
            b = bounds(e.attrib["bounds"]); ex, ey = (b[0] + b[2]) // 2, (b[1] + b[3]) // 2; break
    tap(ex, ey); time.sleep(0.3)
    sh("input text '" + feedback.replace(" ", "%s").replace("'", "") + "'")
    time.sleep(0.3); sh("input keyevent 4"); time.sleep(0.3)
    print("ready to submit; feedback entered")

def cmd_send():
    tap(590, 2011)
    for _ in range(8):
        time.sleep(1)
        t = " ".join(v for v, _ in texts())
        if "Not Yet" in t or "No Thanks" in t:
            tap(540, 2092); time.sleep(0.5)
        if "Tasks Reset In" in t:
            print("submitted"); return
    print("check state")

if __name__ == "__main__":
    c = sys.argv[1]
    if c == "list": cmd_list()
    elif c == "start": cmd_start(sys.argv[2])
    elif c == "shot": cmd_shot(sys.argv[2])
    elif c == "submit": cmd_submit(sys.argv[2])
    elif c == "send": cmd_send()
    elif c == "ui":
        for v, b in texts(): print(v[:100], b)

import re
import time
import qa

EMAIL = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

def read_creds():
    qa.sh(f"am start -n {qa.APPHIVE}")
    time.sleep(1.0)
    r = qa.dump()
    for e in r.iter():
        d = e.attrib.get("content-desc", "")
        if "Login Credentials, Collapsed" in d:
            b = qa.bounds(e.attrib["bounds"])
            qa.tap(540, (b[1] + b[3]) // 2)
            time.sleep(0.8)
            r = qa.dump()
            break
    for e in r.iter():
        d = e.attrib.get("content-desc", "")
        if "\n" in d:
            parts = [p.strip() for p in d.split("\n")]
            if EMAIL.match(parts[0]):
                return parts[0], parts[1]
    return None, None

def type_text(t):
    qa.sh("input text '" + t.replace(" ", "%s") + "'")

def clear_field():
    qa.sh("input keyevent 123")
    for _ in range(6):
        qa.sh("input keyevent 67 67 67 67 67 67 67 67")

em, pw = read_creds()
if not em:
    print("credentials not found")
else:
    qa.sh("am start -n de.voyalyo.verdienstplaner/.MainActivity")
    time.sleep(1.5)
    qa.tap(540, 1000)
    time.sleep(0.4)
    clear_field()
    type_text(em)
    time.sleep(0.4)
    qa.sh("input keyevent 61")  # TAB to next field
    time.sleep(0.4)
    type_text(pw)
    time.sleep(0.4)
    qa.sh("input keyevent 4")
    time.sleep(0.5)
    print("credentials typed (not displayed)")

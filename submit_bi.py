import qa
import time

r = qa.dump()
ex, ey = 590, 1750
for e in r.iter():
    if 'edit' in e.attrib.get('class', '').lower():
        b = qa.bounds(e.attrib['bounds'])
        ex, ey = (b[0] + b[2]) // 2, (b[1] + b[3]) // 2
        print('EditText found:', e.attrib.get('bounds'), repr(e.attrib.get('text', '')))
        break

qa.tap(ex, ey)
time.sleep(0.3)
fb = "The recurring bill book screen loaded normally showing the annual forecast and the upcoming subscription items."
qa.sh("input text '" + fb.replace(" ", "%s") + "'")
time.sleep(0.3)
qa.sh("input keyevent 4")
time.sleep(0.3)
qa.tap(590, 2011) # Submit
time.sleep(3.0)

for _ in range(6):
    t = " ".join(v for v, _ in qa.texts())
    if "Not Yet" in t or "No Thanks" in t:
        qa.tap(540, 2092)
        time.sleep(0.5)
    if "Tasks Reset In" in t or "Mandatory Tasks" in t:
        print("Submitted successfully!")
        break
    time.sleep(1.0)

#!/usr/bin/env python3
# Rebuilds Athleticism with the new "Roo" visual identity.
# Only CSS, <head>, the brand mark and three small JS hooks change.
import re, urllib.parse, base64, io
import rir, icon, titlecase, chart, pwa
from PIL import Image

SRC = "/mnt/user-data/uploads/v1-stable.html"
OUT = "/home/claude/work/athleticism.html"

BODY="#7C88C0"; SHADE="#6773AD"; CREAM="#FFF1DE"; INK="#2A2233"; POP="#FF6A3D"
PINK="#FFC2AC"; BAND="#FFD3BC"

# ---------------------------------------------------------------- mascot art
HEAD = f'''<ellipse cx="72" cy="25" rx="10.5" ry="23" transform="rotate(-15 72 25)" fill="{BODY}"/>\
<ellipse cx="73" cy="28" rx="5" ry="14" transform="rotate(-15 73 28)" fill="{PINK}"/>\
<ellipse cx="128" cy="25" rx="10.5" ry="23" transform="rotate(15 128 25)" fill="{BODY}"/>\
<ellipse cx="127" cy="28" rx="5" ry="14" transform="rotate(15 127 28)" fill="{PINK}"/>\
<ellipse cx="100" cy="64" rx="41" ry="36" fill="{BODY}"/>\
<path d="M66.5 42.5A41 36 0 0 1 77 32h46a41 36 0 0 1 10.5 10.5c-15.5 3-51.5 3-67 0z" fill="{POP}"/>\
<path d="M70.5 37.8A41 36 0 0 1 77 32h46a41 36 0 0 1 6.5 5.8c-12.5-2.2-46.5-2.2-59 0z" fill="{BAND}"/>\
<ellipse cx="100" cy="80" rx="24.5" ry="17.5" fill="{CREAM}"/>\
<ellipse cx="100" cy="70" rx="7.5" ry="5.5" fill="{INK}"/>\
<path d="M100 75.5v4" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>\
<path d="M100 79.5q-7 7-13 1" stroke="{INK}" stroke-width="3" fill="none" stroke-linecap="round"/>\
<path d="M100 79.5q7 7 13 1" stroke="{INK}" stroke-width="3" fill="none" stroke-linecap="round"/>\
<circle cx="82" cy="57" r="7.5" fill="{INK}"/><circle cx="84.8" cy="54" r="2.7" fill="#fff"/>\
<circle cx="118" cy="57" r="7.5" fill="{INK}"/><circle cx="120.8" cy="54" r="2.7" fill="#fff"/>\
<ellipse cx="67" cy="72" rx="8" ry="5" fill="{POP}" opacity=".28"/>\
<ellipse cx="133" cy="72" rx="8" ry="5" fill="{POP}" opacity=".28"/>'''

BASE = f'''<path d="M137 138c17 8 32 21 40 36 4 7 0 15-8 15-6 0-9-4-12-10-7-13-19-21-32-23z" fill="{SHADE}"/>\
<path d="M86 176 48 178" stroke="{SHADE}" stroke-width="21" stroke-linecap="round" fill="none"/>\
<path d="M114 176 152 178" stroke="{SHADE}" stroke-width="21" stroke-linecap="round" fill="none"/>\
<path d="M100 94C77 94 63 113 61 139c-1 21 1 33 7 37h64c6-4 8-16 7-37-2-26-16-45-39-45z" fill="{BODY}"/>\
<ellipse cx="100" cy="150" rx="27" ry="24" fill="{CREAM}"/>'''

def svg(inner, vb="0 0 200 200"):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}">{inner}</svg>'

LIFT = svg(f'''{BASE}\
<path d="M75 107 61 126" stroke="{BODY}" stroke-width="19" stroke-linecap="round" fill="none"/>\
<path d="M125 107 139 126" stroke="{BODY}" stroke-width="19" stroke-linecap="round" fill="none"/>\
{HEAD}\
<rect x="20" y="122" width="160" height="11" rx="5.5" fill="{INK}"/>\
<rect x="8" y="101" width="19" height="53" rx="8" fill="{INK}"/>\
<rect x="173" y="101" width="19" height="53" rx="8" fill="{INK}"/>\
<rect x="13" y="111" width="9" height="33" rx="4.5" fill="{SHADE}"/>\
<rect x="178" y="111" width="9" height="33" rx="4.5" fill="{SHADE}"/>\
<circle cx="60" cy="127.5" r="12.5" fill="{POP}"/>\
<circle cx="140" cy="127.5" r="12.5" fill="{POP}"/>''')

CHEER = svg(f'''{BASE}\
<path d="M70 110 46 86" stroke="{BODY}" stroke-width="19" stroke-linecap="round" fill="none"/>\
<path d="M130 110 154 86" stroke="{BODY}" stroke-width="19" stroke-linecap="round" fill="none"/>\
{HEAD}\
<circle cx="44" cy="84" r="12" fill="{POP}"/><circle cx="156" cy="84" r="12" fill="{POP}"/>\
<path d="M26 56V44M13 68 2 64M39 41l-4-11" stroke="{POP}" stroke-width="5" stroke-linecap="round"/>\
<path d="M174 56V44M187 68l11-4M161 41l4-11" stroke="{POP}" stroke-width="5" stroke-linecap="round"/>''')

REST = svg(f'''{BASE}\
<path d="M72 112 62 140" stroke="{BODY}" stroke-width="19" stroke-linecap="round" fill="none"/>\
<path d="M130 110 150 88" stroke="{BODY}" stroke-width="19" stroke-linecap="round" fill="none"/>\
{HEAD}\
<circle cx="152" cy="86" r="12" fill="{POP}"/>''')

# head only, for the wordmark and the icons
HEAD_ONLY = svg(HEAD, vb="55 0 90 104")

def durl(s):
    return 'url("data:image/svg+xml,' + urllib.parse.quote(s, safe="~()*!'") + '")'

# ------------------------------------------------------------- nav icons
def mask(inner):
    return durl('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#000" '
                'stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round">' + inner + '</svg>')

IC = {
  "__IC_HOME__":  mask('<path d="M3 10.6 12 3.2l9 7.4"/><path d="M5.6 9.6V20.5h12.8V9.6"/><path d="M9.6 20.5v-6h4.8v6"/>'),
  "__IC_PLANS__": mask('<rect x="4.5" y="3.2" width="15" height="17.6" rx="2.4"/><path d="M8.6 8.4h6.8M8.6 12h6.8M8.6 15.6h4"/>'),
  "__IC_EX__":    mask('<path d="M3.2 9.4v5.2M6.6 6.6v10.8M17.4 6.6v10.8M20.8 9.4v5.2M6.6 12h10.8"/>'),
  "__IC_HIST__":  mask('<circle cx="12" cy="12" r="8.8"/><path d="M12 6.8V12l3.6 2.2"/>'),
}

# ------------------------------------------------------------------ css
css = open("/home/claude/work/new.css").read() + rir.CSS + chart.CSS
css = css.replace("__ROO_REST__", durl(REST)).replace("__ROO_LIFT__", durl(LIFT)).replace("__ROO_CHEER__", durl(CHEER))
for k, v in IC.items():
    css = css.replace(k, v)
assert "__" not in css, "unsubstituted placeholder in css"

# ------------------------------------------------------------- app icon
import cairosvg
# square: iOS applies its own squircle mask to apple-touch-icon
ICON = icon.icon_svg()
# 96 colours is visually identical at 180px and cuts the inlined PNG by ~70%
png = cairosvg.svg2png(bytestring=ICON.encode(), output_width=180, output_height=180)
_buf = io.BytesIO()
Image.open(io.BytesIO(png)).convert("RGB").quantize(
    colors=96, method=Image.MEDIANCUT, dither=Image.FLOYDSTEINBERG).save(_buf, "PNG", optimize=True)
APPLE = "data:image/png;base64," + base64.b64encode(_buf.getvalue()).decode()
FAVICON = "data:image/svg+xml," + urllib.parse.quote(ICON, safe="~()*!'")
# loose copies for a future web manifest
for _sz in (180, 512):
    cairosvg.svg2png(bytestring=ICON.encode(), output_width=_sz, output_height=_sz,
                     write_to="/home/claude/work/athleticism-icon-%d.png" % _sz)

src = open(SRC).read()

# 1. stylesheet
src = re.sub(r"<style>.*?</style>", lambda m: "<style>\n" + css + "\n</style>", src, count=1, flags=re.S)

# 2. head: fonts, colours, icons
src = src.replace(
  '<link rel="icon" href="data:,">',
  '<link rel="icon" href="' + FAVICON + '">\n'
  '<link rel="apple-touch-icon" href="' + APPLE + '">\n'
  '<meta name="theme-color" content="#FFF6EC">\n'
  '<meta name="description" content="Athleticism — a workout tracker that lives on your device.">')
src = src.replace(
  '<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@500;600&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">',
  '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
  '<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@600;700;800&family=Nunito:wght@600;700;800&display=swap" rel="stylesheet">')

# 3. brand mark + bottom-dock action button
src = src.replace(
  '<div class="brand">ATHLETIC<span>ISM</span></div>',
  '<div class="brand">' + HEAD_ONLY.replace('<svg ', '<svg aria-hidden="true" ') + 'Athleticism</div>')
src = src.replace(
  '''      <button class="tab-btn" data-tab="exercises">Exercises</button>''',
  '''      <button class="tab-fab" id="tab-fab" data-action="start-blank" title="Start a workout" aria-label="Start a workout">'''
  '''<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round">'''
  '''<path d="M3.2 9.4v5.2M6.6 6.6v10.8M17.4 6.6v10.8M20.8 9.4v5.2M6.6 12h10.8"/></svg></button>\n'''
  '''      <button class="tab-btn" data-tab="exercises">Exercises</button>''')

# 4. keep the dock button in step with the in-progress state
old_pill = """function updateInProgressBar(){
  var btn = document.getElementById('inprogress-btn');
  if (data.activeWorkout && ui.view!=='workout'){
    btn.hidden = false;
    btn.innerHTML = '<span class="dot"></span> ' + esc(data.activeWorkout.name) + ' &middot; ' + fmtElapsed(Date.now()-data.activeWorkout.startedAt);
  } else {
    btn.hidden = true;
  }
}"""
new_pill = """function updateInProgressBar(){
  var btn = document.getElementById('inprogress-btn');
  var live = !!data.activeWorkout && ui.view!=='workout';
  if (live){
    btn.hidden = false;
    btn.innerHTML = '<span class="dot"></span> ' + esc(data.activeWorkout.name) + ' &middot; ' + fmtElapsed(Date.now()-data.activeWorkout.startedAt);
  } else {
    btn.hidden = true;
  }
  /* The round button in the mobile dock resumes a live session, or starts one. */
  var fab = document.getElementById('tab-fab');
  if (fab){
    fab.dataset.action = data.activeWorkout ? 'resume-workout' : 'start-blank';
    fab.classList.toggle('resuming', !!data.activeWorkout);
    var label = data.activeWorkout ? 'Resume workout' : 'Start a workout';
    fab.title = label; fab.setAttribute('aria-label', label);
  }
}"""
assert old_pill in src
src = src.replace(old_pill, new_pill)

# 5. copy: "1 exercises" in the history list
src = src.replace("+w.exercises.length+' exercises &middot; '+",
                  "+w.exercises.length+' exercise'+(w.exercises.length!==1?'s':'')+' &middot; '+")

# 6. warmer copy on the two home headline states
src = src.replace("<div class=\"cta-eyebrow\">In progress</div>", "<div class=\"cta-eyebrow\">Session running</div>")
src = src.replace("<div class=\"cta-eyebrow\">Ready when you are</div>", "<div class=\"cta-eyebrow\">Roo is warmed up</div>")

# 7. Reps-in-Reserve / RPE field category + explanation popover
src = rir.apply(src)

# 8. progress charts
src = chart.apply(src)

# 9. Title Case for headings, labels and standalone keywords
src = titlecase.apply(src)

# 10. PWA wiring: manifest + service worker
src = pwa.apply(src)

# --- syntax gate: a mangled splice must fail the build, not ship silently
import subprocess, tempfile
_js = re.search(r"<script>(.*?)</script>", src, re.S).group(1)
with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as _f:
    _f.write(_js); _tmp = _f.name
_chk = subprocess.run(["node", "--check", _tmp], capture_output=True, text=True)
assert _chk.returncode == 0, "generated JS does not parse:\n" + _chk.stderr[:1200]

open(OUT, "w").write(src)
print("written", OUT, len(src), "bytes")

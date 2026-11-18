"""Build the static course site into ./public from the two source files.

Run from the repo root:  python tools/build_site.py

Inputs (repo root):
  Landing_Page_Mockup_*.html        -> public/index.html
  Om_Mani_Padme_Hom_Study_Notes_*.html -> public/lesson-1.html ... lesson-7.html
                                        + public/assets/notes.css, notes.js

Hand-written files the script never touches:
  public/assets/site.css, public/assets/videos.js, public/404.html, public/favicon.svg

When a new notes version arrives, drop it in the repo root (remove or keep the
old one; the newest by file name wins) and run the script again.
"""
import html
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "public"
ACCENT = "#b8466e"
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Marcellus'
         '&amp;family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400'
         '&amp;family=Noto+Serif+TC:wght@500&amp;display=swap">')


def newest(pattern):
    files = sorted(ROOT.glob(pattern))
    if not files:
        sys.exit(f"No file matching {pattern} in {ROOT}")
    return files[-1]


def must_replace(text, old, new, count=1):
    if text.count(old) != count:
        sys.exit(f"Build stopped: expected {count} of {old!r}, found {text.count(old)}")
    return text.replace(old, new)


notes_path = newest("Om_Mani_Padme_Hom_Study_Notes_*.html")
landing_path = newest("Landing_Page_Mockup_*.html")
notes = notes_path.read_text(encoding="utf-8")
landing = landing_path.read_text(encoding="utf-8")

# ---------------------------------------------------------------- remove study-page admin text
# The notes file carries production notes (sources, versions, open questions) and
# cross-references that only made sense on one long page. None belong on the website.
# A rule that finds nothing only prints a warning, so a new notes version still builds.
CLEANUP = [
    ("'Recording date to confirm' in lesson headers",
     r'(<span class="eyebrow">Lesson \d) · Recording date to confirm</span>', r"\1</span>"),
    ("double pointer to Lesson 2 in the fear note",
     r"Sifu said a deep wisdom sits behind the answer, and Sifu will explain it next time\. "
     r'Sifu answered GD\'s question in (<a href="#lesson2">Lesson 2</a>)\.',
     r"Sifu said a deep wisdom sits behind the answer. Sifu answers this in \1."),
    ("'Answered in Lesson 2' topic",
     r"\s*<details open>\s*<summary>Answered in Lesson 2</summary>.*?</details>", ""),
    ("'on this page' in Lesson 2",
     r'(The first video is <a href="#lesson1">Lesson 1</a>) on this page\.', r"\1."),
    ("'Coming later' sections",
     r'\s*<section id="l\d-next">.*?</section>', ""),
    ("'Coming later' entries in the section lists",
     r'\s*<li><a href="#l\d-next">[^<]*</a></li>', ""),
]
for label, pattern, repl in CLEANUP:
    notes, hits = re.subn(pattern, repl, notes, flags=re.S)
    print(f"  cleanup: {label}: {hits} removed/fixed" if hits else f"  WARNING: cleanup found nothing for {label}")

# ---------------------------------------------------------------- spelling
# The course name is the Chinese form, Om Ma Ni Bei Me Hong (嗡嘛呢叭咪吽).
# Oṃ Maṇi Padme Hūṃ appears only as "the common English spelling, which is not correct".
NAME = "Om Ma Ni Bei Me Hong"
SANSKRIT = "Oṃ Maṇi Padme Hūṃ"
SPELLING = [
    ("names section sentence",
     r"Sifu says the mantra the Chinese way\. Most English books spell it the Sanskrit way\. "
     r"This course writes the mantra as Om Mani Padme Hom\.",
     f"Sifu says the mantra the Chinese way, and the Chinese way is correct. Most English books spell it "
     f"the Sanskrit way, {SANSKRIT}. That common spelling is not correct. This course writes the mantra as {NAME}."),
    ("names table header", r"<th>Most English books</th>", "<th>Common English spelling (not correct)</th>"),
    ("names table: Om", r'(<td class="han">嗡</td><td>Om</td>)<td>Om</td>', r"\1<td>Oṃ</td>"),
    ("names table: Mani", r'(<td class="han">嘛呢</td><td>Ma Ni</td>)<td>Mani</td>', r"\1<td>Maṇi</td>"),
    ("names table: Hum", r'(<td class="han">吽</td><td>Hong</td>)<td>Hum</td>', r"\1<td>Hūṃ</td>"),
    ("quiz answer", r"Most English books write Om Mani Padme Hum\.",
     f"Most English books write {SANSKRIT}, from Sanskrit. That common spelling is not correct."),
    ("course name", r"Om Mani Padme Hom", NAME),
]
for label, pattern, repl in SPELLING:
    notes, hits = re.subn(pattern, repl, notes)
    print(f"  spelling: {label}: {hits} fixed" if hits else f"  WARNING: spelling found nothing for {label}")

# ---------------------------------------------------------------- notes CSS
css = re.search(r"<style>\n(/\* Layout.*?)</style>", notes, re.S).group(1)
css = re.sub(r"/\* Layout:.*?\*/\n", "", css)
# The notes page's own header and footer rules would clash with the site header/footer.
css = re.sub(r"\nheader\{[^}]*\}", "", css)
css = re.sub(r"\nfooter\{[^}]*\}", "", css)
css = css.replace("padding-inline:16px;padding-block:0 48px", "padding:0")
(OUT / "assets").mkdir(parents=True, exist_ok=True)
(OUT / "assets" / "notes.css").write_text(
    "/* Generated by tools/build_site.py from " + notes_path.name + ". Do not edit by hand. */\n"
    + css.strip() + "\n", encoding="utf-8")

# ---------------------------------------------------------------- notes JS
js = re.search(r"<script>\n(.*?)</script>", notes, re.S).group(1)
# Every lesson page loads the same script, so each block must skip itself
# when its part of the page is not there.
js = must_replace(js, "PATH.forEach((s,i)=>{", "if(pathList) PATH.forEach((s,i)=>{")
js = must_replace(js, "const box=document.getElementById(boxId);",
                  "const box=document.getElementById(boxId); if(!box) return;")
js = must_replace(js, "toggleAll.addEventListener(", "if(toggleAll) toggleAll.addEventListener(")
js = must_replace(js, "const list=document.getElementById(listId), scoreEl=document.getElementById(scoreId);",
                  "const list=document.getElementById(listId), scoreEl=document.getElementById(scoreId); if(!list) return;")
(OUT / "assets" / "notes.js").write_text(
    "/* Generated by tools/build_site.py from " + notes_path.name + ". Do not edit by hand. */\n"
    + js, encoding="utf-8")

# ---------------------------------------------------------------- split lessons
body = notes[notes.index('<div class="lesson-band" id="lesson1">'):notes.index("<footer>")]
starts = [m.start() for m in re.finditer(r'<div class="lesson-band[^"]*" id="lesson\d"', body)]
if len(starts) != 7:
    sys.exit(f"Build stopped: expected 7 lessons, found {len(starts)}")
chunks = [body[s:e].strip() for s, e in zip(starts, starts[1:] + [len(body)])]

# Which lesson each id lives in, so cross-lesson links can point at the right page.
id_home = {}
for n, chunk in enumerate(chunks, 1):
    for i in re.findall(r'id="([^"]+)"', chunk):
        id_home[i] = n

# Contents cards: lesson title, date and the section list.
cards = re.findall(r'<div class="toc-card">(.*?)</div>', notes, re.S)
lessons = []
for n, (chunk, card) in enumerate(zip(chunks, cards), 1):
    band = re.match(r'<div class="lesson-band[^"]*" id="lesson\d">(.*?)</div>', chunk, re.S)
    lessons.append({
        "n": n,
        "title": html.unescape(re.search(r"<h2>(.*?)</h2>", band.group(1)).group(1)),
        "desc": html.unescape(re.search(r"<p>(.*?)</p>", band.group(1), re.S).group(1)),
        "toc": re.search(r"<ol>(.*?)</ol>", card, re.S).group(1),
        "chunk": chunk,
    })


def fix_links(text, n):
    def repl(m):
        target = m.group(1)
        lm = re.fullmatch(r"lesson(\d)", target)
        if lm:
            return f'href="lesson-{lm.group(1)}.html"'
        home = id_home.get(target)
        if home is None:
            sys.exit(f"Build stopped: link to unknown section #{target}")
        return f'href="#{target}"' if home == n else f'href="lesson-{home}.html#{target}"'
    return re.sub(r'href="#([^"]+)"', repl, text)


def site_header(current):
    pills = "\n".join(
        f'    <a href="lesson-{i}.html"' + (' aria-current="page"' if i == current else "")
        + f'>Lesson {i}</a>' for i in range(1, 8))
    return f'''<header class="site-header">
  <div class="site-header-in">
    <a class="brand" href="./"><span class="han">嗡</span><span>{NAME}</span></a>
    <nav aria-label="Main"><a href="./#lessons">All lessons</a></nav>
  </div>
</header>
<nav class="jump" aria-label="Lessons">
  <div class="wrap jump-in">
{pills}
  </div>
</nav>'''


def page_head(title, desc, css_files):
    links = "\n".join(f'<link rel="stylesheet" href="{c}">' for c in css_files)
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light only">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
{FONTS}
{links}
</head>'''


# ---------------------------------------------------------------- thumbnails
# Newest Thumbnails/Lesson_N_Thumbnail_*.png per lesson -> public/thumbnails/lesson-N.png
thumbs = set()
(OUT / "thumbnails").mkdir(exist_ok=True)
for n in range(1, 8):
    found = sorted((ROOT / "Thumbnails").glob(f"Lesson_{n}_Thumbnail_*.png"))
    if found:
        shutil.copyfile(found[-1], OUT / "thumbnails" / f"lesson-{n}.png")
        thumbs.add(n)
    else:
        print(f"  WARNING: no thumbnail for Lesson {n}; using the plain placeholder")


def video_box(n, title):
    if n in thumbs:
        return (f'<div class="video has-poster" data-lesson="{n}">\n'
                f'  <img class="video-poster" src="thumbnails/lesson-{n}.png" width="1280" height="720" '
                f'alt="Lesson {n}: {html.escape(title)}">\n'
                f'  <span class="video-soon">Video coming soon</span>\n</div>')
    return (f'<div class="video" data-lesson="{n}">\n  <div class="video-ph">\n'
            f'    <span class="video-ph-title">Video coming soon</span>\n'
            f'    <span class="video-ph-sub">Lesson {n} class video</span>\n  </div>\n</div>')


for L in lessons:
    n = L["n"]
    chunk = fix_links(L["chunk"], n)
    # The lesson title becomes the page's main heading.
    chunk = re.sub(r"(<div class=\"lesson-band[^>]*>.*?)<h2>(.*?)</h2>", r"\1<h1>\2</h1>", chunk, count=1, flags=re.S)
    band_end = chunk.index("</div>") + len("</div>")
    band, rest = chunk[:band_end], chunk[band_end:]
    toc = fix_links(L["toc"], n)
    prev_link = (f'<a class="pn prev" href="lesson-{n-1}.html"><span>Previous</span>'
                 f'Lesson {n-1}: {html.escape(lessons[n-2]["title"])}</a>') if n > 1 else '<span></span>'
    next_link = (f'<a class="pn next" href="lesson-{n+1}.html"><span>Next</span>'
                 f'Lesson {n+1}: {html.escape(lessons[n]["title"])}</a>') if n < 7 else \
                '<a class="pn next" href="./#lessons"><span>Next</span>Back to all lessons</a>'
    page = f'''{page_head(f"Lesson {n}: {L['title']} · {NAME}", L["desc"], ["assets/site.css", "assets/notes.css"])}
<body class="lesson-page">
{site_header(n)}
<main class="wrap">

{band}

{video_box(n, L["title"])}

<nav class="in-lesson" aria-label="In this lesson">
  <h2>In this lesson</h2>
  <ol>{toc}</ol>
</nav>
{rest}

<nav class="prevnext" aria-label="Lesson pages">
  {prev_link}
  {next_link}
</nav>

</main>
<footer class="site-footer"><div class="site-footer-in"><span>{NAME} 嗡嘛呢叭咪吽 · A course with Master Wisdom Kindness</span><span>© 2026</span></div></footer>
<script src="assets/videos.js"></script>
<script src="assets/notes.js"></script>
</body>
</html>
'''
    (OUT / f"lesson-{n}.html").write_text(page, encoding="utf-8")

# ---------------------------------------------------------------- landing page
lbody = re.search(r'(<div style="background: #f7f8f6.*)\n</x-dc>', landing, re.S).group(1)
lbody = lbody.strip()
lbody = lbody[:lbody.rstrip().rindex("</div>")].strip()          # drop the outer wrapper's closing tag
lbody = lbody[lbody.index(">") + 1:].strip()                      # and its opening tag
lbody = lbody.replace("{{accent}}", ACCENT)
# Hero: the title becomes the Chinese form; the line under the characters becomes the spelling note.
lbody = must_replace(
    lbody,
    '<span style="font-family: Marcellus, Georgia, serif; font-size: 20px; color: #5b6670">Om Ma Ni Bei Me Hong</span>\n</div>',
    '</div>\n<p style="margin: 0; max-width: 34em; padding: 12px 16px; background: #ffffff; border: 1px solid #dde3df; '
    'border-left: 3px solid #b8466e; border-radius: 0 10px 10px 0; font-size: 16px; color: #3a4650">'
    f'<b>A note on spelling.</b> Most English books write this mantra <i>{SANSKRIT}</i>, from Sanskrit. '
    f'That common spelling is not correct. The correct form is the Chinese: '
    f'<span lang="zh-Hant" style="font-family: \'Noto Serif TC\', serif; color: #b8466e; white-space: nowrap">嗡嘛呢叭咪吽</span>, '
    f'{NAME}. This course uses it throughout.</p>')
lbody, hits = re.subn(r"Om Mani Padme Hom", NAME, lbody)
print(f"  spelling: landing page: {hits} fixed")
lbody = must_replace(lbody, 'href="#top"', 'href="./"')
# Buttons that started Lesson 1 now open the Lesson 1 page.
lbody = lbody.replace('href="#lesson-1"', 'href="lesson-1.html"')


def fix_article(m):
    art = m.group(0)
    n = re.search(r">Lesson (\d)</span>", art).group(1)
    art = re.sub(r'<a href="[^"]*"( style="[^"]*">Watch Lesson \d</a>)', rf'<a href="lesson-{n}.html"\1', art)
    # Thumbnail becomes a link to the lesson; videos.js adds a play button once a video is set.
    if int(n) in thumbs:
        inner = (f'<img src="thumbnails/lesson-{n}.png" width="1280" height="720" alt="" '
                 f'style="width: 100%; height: 100%; object-fit: cover; display: block">'
                 f'<span class="thumb-soon">Video coming soon</span>')
        extra = "; text-decoration: none; position: relative; overflow: hidden"
    else:
        inner, extra = "Video coming soon", "; text-decoration: none; position: relative"
    art, hits = re.subn(r'<div style="(aspect-ratio: 16 / 9;[^"]*)">Video thumbnail</div>',
                        lambda m: f'<a href="lesson-{n}.html" class="thumb" data-lesson="{n}" '
                                  f'aria-label="Watch Lesson {n}" style="{m.group(1)}{extra}">{inner}</a>', art)
    if hits != 1:
        sys.exit(f"Build stopped: no thumbnail box found on landing card {n}")
    return art


lbody, count = re.subn(r"<article.*?</article>", fix_article, lbody, flags=re.S)
if count != 7:
    sys.exit(f"Build stopped: expected 7 lesson cards on the landing page, found {count}")
lbody = lbody.replace("© [YEAR] [SITE NAME]", "© 2026")
if "{{" in lbody or "[SITE" in lbody:
    sys.exit("Build stopped: a placeholder is left in the landing page")

index =f'''{page_head(f"{NAME} 嗡嘛呢叭咪吽 · Free video course",
                      f"Learn what the mantra {NAME} (嗡嘛呢叭咪吽) means, part by part. Often written Om Mani Padme Hum. "
                      "Seven recorded classes with Master Wisdom Kindness (Sifu).",
                      ["assets/site.css"])}
<body class="landing">
{lbody}
<script src="assets/videos.js"></script>
</body>
</html>
'''
(OUT / "index.html").write_text(index, encoding="utf-8")

print(f"Built {OUT} from {landing_path.name} and {notes_path.name}")
for L in lessons:
    print(f"  lesson-{L['n']}.html  {L['title']}")

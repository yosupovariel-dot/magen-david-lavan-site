"""
בונה את האתר הסטטי: src/pages/*.html + src/data.json  ->  docs/
הרצה:  python tools/build.py
אין תלויות חיצוניות (ספריית התקן של פייתון בלבד).
"""
import json
import re
import html
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
OUT = ROOT / "docs"
DATA = json.loads((SRC / "data.json").read_text(encoding="utf-8"))
S = DATA["site"]
TODAY = date.today().isoformat()
VERSION = TODAY.replace("-", "")

NAV = [
    ("index.html", "ראשי"),
    ("about.html", "אודות"),
    ("patrols.html", "הסיירות"),
    ("services.html", "שירותים"),
    ("leadership.html", "הנהלה"),
    ("endorsements.html", "המלצות"),
    ("media.html", "מדיה"),
    ("contact.html", "צור קשר"),
]

e = html.escape


def ext(url, label, cls="", extra=""):
    """קישור חיצוני מאובטח (noopener/noreferrer) עם הודעה לקורא מסך."""
    c = f' class="{cls}"' if cls else ""
    return (f'<a href="{e(url)}"{c} target="_blank" rel="noopener noreferrer"{extra}>'
            f'{label}<span class="sr-only"> (נפתח בחלון חדש)</span></a>')


def icon(name, cls="ico"):
    return f'<svg class="{cls}" aria-hidden="true" focusable="false"><use href="#i-{name}"/></svg>'


def tel_link(display, cls="tel"):
    digits = re.sub(r"\D", "", display)
    intl = "+972" + digits[1:] if digits.startswith("0") else "+" + digits
    return f'<a class="{cls}" href="tel:{intl}" dir="ltr">{e(display)}</a>'


def picture(name, alt, cls="", sizes="100vw", eager=False, w=1600, h=1067):
    loading = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    c = f' class="{cls}"' if cls else ""
    return (f'<img{c} src="assets/img/{name}-1600.webp" '
            f'srcset="assets/img/{name}-800.webp 800w, assets/img/{name}-1600.webp 1600w" '
            f'sizes="{sizes}" width="{w}" height="{h}" alt="{e(alt)}" {loading}>')


# ---------- רכיבים ----------

def stats_block():
    items = []
    for st in S["stats"]:
        items.append(
            f'<div class="stat"><dt class="stat__label">{e(st["label"])}</dt>'
            f'<dd class="stat__num"><span class="count" data-to="{st["value"]}">{st["value"]:,}</span><span class="stat__plus">+</span></dd></div>')
    return '<dl class="stats">' + "".join(items) + "</dl>"


def patrol_card(p, d):
    meta = []
    if p["manager"]:
        meta.append(f'<p class="patrol__meta"><span class="k">בניהול</span> {e(p["manager"])}</p>')
    if p["phone"]:
        meta.append(f'<p class="patrol__meta"><span class="k">מוקד הסיירת</span> {tel_link(p["phone"])}</p>')
    if not meta:
        meta.append(f'<p class="patrol__meta patrol__meta--muted">לפרטים: מוקד המחוז {tel_link(d["hotline"])}</p>')
    join = ext(p["group"], f'{icon("whatsapp")} הצטרפות לסיירת<span class="sr-only"> {e(p["city"])} בוואטסאפ</span>',
               "btn btn--ghost btn--sm") if p["group"] else ""
    return (f'<li class="patrol" data-city="{e(p["city"])}"><h3 class="patrol__city">סיירת {e(p["city"])}</h3>'
            + "".join(meta) + join + "</li>")


def patrols_full():
    out = []
    for i, d in enumerate(DATA["districts"], 1):
        group_btn = (ext(d["group"], f'{icon("whatsapp")} להתנדבות ב{e(d["name"])}', "btn btn--primary")
                     if d["group"] else
                     f'<a class="btn btn--primary" href="tel:+972{re.sub(r"[^0-9]", "", d["hotline"])[1:]}">{icon("phone")} למוקד {e(d["name"])}</a>')
        cards = "".join(patrol_card(p, d) for p in d["patrols"])
        out.append(f'''
<section class="district district--{d["tone"]}" id="{d["id"]}" aria-labelledby="h-{d["id"]}">
  <div class="district__head">
    <div class="district__media">{picture(d["image"], "", "district__img", "(max-width: 900px) 100vw, 40vw")}</div>
    <div class="district__intro">
      <p class="eyebrow"><span class="eyebrow__num">0{i}</span> {len(d["patrols"])} סיירות</p>
      <h2 id="h-{d["id"]}" class="district__title">{e(d["name"])}</h2>
      <dl class="district__facts">
        <div><dt>בפיקודו של</dt><dd>{e(d["commander"])}</dd></div>
        <div><dt>מוקד המחוז</dt><dd>{tel_link(d["hotline"])}</dd></div>
      </dl>
      {group_btn}
    </div>
  </div>
  <ul class="patrol-grid" role="list">{cards}</ul>
</section>''')
    return "\n".join(out)


def district_cards():
    out = []
    for i, d in enumerate(DATA["districts"], 1):
        out.append(f'''
<li class="dcard dcard--{d["tone"]}">
  <a class="dcard__link" href="patrols.html#{d["id"]}">
    <span class="dcard__idx">0{i}</span>
    <span class="dcard__name">{e(d["name"])}</span>
    <span class="dcard__count"><b>{len(d["patrols"])}</b> סיירות</span>
    <span class="dcard__cities">{e(" · ".join(p["city"] for p in d["patrols"]))}</span>
    <span class="dcard__cmd">מפקד המחוז: {e(d["commander"])}</span>
    {icon("arrow", "ico dcard__arrow")}
  </a>
</li>''')
    return '<ul class="dcards" role="list">' + "".join(out) + "</ul>"


def leaders():
    out = []
    for d in DATA["districts"]:
        initials = "".join(w[0] for w in d["commander"].split()[:2])
        note = f'<p class="leader__note">{e(d["commander_note"])}</p>' if d["commander_note"] else ""
        out.append(f'''
<li class="leader leader--{d["tone"]}">
  <div class="leader__mono" aria-hidden="true">{e(initials)}</div>
  <h3 class="leader__name">{e(d["commander"])}</h3>
  <p class="leader__role">{e(d["commander_role"])}</p>
  <p class="leader__areas"><span class="k">בפיקודו ערים וישובים:</span> {e(d["areas"])}.</p>
  {note}
  <p class="leader__tel"><span class="k">מוקד המחוז</span> {tel_link(d["hotline"])}</p>
</li>''')
    return '<ul class="leaders" role="list">' + "".join(out) + "</ul>"


def quote_card(t, big=False):
    role = f'<span class="quote__role">{e(t["role"])}</span>' if t["role"] else ""
    vid = (ext(f'https://www.youtube.com/watch?v={t["video"]}',
               f'{icon("play")} לצפייה בדברים<span class="sr-only"> של {e(t["name"])} ביוטיוב</span>',
               "quote__video") if t["video"] else "")
    cls = "quote quote--big" if big else "quote"
    return (f'<li class="{cls}" data-group="{t["group"]}"><figure><blockquote><p>{e(t["quote"])}</p></blockquote>'
            f'<figcaption><span class="quote__name">{e(t["name"])}</span>{role}</figcaption></figure>{vid}</li>')


def testimonials_all():
    return '<ul class="quotes" role="list" id="quotes">' + "".join(quote_card(t) for t in DATA["testimonials"]) + "</ul>"


def testimonials_featured():
    fs = [t for t in DATA["testimonials"] if t["featured"]][:6]
    return '<ul class="quotes quotes--rail" role="list">' + "".join(quote_card(t) for t in fs) + "</ul>"


def ticker():
    cities = [p["city"] for d in DATA["districts"] for p in d["patrols"]]
    row = "".join(f'<li>{icon("star", "ico ticker__star")}סיירת {e(c)}</li>' for c in cities)
    return (f'<div class="ticker" aria-hidden="true"><ul class="ticker__track">{row}{row}</ul></div>')


def video_facade(vid, title):
    return f'''
<div class="vframe" data-yt="{vid}" data-title="{e(title)}">
  <img src="assets/video/{vid}.webp" alt="" width="480" height="360" loading="lazy" decoding="async">
  <button type="button" class="vframe__play" aria-label="הפעלת הסרטון: {e(title)}">{icon("play", "ico ico--xl")}</button>
  <p class="vframe__note">הסרטון ייטען מ-YouTube רק לאחר לחיצה.</p>
</div>'''


def social_links(cls="social"):
    s = S["social"]
    items = [
        ("facebook", "פייסבוק", s["facebook"]),
        ("youtube", "יוטיוב", s["youtube"]),
        ("instagram", "אינסטגרם", s["instagram"]),
        ("whatsapp", "סטטוסים בוואטסאפ", s["status"]),
    ]
    return (f'<ul class="{cls}" role="list">' + "".join(
        f'<li>{ext(u, icon(k) + f"<span class=\"social__t\">{t}</span>", "", f" aria-label=\"{t}\"")}</li>'
        for k, t, u in items) + "</ul>")


COUNTS = {
    "total_patrols": sum(len(d["patrols"]) for d in DATA["districts"]),
    "total_districts": len(DATA["districts"]),
}

COMPONENTS = {
    "stats": stats_block,
    "patrols_full": patrols_full,
    "district_cards": district_cards,
    "leaders": leaders,
    "testimonials_all": testimonials_all,
    "testimonials_featured": testimonials_featured,
    "ticker": ticker,
    "main_video": lambda: video_facade(S["main_video"], "מגן דוד לבן - וידאו עלינו"),
    "social": social_links,
}


def fill(text):
    def rep(m):
        key = m.group(1)
        if key in COMPONENTS:
            return COMPONENTS[key]()
        if key.startswith("icon:"):
            return icon(key[5:])
        if key.startswith("img:"):
            # {{img:name|alt|class|sizes|eager}}
            parts = (key[4:].split("|") + ["", "", "", ""])[:5]
            name, alt, cls, sizes, flag = parts
            return picture(name, alt, cls, sizes or "100vw", eager=flag == "eager")
        if key.startswith("ext:"):
            # {{ext:URL|label|class}}
            url, label, *rest = key[4:].split("|")
            return ext(url, label, rest[0] if rest else "")
        if key in COUNTS:
            return str(COUNTS[key])
        cur = S
        for part in key.split("."):
            cur = cur[part]
        return e(str(cur))
    return re.sub(r"\{\{\s*([^}]+?)\s*\}\}", rep, text)


# ---------- SEO ----------

def org_jsonld():
    return {
        "@context": "https://schema.org",
        "@type": "NGO",
        "@id": S["url"] + "/#org",
        "name": S["name"],
        "alternateName": S["name_en"],
        "slogan": S["slogan"],
        "url": S["url"] + "/",
        "logo": S["url"] + "/icon-512.png",
        "image": S["url"] + "/og-image.jpg",
        "email": S["email"],
        "address": {"@type": "PostalAddress", "addressLocality": "אבן שמואל", "addressCountry": "IL"},
        "areaServed": {"@type": "Country", "name": "ישראל"},
        "contactPoint": [
            {"@type": "ContactPoint", "telephone": S["volunteer_line"]["tel"], "contactType": "volunteer", "name": S["volunteer_line"]["label"], "availableLanguage": "he"},
            {"@type": "ContactPoint", "telephone": S["emergency_line"]["tel"], "contactType": "emergency", "name": S["emergency_line"]["label"], "availableLanguage": "he"},
        ],
        "sameAs": [S["social"]["facebook"], S["social"]["youtube"]],
    }


def breadcrumb(slug, title):
    if slug == "index.html":
        return None
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "ראשי", "item": S["url"] + "/"},
            {"@type": "ListItem", "position": 2, "name": title, "item": f'{S["url"]}/{slug}'},
        ],
    }


def nav_html(slug, mobile=False):
    items = []
    for href, label in NAV:
        cur = ' aria-current="page"' if href == slug else ""
        items.append(f'<li><a href="{href}"{cur}>{label}</a></li>')
    return "".join(items)


def build():
    layout = (SRC / "layout.html").read_text(encoding="utf-8")
    pages = sorted((SRC / "pages").glob("*.html"))
    sitemap = []
    for p in pages:
        raw = p.read_text(encoding="utf-8")
        m = re.match(r"\s*<!--\s*(\{.*?\})\s*-->", raw, re.S)
        meta = json.loads(m.group(1))
        body = raw[m.end():]
        slug = p.name
        canonical = S["url"] + "/" + ("" if slug == "index.html" else slug)
        lds = [org_jsonld()] if slug == "index.html" else []
        bc = breadcrumb(slug, meta.get("crumb", meta["title"]))
        if bc:
            lds.append(bc)
        lds += meta.get("jsonld", [])
        ld_html = "".join(
            f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in lds)
        full_title = meta["title"] if slug == "index.html" else f'{meta["title"]} | {S["name"]}'
        out = layout
        repl = {
            "%TITLE%": e(full_title),
            "%DESC%": e(meta["description"]),
            "%CANONICAL%": canonical,
            "%OG_IMAGE%": S["url"] + "/og-image.jpg",
            "%ROBOTS%": meta.get("robots", "index,follow,max-image-preview:large"),
            "%JSONLD%": ld_html,
            "%NAV%": nav_html(slug),
            "%BODYCLASS%": meta.get("bodyclass", ""),
            "%PRELOAD%": (f'<link rel="preload" as="image" href="assets/img/{meta["preload"]}-1600.webp" '
                          f'imagesrcset="assets/img/{meta["preload"]}-800.webp 800w, assets/img/{meta["preload"]}-1600.webp 1600w" imagesizes="100vw">'
                          if meta.get("preload") else ""),
            "%V%": VERSION,
            "%YEAR%": str(date.today().year),
            "%CONTENT%": body,
        }
        for k, v in repl.items():
            out = out.replace(k, v)
        out = fill(out)
        (OUT / slug).write_text(out, encoding="utf-8")
        if meta.get("sitemap", True):
            sitemap.append((canonical, meta.get("priority", "0.7")))
        print("built", slug)

    xml = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, pr in sitemap:
        xml.append(f"  <url><loc>{loc}</loc><lastmod>{TODAY}</lastmod><priority>{pr}</priority></url>")
    xml.append("</urlset>")
    (OUT / "sitemap.xml").write_text("\n".join(xml) + "\n", encoding="utf-8")
    print("built sitemap.xml")


if __name__ == "__main__":
    build()

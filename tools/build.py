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
_EMB = json.loads((SRC / "emblems.json").read_text(encoding="utf-8")) if (SRC / "emblems.json").exists() else {}
EMBLEMS = _EMB.get("map", {})
DISTRICT_LOGOS = _EMB.get("districts", {})
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
    vol, helped, comp = S["stats"]
    ds = DATA["districts"]
    total = sum(len(d["patrols"]) for d in ds)

    def num(v):
        return (f'<p class="impact__num"><span class="count" data-to="{v}">{v:,}</span>'
                f'<span class="impact__plus" aria-hidden="true">+</span></p>')

    bar = "".join(f'<span class="tone-{d["tone"]} g{len(d["patrols"])}"></span>' for d in ds)
    legend = "".join(f'<span class="impact__lg"><i class="tone-{d["tone"]}"></i>{e(d["name"].replace("מחוז ", ""))} <b>{len(d["patrols"])}</b></span>'
                     for d in ds)
    return f'''
<div class="impact">
  <div class="impact__tile impact__tile--feat">
    <svg class="impact__hex" viewBox="0 0 200 200" aria-hidden="true"><path d="M100 14 174 142H26zM100 186 26 58h148z" fill="none" stroke="currentColor" stroke-width="1.4"/></svg>
    <span class="impact__ico">{icon("heart")}</span>
    {num(helped["value"])}
    <p class="impact__label">{e(helped["label"])}</p>
    <p class="impact__note">בזירה הביטחונית, בזירה הנפשית ובזירה העורפית.</p>
  </div>
  <div class="impact__tile impact__tile--vol">
    <span class="impact__ico">{icon("users")}</span>
    {num(vol["value"])}
    <p class="impact__label">{e(vol["label"])}</p>
    <p class="impact__note">מתנדבי סיירות הפרוסים בכל חלקי הארץ.</p>
  </div>
  <div class="impact__tile impact__tile--comp">
    <span class="impact__ico">{icon("hand")}</span>
    {num(comp["value"])}
    <p class="impact__label">{e(comp["label"])}</p>
    <p class="impact__note">גופים שבחרו לעבוד לצד המערך.</p>
  </div>
  <a class="impact__tile impact__tile--patrols" href="patrols.html">
    <span class="impact__row">
      <span>
        <span class="impact__label"><span class="sr-only">{total} </span>סיירות אזוריות</span>
        <span class="impact__note">ב-{len(ds)} מחוזות, מאילת ועד צפת.</span>
      </span>
      <span class="impact__num" aria-hidden="true"><span>{total}</span></span>
    </span>
    <span class="impact__bar" aria-hidden="true">{bar}</span>
    <span class="impact__legend" aria-hidden="true">{legend}</span>
    <span class="impact__go">לכל הסיירות{icon("arrow")}</span>
  </a>
</div>'''


SHORT = {"north": "צפון", "center": "מרכז", "judea-samaria": "יו״ש", "south": "דרום"}


ABBR = {"ראשון לציון": "ראשל״צ"}


def initials(city):
    if city in ABBR:
        return ABBR[city]
    words = city.replace("-", " ").split()
    if len(words) == 1:
        return words[0][0]
    letters = [w[0] for w in words[:2]]
    return letters[0] + "״" + letters[1]


def district_emblem(d, cls="dlogo"):
    return (f'<span class="{cls} {cls}--{d["tone"]}" aria-hidden="true">'
            f'<img src="assets/{("emblems/" + DISTRICT_LOGOS[d["id"]]) if d["id"] in DISTRICT_LOGOS else "img/logo-160.webp"}" width="72" height="72" alt="">'
            f'<span class="{cls}__t">{e(SHORT.get(d["id"], ""))}</span></span>')


def city_badge(city, tone):
    if city in EMBLEMS:
        return (f'<span class="cbadge cbadge--img cbadge--{tone}" aria-hidden="true">'
                f'<img src="assets/emblems/{EMBLEMS[city]}" width="56" height="56" alt="" loading="lazy" decoding="async"></span>')
    t = initials(city)
    small = " cbadge--sm" if len(t) > 3 else ""
    return f'<span class="cbadge cbadge--{tone}{small}" aria-hidden="true">{e(t)}</span>'


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
    return (f'<li class="patrol" data-city="{e(p["city"])}"><div class="patrol__head">{city_badge(p["city"], d["tone"])}'
            f'<h3 class="patrol__city">סיירת {e(p["city"])}</h3></div>'
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
      <div class="district__titlerow">{district_emblem(d)}<h2 id="h-{d["id"]}" class="district__title">{e(d["name"])}</h2></div>
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
        if (OUT / "assets" / "people" / f'leader-{d["id"]}.webp').exists():
            photo = (f'<img class="leader__photo" src="assets/people/leader-{d["id"]}.webp" width="96" height="96" '
                     f'alt="{e(d["commander"])}" loading="lazy" decoding="async">')
        else:
            photo = f'<div class="leader__mono" aria-hidden="true">{e(initials)}</div>'
        note = f'<p class="leader__note">{e(d["commander_note"])}</p>' if d["commander_note"] else ""
        out.append(f'''
<li class="leader leader--{d["tone"]}">
  {photo}
  <h3 class="leader__name">{e(d["commander"])}</h3>
  <p class="leader__role">{e(d["commander_role"])}</p>
  <p class="leader__areas"><span class="k">בפיקודו ערים וישובים:</span> {e(d["areas"])}.</p>
  {note}
  <p class="leader__tel"><span class="k">מוקד המחוז</span> {tel_link(d["hotline"])}</p>
</li>''')
    return '<ul class="leaders" role="list">' + "".join(out) + "</ul>"


PEOPLE_DIR = OUT / "assets" / "people"


def avatar(t):
    if t["video"] and (PEOPLE_DIR / f'{t["video"]}.webp').exists():
        return (f'<img class="quote__avatar" src="assets/people/{t["video"]}.webp" width="56" height="56" '
                f'alt="" loading="lazy" decoding="async">')
    words = [w for w in t["name"].replace('"', "").split() if w not in ("הרב", "הגאון", "רבי", "שליט״א", "שליט\"א")]
    letters = "".join(w[0] for w in words[:2])
    return f'<span class="quote__avatar quote__avatar--mono" aria-hidden="true">{e(letters)}</span>'


def ordered_testimonials():
    rabbis = [t for t in DATA["testimonials"] if t["group"] == "rabbis"]
    public = [t for t in DATA["testimonials"] if t["group"] != "rabbis"]
    out = []
    while rabbis or public:
        if rabbis:
            out.append(rabbis.pop(0))
        if public:
            out.append(public.pop(0))
    return out


def quote_card(t):
    role = f'<span class="quote__role">{e(t["role"])}</span>' if t["role"] else ""
    vid = (ext(f'https://www.youtube.com/watch?v={t["video"]}',
               f'{icon("play")} לצפייה בדברים<span class="sr-only"> של {e(t["name"])} ביוטיוב</span>',
               "quote__video") if t["video"] else "")
    return (f'<li class="quote" data-group="{t["group"]}"><figure><blockquote><p>{e(t["quote"])}</p></blockquote>'
            f'<figcaption>{avatar(t)}<span class="quote__who"><span class="quote__name">{e(t["name"])}</span>{role}</span>'
            f'</figcaption></figure>{vid}</li>')


def testimonials_rail():
    ts = ordered_testimonials()
    return ('<div class="rail" data-rail>'
            '<ul class="quotes quotes--rail" id="quotes" role="list" tabindex="0" aria-label="המלצות - ניתן לגלול הצידה">'
            + "".join(quote_card(t) for t in ts) + "</ul>"
            '<div class="rail__ctrl">'
            f'<button type="button" class="rail__btn" data-dir="prev" aria-label="ההמלצה הקודמת">{icon("arrow", "ico rail__ico--prev")}</button>'
            '<div class="rail__track" aria-hidden="true"><span class="rail__fill"></span></div>'
            f'<p class="rail__count" aria-live="polite"><b class="rail__cur">1</b> / <span class="rail__total">{len(ts)}</span></p>'
            f'<button type="button" class="rail__btn" data-dir="next" aria-label="ההמלצה הבאה">{icon("arrow")}</button>'
            '</div></div>')


GALLERY_CATS = [("security", "מתנדבינו בביטחון"), ("agriculture", "מתנדבינו בחקלאות"), ("transport", "מתנדבינו בשינועים")]


def gallery():
    data = json.loads((SRC / "gallery.json").read_text(encoding="utf-8"))
    tabs, panels = [], []
    for i, (key, label) in enumerate(GALLERY_CATS):
        sel = i == 0
        items = data.get(key, [])
        tabs.append(f'<button type="button" class="gtab" role="tab" id="gt-{key}" aria-controls="gp-{key}" '
                    f'aria-selected="{"true" if sel else "false"}" tabindex="{0 if sel else -1}">{e(label)} '
                    f'<span class="gtab__n">{len(items)}</span></button>')
        figs = "".join(
            f'<li class="gitem"><a class="gitem__a" href="assets/gallery/{it["f"]}.webp" data-lightbox="{key}" '
            f'data-w="{it["w"]}" data-h="{it["h"]}">'
            f'<img src="assets/gallery/{it["f"]}-s.webp" width="{it["tw"]}" height="{it["th"]}" '
            f'alt="{e(label)} - תמונה {n} מתוך {len(items)}" loading="lazy" decoding="async"></a></li>'
            for n, it in enumerate(items, 1))
        panels.append(f'<div class="gpanel" role="tabpanel" id="gp-{key}" aria-labelledby="gt-{key}"{"" if sel else " hidden"}>'
                      f'<ul class="ggrid" role="list">{figs}</ul></div>')
    return (f'<div class="gallery"><div class="gtabs" role="tablist" aria-label="קטגוריות הגלריה">{"".join(tabs)}</div>'
            + "".join(panels) +
            '<div class="lb" id="lightbox" role="dialog" aria-modal="true" aria-label="צפייה בתמונה" hidden>'
            f'<button type="button" class="lb__close" aria-label="סגירה">{icon("close")}</button>'
            f'<button type="button" class="lb__nav lb__nav--prev" aria-label="התמונה הקודמת">{icon("arrow", "ico rail__ico--prev")}</button>'
            '<figure class="lb__fig"><img class="lb__img" alt=""><figcaption class="lb__cap" aria-live="polite"></figcaption></figure>'
            f'<button type="button" class="lb__nav lb__nav--next" aria-label="התמונה הבאה">{icon("arrow")}</button>'
            '</div></div>')


THANKS = [
    ("עיצוב ובניית האתר", "ArielYosupov-WebDesign", "https://arielyosupov-webdesign.com", "האתר עוצב ונבנה מחדש על ידי ArielYosupov-WebDesign."),
    ("תודות", "SearchAOA", "https://www.searchaoa.com/", "תודה לצוותי SearchAOA."),
    ("תודות", "גרפיקה י.ז", "", "תודה לגרפיקה י.ז."),
    ("בתמיכת", "הרבנות הראשית לישראל", "https://www.gov.il/he/departments/chief_rabbinate_of_israel/govil-landing-page", "בתמיכת הרבנות הראשית."),
    ("בתמיכת", "שרים בכנסת ישראל", "https://main.knesset.gov.il/pages/default.aspx", "בתמיכת שרים בכנסת ישראל."),
    ("בשיתוף", "BANO - יזמות ופרסום", "https://chat.whatsapp.com/JdA5tZc00FQ3LCMmBomgCL", "בשיתוף חברת BANO - יזמות ופרסום."),
]


def thanks():
    out = []
    for i, (k, name, url, note) in enumerate(THANKS, 1):
        link = ext(url, f'לאתר{icon("arrow")}', "thanks__link", f' aria-label="{e(name)} - מעבר לאתר"') if url else ""
        out.append(f'<li class="thanks__item"><span class="thanks__n" aria-hidden="true">{i:02d}</span>'
                   f'<span class="thanks__k">{e(k)}</span><h3 class="thanks__name">{e(name)}</h3>'
                   f'<p class="thanks__note">{e(note)}</p>{link}</li>')
    return '<ul class="thanks" role="list">' + "".join(out) + "</ul>"


def ticker():
    items = [(p["city"], p["group"]) for d in DATA["districts"] for p in d["patrols"] if p["group"]]

    def row(hidden):
        extra = ' tabindex="-1"' if hidden else ""
        return "".join(
            f'<li><a href="{e(g)}" target="_blank" rel="noopener noreferrer"{extra}>'
            f'{icon("star", "ico ticker__star")}סיירת {e(c)}'
            + ("" if hidden else '<span class="sr-only"> - הצטרפות לקבוצת הוואטסאפ (נפתח בחלון חדש)</span>')
            + "</a></li>" for c, g in items)

    return ('<nav class="ticker" aria-label="קבוצות הוואטסאפ של הסיירות"><div class="ticker__move">'
            f'<ul class="ticker__track" role="list">{row(False)}</ul>'
            f'<ul class="ticker__track" role="list" aria-hidden="true">{row(True)}</ul>'
            '</div></nav>')


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
    "testimonials_rail": testimonials_rail,
    "thanks": thanks,
    "gallery": gallery,
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
        "address": {"@type": "PostalAddress", "streetAddress": "הזמיר 2", "addressLocality": "אבן שמואל", "addressCountry": "IL"},
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


def mnav_html(slug):
    items = []
    for i, (href, label) in enumerate(NAV, 1):
        cur = ' aria-current="page"' if href == slug else ""
        items.append(f'<li><a href="{href}"{cur}><span class="mnav__n" aria-hidden="true">{i:02d}</span>'
                     f'<span class="mnav__t">{label}</span>{icon("arrow", "ico mnav__arrow")}</a></li>')
    items.append(f'<li><a href="accessibility.html"{" aria-current=\"page\"" if slug == "accessibility.html" else ""}>'
                 f'<span class="mnav__n" aria-hidden="true">{len(NAV) + 1:02d}</span><span class="mnav__t">נגישות</span>'
                 f'{icon("arrow", "ico mnav__arrow")}</a></li>')
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
            "%MNAV%": mnav_html(slug),
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


# הפניות מכתובות האתר הישן (למניעת אובדן דירוג בגוגל אחרי מעבר הדומיין)
OLD_URLS = {
    "אודות-1": "about.html",
    "על-האתר": "about.html",
    "עוד-עלינו": "about.html",
    "הסיירות-שלנו": "patrols.html",
    "services": "services.html",
    "גלריה": "media.html",
    "וידאו-עלינו": "media.html",
    "דברו-במספרים": "index.html",
    "הנהלת-המערך-הארצי": "leadership.html",
    "המלצות": "endorsements.html",
    "תרומה": "donate.html",
    "privacy": "privacy.html",
}


def build_redirects():
    for old, new in OLD_URLS.items():
        target = S["url"] + "/" + ("" if new == "index.html" else new)
        d = OUT / old
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(
            '<!doctype html><html lang="he" dir="rtl"><head><meta charset="utf-8">'
            f'<title>{e(S["name"])}</title><link rel="canonical" href="{target}">'
            '<meta name="robots" content="noindex,follow">'
            f'<meta http-equiv="refresh" content="0; url=../{new}"></head>'
            f'<body><p><a href="../{new}">המשך לעמוד החדש</a></p></body></html>\n',
            encoding="utf-8")
    print("built", len(OLD_URLS), "redirects")


if __name__ == "__main__":
    build()
    build_redirects()

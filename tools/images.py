"""
מכין את תמונות האתר (docs/assets/img/v-*.webp) לטעינה מהירה:
  * יוצר גרסה קטנה ‎-480‎ לכל תמונה (לטלפונים ולתמונות קטנות).
  * דוחס מחדש קבצים כבדים מדי (מעל ~200KB).
  * שומר את המידות האמיתיות ותצוגה מקדימה מטושטשת (LQIP) ב-src/images.json,
    ומפיק docs/css/lqip.css - כך שבזמן הטעינה רואים טשטוש של התמונה ולא מסגרת ריקה.

הרצה (דורש Pillow):  python tools/images.py
מריצים פעם אחת אחרי הוספה/החלפה של תמונה, ואז  python tools/build.py
"""
import base64
import io
import json
from pathlib import Path

from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "docs" / "assets" / "img"
MAX_BYTES = 200_000
SIZES = (("480", 480), ("800", 800), ("1200", 1200))


def save(im, path, q):
    im.save(path, "WEBP", quality=q, method=6)


def main():
    meta_path = ROOT / "src" / "images.json"
    done = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
    meta = {}
    css = ["/* נוצר אוטומטית ע\"י tools/images.py - לא לערוך ידנית */"]
    for big in sorted(IMG.glob("v-*-1600.webp")):
        name = big.name[: -len("-1600.webp")]
        im = Image.open(big).convert("RGB")
        if name not in done and big.stat().st_size > MAX_BYTES:  # רק פעם אחת, למנוע דחיסה חוזרת
            for q in (80, 76, 72, 68):
                buf = io.BytesIO()
                im.save(buf, "WEBP", quality=q, method=6)
                if buf.tell() <= MAX_BYTES:
                    break
            big.write_bytes(buf.getvalue())
            im = Image.open(big).convert("RGB")
        w, h = im.size
        variants = {"1600": [w, h]}
        for suf, tw in SIZES:
            p = IMG / f"{name}-{suf}.webp"
            if w <= tw:
                continue
            th = round(h * tw / w)
            if suf != "800" or not p.exists():  # ‎-800‎ קיים כבר מהמקור
                save(im.resize((tw, th), Image.LANCZOS), p, 78)
            variants[suf] = list(Image.open(p).size)
        # LQIP: תמונה זעירה מטושטשת, מוטמעת ב-CSS כ-data URI
        tiny = im.resize((24, max(1, round(24 * h / w))), Image.LANCZOS).filter(ImageFilter.GaussianBlur(0.6))
        buf = io.BytesIO()
        tiny.save(buf, "WEBP", quality=45)
        uri = "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()
        css.append(f".lqip-{name}{{background-image:url({uri})}}")
        meta[name] = {"w": w, "h": h, "variants": variants}
        print(f"{name}: {w}x{h}, {big.stat().st_size // 1024}KB")
    css.append("img[class*=\"lqip-\"]{background-size:cover;background-position:center;background-repeat:no-repeat}")
    (ROOT / "docs" / "css" / "lqip.css").write_text("\n".join(css) + "\n", encoding="utf-8")
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

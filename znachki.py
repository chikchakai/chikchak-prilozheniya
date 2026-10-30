"""Android icons and splash for a wrapper app from one square full-bleed picture.

py -X utf8 znachki.py <app folder> <square png> <background #hex> <scale 0..1>
scale = share of the 108dp adaptive canvas the picture takes (1 = full bleed).
"""
import pathlib
import sys

from PIL import Image, ImageDraw

papka, kartinka, fon, masshtab = pathlib.Path(sys.argv[1]), sys.argv[2], sys.argv[3], float(sys.argv[4])
res = papka / "android/app/src/main/res"
ish = Image.open(kartinka).convert("RGBA")
PLOTNOSTI = {"mdpi": 1, "hdpi": 1.5, "xhdpi": 2, "xxhdpi": 3, "xxxhdpi": 4}


def kvadrat(razmer, dolya, kraya=fon):
    holst = Image.new("RGBA", (razmer, razmer), kraya)
    k = round(razmer * dolya)
    holst.alpha_composite(ish.resize((k, k), Image.LANCZOS), ((razmer - k) // 2, (razmer - k) // 2))
    return holst


for imya, p in PLOTNOSTI.items():
    d = res / f"mipmap-{imya}"
    legacy = round(48 * p)
    # Legacy launchers: the visible 72/108 part of the adaptive picture.
    vidno = kvadrat(round(108 * p), masshtab).crop((round(18 * p), round(18 * p), round(90 * p), round(90 * p))).resize((legacy, legacy), Image.LANCZOS)
    vidno.save(d / "ic_launcher.png")
    maska = Image.new("L", vidno.size, 0)
    ImageDraw.Draw(maska).ellipse((0, 0, legacy - 1, legacy - 1), fill=255)
    krug = Image.new("RGBA", vidno.size, (0, 0, 0, 0))
    krug.paste(vidno, mask=maska)
    krug.save(d / "ic_launcher_round.png")
    kvadrat(round(108 * p), masshtab).save(d / "ic_launcher_foreground.png")

(res / "values/ic_launcher_background.xml").write_text(
    f'<?xml version="1.0" encoding="utf-8"?>\n<resources>\n    <color name="ic_launcher_background">{fon}</color>\n</resources>\n', encoding="utf-8")

# Splash for Android < 12: background colour with the icon in the middle.
for f in res.glob("drawable*/splash.png"):
    w, h = Image.open(f).size
    holst = Image.new("RGB", (w, h), fon)
    k = round(min(w, h) * 0.32)
    znachok = kvadrat(round(k * 108 / 72), masshtab).crop((round(k * 18 / 72), round(k * 18 / 72), round(k * 90 / 72), round(k * 90 / 72)))
    m = Image.new("L", znachok.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, znachok.size[0] - 1, znachok.size[1] - 1), radius=k // 5, fill=255)
    holst.paste(znachok.convert("RGB"), ((w - znachok.size[0]) // 2, (h - znachok.size[1]) // 2), m)
    holst.save(f)

# The template's vector foreground would sit on top of our PNG one.
(res / "drawable-v24/ic_launcher_foreground.xml").unlink(missing_ok=True)
print("ok", papka)

"""Слои логотипа «Хинкальная City» и фото блюд для заставки приложения Хинкальной (30.10.2026).

Логотип — вектор со старого сайта (hinkali.city/safari-pinned-tab.svg, 21 контур). Режем на слои
регионами: рамка, хинкали, вилка, нож (вырезанное «Кафе» заливаем), надпись, «City».
py -X utf8 zastavka_sloi.py <pinned.svg>  ->  hinkali/www/zastavka/*.png|webp + sloi.json
"""
import json
import pathlib
import re
import sys

from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

# Логотип только чёрный, как в оригинале (владелец 30.10): линии и «City» чёрные, хинкали внутри белое.
KREM, TESTO, UGOL, SHAFRAN = "#141416", "#FFFFFF", "#141416", "#141416"
STAL, STAL_SVET = "#D3D6D9", "#ECEEF0"  # светлая сталь, как светлая тема кассы
OKNO = (30, 100, 970, 850)          # рамка кадра в координатах вектора (1000 x 1000, y вниз)
CITY = (336, 674)                   # левый верх «City»: в уголке рамки под «ин», ниже «кал» проходит край рамки
MASHTAB = 1.4                        # px на единицу вектора
PAPKA = pathlib.Path("hinkali/www/zastavka")
FOTO = pathlib.Path("C:/resto-testing/vitrina_hinkalnaya/v2/foto")
BLYUDA = {  # порядок вылета
    "megrel": "cldrgyf8x002oo98l0bpdb73b", "shashlyk": "cldrgyf3t001co98ljv13qjj9",
    "harcho": "cldrgyfag002zo98l0g2ybz5l", "adzhar": "cldrgyf9a002qo98lyoap69ta",
    "tarhun": "cldrgyf16000ko98lkje3oz2l", "phali": "cldrgyfdx003uo98l10t0del2",
    "odzhahuri": "cldrgyf62001wo98lg8uekq46", "hinkali": "cldrgyfg3004co98l60rkptxn",
}

ds = re.findall(r'<path d="([^"]+)"', pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
x0, y0, x1, y1 = OKNO
W, H = round((x1 - x0) * MASHTAB), round((y1 - y0) * MASHTAB)
VILKA = (300, 462, 830, 516)
TEKST = (0, 520, 1000, 700)


def kontury(nomera, cvet):
    return "".join(f'<path d="{ds[i]}" fill="{cvet}"/>' for i in nomera)


def rect(r):
    return f'<rect x="{r[0]}" y="{r[1]}" width="{r[2] - r[0]}" height="{r[3] - r[1]}"/>'


def svg(vnutri, defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="{x0} {y0} {x1 - x0} {y1 - y0}">'
            f'<defs>{defs}</defs>{vnutri}</svg>')


VEKTOR = '<g transform="translate(0,1000) scale(0.1,-0.1)">{}</g>'
CLIP = (f'<clipPath id="vilka">{rect(VILKA)}</clipPath><clipPath id="tekst">{rect(TEKST)}</clipPath>'
        f'<mask id="ramka"><rect x="0" y="0" width="1000" height="1000" fill="white"/>'
        f'<g fill="black">{rect(VILKA)}{rect(TEKST)}</g></mask>')
SLOI = {
    "ramka": svg(f'<g mask="url(#ramka)">{VEKTOR.format(kontury([0], KREM))}</g>', CLIP),
    "vilka": svg(f'<g clip-path="url(#vilka)">{VEKTOR.format(kontury([0], KREM))}</g>', CLIP),
    "tekst": svg(f'<g clip-path="url(#tekst)">{VEKTOR.format(kontury([0], KREM))}</g>{VEKTOR.format(kontury([17, 18, 19, 20], KREM))}', CLIP),
    "nozh": svg(VEKTOR.format(kontury([11, 13], KREM))),
    # хинкали: тесто внутри, кремовый контур и тёмные складки
    "hinkali": svg(VEKTOR.format(f'<path d="{ds[1].split("z")[0]}z" fill="{TESTO}"/>' + kontury([1], KREM) + kontury(range(2, 11), UGOL))),
}

PAPKA.mkdir(parents=True, exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": W, "height": H})
    for imya, s in SLOI.items():
        pg.set_content(f'<body style="margin:0;background:transparent">{s}</body>')
        pg.screenshot(path=str(PAPKA / f"{imya}.png"), omit_background=True)
    # «City» — как на старой иконке: кистевой курсив под «кал»
    pg.set_content('<html><head><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Kaushan+Script&display=block"></head>'
                   f'<body style="margin:0;background:transparent"><div id="c" style="display:inline-block;padding:0 8px;'
                   f'font:{round(54 * MASHTAB)}px \'Kaushan Script\';color:{SHAFRAN};line-height:1.15">City</div></body></html>')
    pg.wait_for_function("document.fonts.ready.then(() => document.fonts.check(\"40px 'Kaushan Script'\"))")
    pg.locator("#c").screenshot(path=str(PAPKA / "city.png"), omit_background=True)
    b.close()

# Нож: «Кафе» вырезано в клинке. Края клинка в этом окне почти прямые: берём верх и низ
# на границах окна и заливаем многоугольник между ними.
nozh = Image.open(PAPKA / "nozh.png").convert("RGBA")
la, lb = (round((v - x0) * MASHTAB) for v in (436, 566))
alfa = nozh.split()[3]


def kraya(x):
    ys = [y for y in range(H) if alfa.getpixel((x, y)) > 128]
    return min(ys), max(ys)


(ta, ba), (tb, bb) = kraya(la), kraya(lb)
maska = Image.new("L", nozh.size, 0)
ImageDraw.Draw(maska).polygon([(la, ta), (lb, tb), (lb, bb), (la, ba)], fill=255)
nozh.paste(Image.new("RGBA", nozh.size, KREM), (0, 0), maska)
nozh.save(PAPKA / "nozh.png")

for imya, fid in BLYUDA.items():
    Image.open(FOTO / f"{fid}.webp").convert("RGBA").resize((480, 480), Image.LANCZOS).save(PAPKA / f"{imya}.webp", quality=80)

city = Image.open(PAPKA / "city.png")
json.dump({"okno": OKNO, "mashtab": MASHTAB, "razmer": [W, H], "city": list(city.size), "blyuda": list(BLYUDA)},
          open(PAPKA / "sloi.json", "w"), indent=1)
print("ok", W, H, "city", city.size)

# Иконка приложения: тот же логотип на угле, что и в заставке (1024 — для значка, 512 — для карточки магазина).
def ikonka(storona, dolya):
    holst = Image.new("RGBA", (storona, storona), STAL)
    fon = Image.radial_gradient("L").resize((storona, storona))  # 0 в центре, 255 к краям
    holst.paste(Image.new("RGBA", holst.size, STAL_SVET), (0, 0), fon.point(lambda v: 255 - v))
    # шлифовка: шум, вытянутый по горизонтали
    shum = Image.effect_noise((max(1, storona // 16), storona), 40).resize((storona, storona), Image.BILINEAR)
    holst.paste(Image.new("RGBA", holst.size, "#FFFFFF"), (0, 0), shum.point(lambda v: max(0, v - 128) // 3))
    holst.paste(Image.new("RGBA", holst.size, "#8A9096"), (0, 0), shum.point(lambda v: max(0, 128 - v) // 4))
    logo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for imya in ("ramka", "vilka", "nozh", "tekst", "hinkali"):
        logo.alpha_composite(Image.open(PAPKA / f"{imya}.png"))
    logo.alpha_composite(city, (round((CITY[0] - x0) * MASHTAB), round((CITY[1] - y0) * MASHTAB)))
    w = round(storona * dolya); h = round(w * H / W)
    holst.alpha_composite(logo.resize((w, h), Image.LANCZOS), ((storona - w) // 2, (storona - h) // 2))
    return holst


ikonka(1024, 0.6).save("hinkali/ikonka_1024.png")
ikonka(512, 0.84).convert("RGB").save("hinkali/ikonka_magazin_512.png")

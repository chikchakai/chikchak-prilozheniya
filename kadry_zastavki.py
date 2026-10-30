"""Полоса кадров заставки: py -X utf8 kadry_zastavki.py <out.png> [t1 t2 ...] [--vyhod 1.75]"""
import pathlib
import sys

from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

out = sys.argv[1]
args = sys.argv[2:]
vyhod = None
if '--vyhod' in args:
    i = args.index('--vyhod'); vyhod = args[i + 1]; args = args[:i] + args[i + 2:]
ts = [float(x) for x in args] or [0.1, 0.25, 0.4, 0.55, 0.7, 0.85, 1.0, 1.15, 1.3, 1.5, 1.75, 2.0]
url = pathlib.Path('hinkali/www/index.html').resolve().as_uri()
kadry = []
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 390, 'height': 844}, device_scale_factor=1)
    for t in ts:
        pg.goto(f'{url}?t={t}' + (f'&vyhod={vyhod}' if vyhod else ''))
        pg.wait_for_selector('body[data-kadr]')
        f = f'{out}.{t}.png'; pg.screenshot(path=f); kadry.append((t, Image.open(f)))
    b.close()
w, h = 195, 422
list_ = Image.new('RGB', (w * min(6, len(kadry)), h * ((len(kadry) + 5) // 6)), 'white')
d = ImageDraw.Draw(list_)
for i, (t, im) in enumerate(kadry):
    x, y = (i % 6) * w, (i // 6) * h
    list_.paste(im.resize((w, h)), (x, y)); d.text((x + 4, y + 4), f'{t:.2f}s', fill='white')
list_.save(out)
for t, _ in kadry:
    pathlib.Path(f'{out}.{t}.png').unlink()

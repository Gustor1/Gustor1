"""Génère assets/banner.svg : Shanghai la nuit, fenêtres animées.

Le texte est converti en contours (paths) pour que la bannière s'affiche
à l'identique partout, même sans police chinoise installée.

Usage :  python tools/build_banner.py
Prérequis : fontTools (pip install fonttools) et les polices Windows
Georgia, Consolas et KaiTi (simkai.ttf).
"""
import random
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

FONTS = Path("C:/Windows/Fonts")
OUT = Path(__file__).resolve().parent.parent / "assets"
_cache = {}


def font(name):
    if name not in _cache:
        _cache[name] = TTFont(FONTS / name)
    return _cache[name]


def text_path(fname, text, size, x, y, tracking=0.0, anchor="start"):
    """Retourne (d, largeur) pour `text` posé sur la ligne de base y."""
    f = font(fname)
    cmap, gs, hmtx = f.getBestCmap(), f.getGlyphSet(), f["hmtx"]
    scale = size / f["head"].unitsPerEm
    adv = [hmtx[cmap[ord(c)]][0] * scale + tracking for c in text]
    width = sum(adv) - (tracking if text else 0)
    if anchor == "end":
        x -= width
    elif anchor == "middle":
        x -= width / 2
    pen = SVGPathPen(gs, ntos=lambda v: ("%.1f" % v).rstrip("0").rstrip("."))
    for c, a in zip(text, adv):
        gs[cmap[ord(c)]].draw(TransformPen(pen, (scale, 0, 0, -scale, x, y)))
        x += a
    return pen.getCommands(), width


W, H = 1200, 440
GROUND = 344  # ligne du quai ; en dessous, le Huangpu
C = dict(sky1="#05070F", sky2="#101A2E", river="#04060C", ink="#F3EEE4",
         muted="#8B95A8", body="#0A1120", edge="#33425E", red="#D9412B",
         pink="#FF4FA3", cyan="#7FD6FF")

# Géométrie de la skyline (repère d'origine, sol à y=288), mise à l'échelle ensuite.
BUILDINGS = [
    "M716 288V262H742V288Z", "M748 288V270H768V288Z", "M832 288V258H858V288Z",
    # Jin Mao
    "M872 288V226H876V198H879V172H882V150H885V134H888V112L890 92L892 112V134"
    "H895V150H898V172H901V198H904V226H908V288Z",
    # SWFC
    "M924 288V108Q924 94 938 92H958Q970 94 970 108V288Z",
    # Shanghai Tower
    "M986 288Q988 160 1004 62L1008 54L1012 62Q1026 160 1030 288Z",
    "M1044 288V246H1068V288Z", "M1074 288V266H1096V288Z",
    "M1104 288V254H1122V288Z",
]
TOWER = BUILDINGS[5]
PEARL_LINES = ["M786 288L795 256", "M814 288L805 256", "M800 288V256",
               "M796 216V162", "M804 216V162", "M800 138V117", "M800 107V70"]
SPHERES = [(800, 236, 20), (800, 150, 12), (800, 112, 5)]
# Zones de fenêtres (x1, y1, x2, y2)
WINDOW_ZONES = [
    (719, 265, 739, 286), (751, 273, 765, 286), (835, 261, 855, 286),
    (875, 229, 905, 286), (878, 201, 902, 225), (881, 175, 899, 197), (884, 153, 896, 171),
    (927, 122, 967, 286),
    (990, 240, 1026, 286), (992, 190, 1024, 236), (995, 140, 1021, 186),
    (998, 102, 1018, 136), (1002, 76, 1014, 98),
    (1047, 249, 1065, 286), (1077, 269, 1093, 286), (1107, 257, 1119, 286),
]
CITY_TF = f"translate(606 {GROUND}) scale(1.4) translate(-716 -288)"


def windows(rng):
    out = []
    for x1, y1, x2, y2 in WINDOW_ZONES:
        y = y2 - 3.2
        while y >= y1:
            x = x1
            while x + 2.6 <= x2:
                if rng.random() < 0.5:
                    col = rng.choice(["#FFD27A"] * 5 + ["#FFE9B0"] * 3 + ["#9FD8FF"] * 2)
                    # la ville s'allume de gauche à droite, du bas vers le haut
                    d = 0.5 + (x - 716) / 410 * 2.2 + (288 - y) / 240 * 0.8 + rng.random() * 0.6
                    r = rng.random()
                    if r < 0.12:
                        cls, st = "w f", f"animation-delay:{d:.2f}s,{d + rng.uniform(1, 9):.2f}s"
                    elif r < 0.22:
                        cls = "w t"
                        st = (f"animation-delay:{d:.2f}s,{d + rng.uniform(2, 14):.2f}s;"
                              f"animation-duration:.6s,{rng.uniform(10, 22):.1f}s")
                    else:
                        cls, st = "w", f"animation-delay:{d:.2f}s"
                    out.append(f'<rect class="{cls}" style="{st}" x="{x:.1f}" y="{y:.1f}" '
                               f'width="2.6" height="2" fill="{col}"/>')
                x += 4.4
            y -= 4.6
    return "\n      ".join(out)


def stars(rng):
    out = []
    for _ in range(70):
        x, y = rng.uniform(20, 1180), rng.uniform(14, 230)
        if x < 600 and 60 < y < 320:  # pas d'étoiles derrière le texte
            continue
        r = rng.choice([0.6, 0.8, 1, 1.3])
        out.append(f'<circle class="s" style="animation-delay:{rng.uniform(0, 6):.1f}s;'
                   f'animation-duration:{rng.uniform(3, 7):.1f}s" cx="{x:.0f}" cy="{y:.0f}" r="{r}"/>')
    return "\n    ".join(out)


def build():
    rng = random.Random(2027)
    label_d, _ = text_path("consola.ttf", "ENGINEERING APPRENTICE · UTBM × ÉLECTRICITÉ DE STRASBOURG",
                           12, 66, 108, tracking=1.6)
    name_d, name_w = text_path("georgia.ttf", "Eliott", 112, 62, 214)
    tag_d, _ = text_path("georgiai.ttf", "AI agents, web apps & local-first tools.", 28, 66, 266)
    fr_d, _ = text_path("georgia.ttf", "Agents IA, apps web et outils local-first.", 18, 66, 298)
    left_d, _ = text_path("consola.ttf", "BELFORT / STRASBOURG  48.58°N 7.75°E", 12, 66, 418, tracking=1.4)
    right_d, _ = text_path("consola.ttf", "SHANGHAI  31.23°N 121.47°E", 12, 1134, 418, tracking=1.4, anchor="end")
    # Sceau 爱 (ài) : « aimer », et se prononce comme « AI ».
    sx, sy, ss = 62 + name_w + 22, 124, 64
    seal_d, _ = text_path("simkai.ttf", "爱", 50, sx + ss / 2, sy + ss / 2 + 18, anchor="middle")

    bodies = "\n      ".join(f'<path d="{d}"/>' for d in BUILDINGS)
    pearl = "\n      ".join(f'<path d="{d}"/>' for d in PEARL_LINES)
    spheres = "\n      ".join(f'<circle cx="{x}" cy="{y}" r="{r}"/>' for x, y, r in SPHERES)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t d">
  <title id="t">Eliott — engineering apprentice at UTBM and Électricité de Strasbourg</title>
  <desc id="d">AI agents, web apps and local-first tools. A red seal with the character 爱 (ài, love) and the Shanghai skyline at night, its windows lighting up one by one and reflecting in the river.</desc>
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{C['sky1']}"/><stop offset="1" stop-color="{C['sky2']}"/>
    </linearGradient>
    <radialGradient id="haze" cx=".78" cy=".72" r=".5">
      <stop offset="0" stop-color="#3B2A55" stop-opacity=".55"/><stop offset="1" stop-color="#3B2A55" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="scan" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{C['cyan']}" stop-opacity="0"/>
      <stop offset=".5" stop-color="{C['cyan']}" stop-opacity=".75"/>
      <stop offset="1" stop-color="{C['cyan']}" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="fade" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#fff" stop-opacity=".6"/><stop offset=".75" stop-color="#fff" stop-opacity="0"/>
    </linearGradient>
    <mask id="reflMask"><rect x="0" y="{GROUND}" width="{W}" height="{H - GROUND}" fill="url(#fade)"/></mask>
    <clipPath id="towerClip"><path d="{TOWER}"/></clipPath>
    <clipPath id="card"><rect width="{W}" height="{H}" rx="16"/></clipPath>
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="3.5" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="wave" x="0" y="0" width="100%" height="100%">
      <feTurbulence type="fractalNoise" baseFrequency="0.004 0.09" numOctaves="1" seed="7">
        <animate attributeName="baseFrequency" dur="9s" values="0.004 0.09;0.004 0.12;0.004 0.09" repeatCount="indefinite"/>
      </feTurbulence>
      <feDisplacementMap in="SourceGraphic" scale="9"/>
    </filter>
  </defs>
  <style>
    .w {{ opacity: 0; animation: on .6s ease-out forwards; }}
    .w.f {{ animation-name: on, flick; animation-duration: .6s, 7s; animation-iteration-count: 1, infinite; animation-timing-function: ease-out, steps(1); }}
    .w.t {{ animation-name: on, toggle; animation-iteration-count: 1, infinite; animation-timing-function: ease-out, steps(1); }}
    .s {{ animation: twinkle 5s ease-in-out infinite; }}
    .pulse {{ animation: pulse 3.2s ease-in-out infinite; }}
    .blink {{ animation: blink 1.6s steps(1) infinite; }}
    .scan {{ animation: scan 4.5s cubic-bezier(.5,0,.5,1) 3s infinite; transform: translateY(300px); }}
    .ripple {{ animation: ripple 6s linear infinite; }}
    .fadein {{ opacity: 0; animation: on 1.4s ease 2.8s forwards; }}
    @keyframes on {{ to {{ opacity: 1; }} }}
    @keyframes flick {{ 0%, 88%, 91%, 94%, 100% {{ opacity: 1; }} 89%, 92% {{ opacity: .15; }} }}
    @keyframes toggle {{ 0%, 55% {{ opacity: 1; }} 56%, 100% {{ opacity: .08; }} }}
    @keyframes twinkle {{ 0%, 100% {{ opacity: .25; }} 50% {{ opacity: .95; }} }}
    @keyframes pulse {{ 0%, 100% {{ opacity: .55; }} 50% {{ opacity: 1; }} }}
    @keyframes blink {{ 0% {{ opacity: 1; }} 50% {{ opacity: .1; }} }}
    @keyframes scan {{ from {{ transform: translateY(300px); }} to {{ transform: translateY(-40px); }} }}
    @keyframes ripple {{ from {{ transform: translateX(0); }} to {{ transform: translateX(-60px); }} }}
    @media (prefers-reduced-motion: reduce) {{
      .w, .s, .pulse, .blink, .ripple, .fadein {{ animation: none !important; opacity: 1; }}
      .scan {{ animation: none; opacity: 0; }}
    }}
  </style>

  <g clip-path="url(#card)">
    <rect width="{W}" height="{GROUND}" fill="url(#sky)"/>
    <rect width="{W}" height="{GROUND}" fill="url(#haze)"/>
    <rect y="{GROUND}" width="{W}" height="{H - GROUND}" fill="{C['river']}"/>
    <g fill="#DCE6FF">
    {stars(rng)}
    </g>
    <circle class="fadein" cx="560" cy="58" r="17" fill="#F4E7C8" filter="url(#glow)" opacity=".9"/>

    <g id="city" transform="{CITY_TF}">
      <g fill="{C['body']}" stroke="{C['edge']}" stroke-width="1" stroke-linejoin="round">
      {bodies}
      </g>
      <g clip-path="url(#towerClip)"><rect class="scan" x="980" y="0" width="56" height="46" fill="url(#scan)"/></g>
      <path d="M996 288Q1001 170 1008 60" fill="none" stroke="{C['edge']}" stroke-width=".8"/>
      <path d="M936 104H958L955 118H939Z" class="pulse" fill="{C['cyan']}" opacity=".7" filter="url(#glow)"/>
      <g fill="none" stroke="#5A6A88" stroke-width="1.4" stroke-linecap="round">
      {pearl}
      </g>
      <g class="pulse" fill="{C['pink']}" stroke="#FF9ACB" stroke-width=".8" filter="url(#glow)">
      {spheres}
      </g>
      {windows(rng)}
      <circle class="blink" cx="1008" cy="54" r="1.8" fill="#FF3B3B" filter="url(#glow)"/>
      <circle class="blink" style="animation-delay:.8s" cx="890" cy="92" r="1.5" fill="#FF3B3B" filter="url(#glow)"/>
      <circle class="blink" style="animation-delay:.4s" cx="800" cy="70" r="1.5" fill="#FF3B3B" filter="url(#glow)"/>
    </g>

    <g mask="url(#reflMask)" filter="url(#wave)">
      <use xlink:href="#city" href="#city" transform="translate(0 {2 * GROUND}) scale(1 -1)"/>
    </g>
    <g class="ripple" stroke="#7FA0D8" stroke-opacity=".18" stroke-width="1" stroke-dasharray="14 46">
      <path d="M560 358H1260"/><path d="M600 372H1260" stroke-dashoffset="20"/><path d="M580 388H1260" stroke-dashoffset="35"/>
    </g>
    <path d="M0 {GROUND}H{W}" stroke="#1E2A40" stroke-width="1.2"/>

    <path d="{label_d}" fill="{C['muted']}"/>
    <path d="{name_d}" fill="{C['ink']}"/>
    <g transform="rotate(-4 {sx + ss / 2} {sy + ss / 2})">
      <rect x="{sx}" y="{sy}" width="{ss}" height="{ss}" rx="7" fill="{C['red']}"/>
      <rect x="{sx + 4}" y="{sy + 4}" width="{ss - 8}" height="{ss - 8}" rx="4" fill="none" stroke="{C['sky1']}" stroke-width="1.4" opacity=".5"/>
      <path d="{seal_d}" fill="{C['sky1']}"/>
    </g>
    <path d="{tag_d}" fill="{C['ink']}"/>
    <path d="{fr_d}" fill="{C['muted']}"/>
    <path d="{left_d}" fill="{C['muted']}"/>
    <path d="{right_d}" fill="{C['muted']}"/>
  </g>
</svg>
"""


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    svg = build()
    (OUT / "banner.svg").write_text(svg, encoding="utf-8")
    print("ok", OUT / "banner.svg", len(svg) // 1024, "KB")

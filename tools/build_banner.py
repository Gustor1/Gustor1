"""Génère assets/banner-light.svg et assets/banner-dark.svg.

Le texte est converti en contours (paths) pour que la bannière s'affiche
à l'identique partout, même sans police chinoise installée.

Usage :  python tools/build_banner.py
Prérequis : fontTools (pip install fonttools) et les polices Windows
Georgia, Consolas et KaiTi (simkai.ttf).
"""
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
    cmap = f.getBestCmap()
    gs = f.getGlyphSet()
    hmtx = f["hmtx"]
    scale = size / f["head"].unitsPerEm
    advances = [hmtx[cmap[ord(c)]][0] * scale + tracking for c in text]
    width = sum(advances) - (tracking if text else 0)
    if anchor == "end":
        x -= width
    elif anchor == "middle":
        x -= width / 2
    pen = SVGPathPen(gs, ntos=lambda v: ("%.1f" % v).rstrip("0").rstrip("."))
    cx = x
    for c, adv in zip(text, advances):
        gname = cmap[ord(c)]
        tp = TransformPen(pen, (scale, 0, 0, -scale, cx, y))
        gs[gname].draw(tp)
        cx += adv
    return pen.getCommands(), width


THEMES = {
    "light": dict(bg="#F7F4EE", ink="#1F2328", muted="#6B6F76",
                  line="#D9D3C7", sky="#3A3F46", red="#C23B22", seal_ink="#F7F4EE"),
    "dark": dict(bg="#0E1116", ink="#ECE7DD", muted="#8B919A",
                 line="#2B3038", sky="#AEB4BD", red="#E0533A", seal_ink="#0E1116"),
}

W, H, GROUND = 1200, 340, 288

# Skyline de Pudong, trait unique : Perle de l'Orient, Jin Mao, SWFC, Shanghai Tower.
SKYLINE = [
    # petits immeubles à gauche
    "M716 288V262H742V288", "M748 288V270H768V288",
    # Perle de l'Orient (centre x=800)
    "M786 288L795 256", "M814 288L805 256", "M800 288V256",
    "M796 216V162", "M804 216V162", "M800 138V117", "M800 107V70",
    # bloc bas
    "M832 288V258H858V288",
    # Jin Mao (centre x=890), silhouette en pagode
    "M872 288V226H876V198H879V172H882V150H885V134H888V112L890 92L892 112V134"
    "H895V150H898V172H901V198H904V226H908V288",
    # SWFC « décapsuleur »
    "M924 288V108Q924 94 938 92H958Q970 94 970 108V288",
    "M936 104H958L955 118H939Z",
    # Shanghai Tower, la plus haute, en torsade
    "M986 288Q988 160 1004 62L1008 54L1012 62Q1026 160 1030 288",
    "M996 288Q1001 170 1008 60",
    # immeubles à droite
    "M1044 288V246H1068V288", "M1074 288V266H1096V288",
]
SPHERES = [(800, 236, 20), (800, 150, 12), (800, 112, 5)]


def build(theme):
    t = THEMES[theme]
    name_d, name_w = text_path("georgia.ttf", "Eliott", 104, 64, 186)
    label_d, _ = text_path("consola.ttf", "ENGINEERING STUDENT · UTBM", 15, 66, 80, tracking=3.2)
    tag_d, _ = text_path("georgiai.ttf", "AI agents, web apps & local-first tools.", 27, 66, 236)
    fr_d, _ = text_path("georgia.ttf", "Agents IA, apps web et outils local-first.", 18, 66, 268)
    left_d, _ = text_path("consola.ttf", "BELFORT  47.64°N 6.86°E", 12.5, 64, 316, tracking=1.4)
    right_d, rw = text_path("consola.ttf", "31.23°N 121.47°E", 12.5, 1136, 316, tracking=1.4, anchor="end")
    sh_d, _ = text_path("simkai.ttf", "上海", 15, 1136 - rw - 12, 317, anchor="end")

    # Sceau 艾 (ài) : se lit « AI », et sonne comme 爱 (aimer).
    sx, sy, ss = 64 + name_w + 22, 100, 62
    seal_d, _ = text_path("simkai.ttf", "艾", 48, sx + ss / 2, sy + ss / 2 + 17, anchor="middle")

    sky = "\n    ".join(f'<path pathLength="1" d="{d}"/>' for d in SKYLINE)
    spheres = "\n    ".join(f'<circle pathLength="1" cx="{x}" cy="{y}" r="{r}"/>' for x, y, r in SPHERES)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t d">
  <title id="t">Eliott — engineering student at UTBM</title>
  <desc id="d">AI agents, web apps and local-first tools. A red seal with the character 艾 (ài) and a line drawing of the Shanghai skyline.</desc>
  <style>
    .sky {{ stroke-dasharray: 1; stroke-dashoffset: 1; animation: draw 2.6s cubic-bezier(.6,.05,.25,1) .3s forwards; }}
    .fade {{ opacity: 0; animation: fade 1.2s ease 1.6s forwards; }}
    @keyframes draw {{ to {{ stroke-dashoffset: 0; }} }}
    @keyframes fade {{ to {{ opacity: 1; }} }}
    @media (prefers-reduced-motion: reduce) {{
      .sky {{ animation: none; stroke-dashoffset: 0; }}
      .fade {{ animation: none; opacity: 1; }}
    }}
  </style>
  <rect width="{W}" height="{H}" rx="14" fill="{t['bg']}"/>

  <path d="{label_d}" fill="{t['muted']}"/>
  <path d="{name_d}" fill="{t['ink']}"/>
  <g transform="rotate(-4 {sx + ss / 2} {sy + ss / 2})">
    <rect x="{sx}" y="{sy}" width="{ss}" height="{ss}" rx="7" fill="{t['red']}"/>
    <rect x="{sx + 4}" y="{sy + 4}" width="{ss - 8}" height="{ss - 8}" rx="4" fill="none" stroke="{t['seal_ink']}" stroke-width="1.4" opacity=".55"/>
    <path d="{seal_d}" fill="{t['seal_ink']}"/>
  </g>
  <path d="{tag_d}" fill="{t['ink']}"/>
  <path d="{fr_d}" fill="{t['muted']}"/>

  <circle class="fade" cx="1074" cy="120" r="19" fill="none" stroke="{t['red']}" stroke-width="1.6"/>
  <g fill="none" stroke="{t['sky']}" stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round">
    <g class="sky">
    {sky}
    {spheres}
    </g>
  </g>

  <path d="M64 {GROUND}H1136" stroke="{t['line']}" stroke-width="1.2"/>
  <path d="{left_d}" fill="{t['muted']}"/>
  <path d="{sh_d}" fill="{t['muted']}"/>
  <path d="{right_d}" fill="{t['muted']}"/>
</svg>
"""


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for th in THEMES:
        svg = build(th)
        (OUT / f"banner-{th}.svg").write_text(svg, encoding="utf-8")
        print("ok", OUT / f"banner-{th}.svg", len(svg) // 1024, "KB")

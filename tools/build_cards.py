"""Génère assets/card-*.svg : les projets en cartes de nuit, même DA que la bannière.

Usage :  python tools/build_cards.py
Mêmes prérequis que build_banner.py (fontTools + polices Windows, dont Segoe UI).
"""
import math
import random
from pathlib import Path

from build_banner import font, text_path

OUT = Path(__file__).resolve().parent.parent / "assets"
LANG = "en"


def T(en, fr):
    return fr if LANG == "fr" else en


W, H = 1200, 340
C = dict(sky1="#05070F", sky2="#101A2E", ink="#F3EEE4", body="#C5CCD8", muted="#8B95A8",
         edge="#22304A", pill="#0E172A", red="#D9412B", pink="#FF4FA3", cyan="#7FD6FF",
         gold="#FFD27A", coral="#FF6B4A")


def width(fname, text, size):
    f = font(fname)
    cmap, hmtx = f.getBestCmap(), f["hmtx"]
    return sum(hmtx[cmap[ord(c)]][0] for c in text) * size / f["head"].unitsPerEm


def wrap(fname, text, size, maxw):
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if width(fname, trial, size) > maxw and cur:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    return lines + [cur]


def tags(items, x, y):
    out = []
    for t in items:
        d, w = text_path("consola.ttf", t, 13, x + 12, y + 18)
        out.append(f'<rect x="{x}" y="{y}" width="{w + 24:.1f}" height="26" rx="13" fill="{C["pill"]}" stroke="#2E3D5C"/>'
                   f'<path d="{d}" fill="{C["body"]}"/>')
        x += w + 24 + 8
    return "".join(out)


def card(num, label, title, desc, fr, tag_list, art, art_css, desc_w=600):
    label_d, _ = text_path("consola.ttf", f"{num} — {label}", 12, 56, 62, tracking=1.6)
    title_d, _ = text_path("georgia.ttf", title, 44, 54, 114)
    body = []
    y = 156
    for line in wrap("segoeui.ttf", desc, 18.5, desc_w):
        d, _ = text_path("segoeui.ttf", line, 18.5, 56, y)
        body.append(f'<path d="{d}" fill="{C["body"]}"/>')
        y += 27
    fr_d = text_path("georgiai.ttf", fr, 14.5, 56, y + 6)[0] if fr else ""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{title}: {desc}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{C['sky1']}"/><stop offset="1" stop-color="{C['sky2']}"/></linearGradient>
    <radialGradient id="haze" cx=".8" cy=".55" r=".5"><stop offset="0" stop-color="#3B2A55" stop-opacity=".45"/><stop offset="1" stop-color="#3B2A55" stop-opacity="0"/></radialGradient>
    <filter id="glow" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="3" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  </defs>
  <style>
    .s {{ animation: tw 5s ease-in-out infinite; }}
    @keyframes tw {{ 0%, 100% {{ opacity: .2; }} 50% {{ opacity: .9; }} }}
    {art_css}
    @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
  </style>
  <rect width="{W}" height="{H}" rx="16" fill="url(#bg)"/>
  <rect width="{W}" height="{H}" rx="16" fill="url(#haze)"/>
  {stars()}
  <rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="15.5" fill="none" stroke="{C['edge']}"/>
  <path d="{label_d}" fill="{C['muted']}"/>
  <path d="{title_d}" fill="{C['ink']}"/>
  {''.join(body)}
  <path d="{fr_d}" fill="{C['muted']}"/>
  {tags(tag_list, 56, 284)}
  {art}
</svg>
"""


def stars():
    rng = random.Random(len(OUT.as_posix()))
    out = []
    for _ in range(26):
        x, y = rng.uniform(700, 1180), rng.uniform(14, 326)
        out.append(f'<circle class="s" style="animation-delay:{rng.uniform(0, 5):.1f}s" cx="{x:.0f}" cy="{y:.0f}" '
                   f'r="{rng.choice([.6, .8, 1])}" fill="#DCE6FF"/>')
    return "".join(out)


# ---------- 01 · réseau d'agents ----------
def art_agents():
    cx, cy = 935, 170
    names = T(["flights", "stays", "budget", "routes", "food", "safety"],
              ["vols", "hôtels", "budget", "trajets", "cuisine", "sécurité"])
    out, css = [], []
    for i, n in enumerate(names):
        a = -math.pi / 2 + i * math.tau / 6
        x, y = cx + 150 * math.cos(a), cy + 110 * math.sin(a)
        out.append(f'<path d="M{cx} {cy}L{x:.1f} {y:.1f}" stroke="#2A3A5A" stroke-width="1.2"/>')
        out.append(f'<path class="flow" style="animation-delay:{i * .55:.2f}s" d="M{cx} {cy}L{x:.1f} {y:.1f}" '
                   f'stroke="{C["cyan"]}" stroke-width="2" stroke-linecap="round" pathLength="100" stroke-dasharray="8 92"/>')
        out.append(f'<circle class="node" style="animation-delay:{i * .55 + .5:.2f}s" cx="{x:.1f}" cy="{y:.1f}" r="15" '
                   f'fill="#0E172A" stroke="{C["cyan"]}" stroke-width="1.4"/>')
        out.append(f'<circle class="core" style="animation-delay:{i * .55 + .5:.2f}s" cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="{C["gold"]}" filter="url(#glow)"/>')
        lx = x + (24 if math.cos(a) > 0.2 else -24 if math.cos(a) < -0.2 else 0)
        ly = y + (5 if abs(math.cos(a)) > 0.2 else (-24 if math.sin(a) < 0 else 32))
        anchor = "start" if math.cos(a) > 0.2 else "end" if math.cos(a) < -0.2 else "middle"
        d, _ = text_path("consola.ttf", n, 12, lx, ly, anchor=anchor)
        out.append(f'<path d="{d}" fill="{C["muted"]}"/>')
    out.append(f'<circle class="halo" cx="{cx}" cy="{cy}" r="34" fill="none" stroke="{C["pink"]}" stroke-width="1.2"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="24" fill="#1A1030" stroke="{C["pink"]}" stroke-width="1.6" filter="url(#glow)"/>')
    d, _ = text_path("consola.ttf", "MCP", 13, cx, cy + 4.5, anchor="middle")
    out.append(f'<path d="{d}" fill="{C["ink"]}"/>')
    css = """.flow { animation: flow 3.3s linear infinite; }
    .node { animation: node 3.3s ease-in-out infinite; }
    .core { opacity: .25; animation: core 3.3s ease-in-out infinite; }
    .halo { transform-origin: 935px 170px; animation: halo 2.6s ease-out infinite; }
    @keyframes flow { from { stroke-dashoffset: 100; } to { stroke-dashoffset: 0; } }
    @keyframes node { 0%, 100% { stroke-opacity: .35; } 15% { stroke-opacity: 1; } }
    @keyframes core { 0%, 100% { opacity: .25; } 15% { opacity: 1; } }
    @keyframes halo { from { transform: scale(.7); opacity: .9; } to { transform: scale(1.6); opacity: 0; } }"""
    return "".join(out), css


# ---------- 02 · itinéraire en Chine ----------
CITIES = [("Shenzhen", 114.06, 22.54), ("Yangshuo", 110.49, 24.78), ("Chongqing", 106.55, 29.56),
          ("Chengdu", 104.07, 30.67), ("Shanghai", 121.47, 31.23)]


def proj(lon, lat):
    return 745 + (lon - 102) / 21 * 390, 300 - (lat - 20.5) / 12 * 240


def art_route():
    pts = [proj(lon, lat) for _, lon, lat in CITIES]
    out = []
    # quadrillage façon carte
    for gx in range(760, 1150, 40):
        out.append(f'<path d="M{gx} 40V310" stroke="#16213A" stroke-width="1"/>')
    for gy in range(50, 320, 40):
        out.append(f'<path d="M730 {gy}H1160" stroke="#16213A" stroke-width="1"/>')
    ground = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts[:4])
    out.append(f'<path class="route" d="{ground}" fill="none" stroke="{C["gold"]}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" pathLength="1"/>')
    (x1, y1), (x2, y2) = pts[3], pts[4]
    arc = f"M{x1:.1f} {y1:.1f}Q{(x1 + x2) / 2:.1f} {min(y1, y2) - 90:.1f} {x2:.1f} {y2:.1f}"
    out.append(f'<path class="flight" d="{arc}" fill="none" stroke="{C["cyan"]}" stroke-width="1.8" stroke-dasharray="2 7" stroke-linecap="round"/>')
    for i, ((name, _, _), (x, y)) in enumerate(zip(CITIES, pts)):
        dl = [0.1, 0.7, 1.4, 2.0, 3.2][i]
        out.append(f'<g class="pin" style="animation-delay:{dl}s">'
                   f'<circle cx="{x:.1f}" cy="{y:.1f}" r="9" fill="{C["red"]}" opacity=".25"/>'
                   f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="{C["red"]}" filter="url(#glow)"/>')
        dx, anchor = {"Shenzhen": (12, "start"), "Yangshuo": (-12, "end"), "Chongqing": (12, "start"),
                      "Chengdu": (-12, "end"), "Shanghai": (-12, "end")}[name]
        dy = 22 if name == "Shanghai" else 4
        d, _ = text_path("consola.ttf", name.upper(), 11, x + dx, y + dy, tracking=1.2, anchor=anchor)
        out.append(f'<path d="{d}" fill="{C["body"]}"/></g>')
    css = """.route { stroke-dasharray: 1; stroke-dashoffset: 1; animation: draw 8s ease-in-out infinite; }
    .flight { opacity: 0; animation: fly 8s ease-in-out infinite; }
    .pin { opacity: 0; animation: pin 8s ease-out infinite; }
    @keyframes draw { 0% { stroke-dashoffset: 1; } 30%, 85% { stroke-dashoffset: 0; opacity: 1; } 95%, 100% { stroke-dashoffset: 0; opacity: 0; } }
    @keyframes fly { 0%, 36% { opacity: 0; stroke-dashoffset: 40; } 48%, 85% { opacity: 1; stroke-dashoffset: 0; } 95%, 100% { opacity: 0; } }
    @keyframes pin { 0% { opacity: 0; } 4%, 85% { opacity: 1; } 95%, 100% { opacity: 0; } }"""
    return "".join(out), css


# ---------- 03 · onde sonore et bruit ----------
def art_wave():
    rng = random.Random(3)
    out = []
    stat_d, sw = text_path("georgia.ttf", "+11 %", 58, 1140, 104, anchor="end")
    out.append(f'<path d="{stat_d}" fill="{C["coral"]}"/>')
    cap_d, _ = text_path("consola.ttf", T("WORD ERROR RATE · WIENER IN REAL NOISE", "TAUX D'ERREUR · WIENER EN BRUIT RÉEL"), 11, 1140, 128, tracking=1.2, anchor="end")
    out.append(f'<path d="{cap_d}" fill="{C["muted"]}"/>')
    n, x0, x1, mid = 64, 740, 1140, 230
    step = (x1 - x0) / n
    for i in range(n):
        t = i / n
        env = 0.25 + 0.75 * abs(math.sin(t * math.pi * 3.2)) * (0.6 + 0.4 * math.sin(t * 9))
        h = 8 + 70 * env * rng.uniform(0.6, 1)
        noisy = i < n / 2
        col = "#5B6B8C" if noisy else C["cyan"]
        x = x0 + i * step
        out.append(f'<rect class="bar" style="animation-delay:{-rng.uniform(0, 1.4):.2f}s;animation-duration:{rng.uniform(.9, 1.6):.2f}s" '
                   f'x="{x:.1f}" y="{mid - h / 2:.1f}" width="{step * .55:.1f}" height="{h:.1f}" rx="1.5" fill="{col}"/>')
        if noisy:
            for _ in range(2):
                out.append(f'<circle class="grain" style="animation-delay:{-rng.uniform(0, 1):.2f}s" cx="{x + rng.uniform(-2, 4):.1f}" '
                           f'cy="{mid + rng.uniform(-45, 45):.1f}" r=".9" fill="#8B95A8"/>')
    for lbl, xx, anchor in [(T("NOISY INPUT", "ENTRÉE BRUITÉE"), x0, "start"), (T("ROUTED + FUSED", "ROUTÉ + FUSIONNÉ"), x1, "end")]:
        d, _ = text_path("consola.ttf", lbl, 11, xx, 300, tracking=1.2, anchor=anchor)
        out.append(f'<path d="{d}" fill="{C["muted"]}"/>')
    out.append(f'<path class="scanline" d="M{x0} 175V285" stroke="{C["pink"]}" stroke-width="1.5" filter="url(#glow)"/>')
    css = """.bar { transform-box: fill-box; transform-origin: center; animation: eq 1.2s ease-in-out infinite alternate; }
    .grain { animation: grain .7s steps(2) infinite; }
    .scanline { animation: scan 5s ease-in-out infinite; }
    @keyframes eq { from { transform: scaleY(.35); } to { transform: scaleY(1); } }
    @keyframes grain { 0% { opacity: .9; } 50% { opacity: .1; } }
    @keyframes scan { 0% { transform: translateX(0); opacity: 0; } 8% { opacity: 1; } 92% { opacity: 1; } 100% { transform: translateX(400px); opacity: 0; } }"""
    return "".join(out), css


CARDS = {
    "card-travel-agent": dict(
        label_fr='AGENTS IA · OPEN SOURCE',
        title_fr='Ultimate Travel Agent',
        desc_fr='Une boîte à outils open-source multi-agents pour planifier des voyages vérifiables : 14 skills, 12 agents spécialisés et 9 workflows sur un cœur Python déterministe, avec un serveur MCP en option. Chaque recommandation est sourcée, avec un budget vérifiable.',
        num="01", label="AI AGENTS · OPEN SOURCE", title="Ultimate Travel Agent",
        desc="An open-source multi-agent toolkit that plans trips you can actually check: 14 skills, "
             "12 specialist agents and 9 workflows on a deterministic Python core, with an optional MCP "
             "server. Every recommendation comes with sources and a verifiable budget.",
        tag_list=["Python", "MCP", "Agent Skills", "multi-agent", "local-first"], art=art_agents),
    "card-detours": dict(
        label_fr='APPLI WEB · EN LIGNE',
        title_fr='Détours',
        desc_fr="Une appli de carnet de voyage née d'un voyage en Chine prévu en 2027 : planning jour par jour, cartes, réservations, budget CNY/EUR et phrases en chinois à copier. Elle marche hors-ligne sans compte, et une bêta Supabase ajoute Google, la synchro et les carnets partagés.",
        num="02", label="WEB APP · LIVE", title="Détours",
        desc="A travel notebook app born from a 2027 trip across China: day plans, maps, bookings, "
             "a CNY/EUR budget and Chinese phrases to copy. It works offline with no account, and a "
             "Supabase beta adds Google sign-in, sync and shared notebooks.",
        tag_list=["React", "TypeScript", "Vite", "Leaflet", "Supabase", "PWA"], art=art_route),
    "card-speech": dict(
        label_fr='MACHINE LEARNING · SHANGHAI UNIVERSITY × UTBM',
        title_fr='Speech under noise',
        desc_fr="Le débruitage classique aide-t-il les modèles de parole modernes ? Pas en bruit réel : le filtre de Wiener augmente l'erreur de Whisper de 8 à 11 % et efface les indices d'émotion. Notre réponse, à 6 : routage parallèle et fusion multimodale, +20 % sur l'émotion.",
        num="03", label="MACHINE LEARNING · SHANGHAI UNIVERSITY × UTBM", title="Speech under noise",
        desc="Does classical denoising help modern speech models? Not in real noise: Wiener filtering "
             "raises Whisper's error rate by 8 to 11 % and erases emotion cues. Our answer, built by a "
             "team of 6: parallel routing and multimodal fusion, +20 % emotion accuracy.",
        tag_list=["Python", "Whisper", "Wav2Vec2", "DistilBERT", "DSP"], art=art_wave),
}

# ---------- 04 · outils de révision (captures du repo study-tools) ----------
STUDY_TOOLS = [("bd70-exercice", "SQL TRAINER"), ("sr71-simulateur", "CISCO IOS SIMULATOR"),
               ("sr71-cablage", "CABLING LAB"), ("qcm", "438-CARD QUIZ"),
               ("java-accueil", "JAVA LAB TRAINER"), ("techtalk", "ENGLISH WORKSHOP")]
STUDY_FR = ["ENTRAÎNEUR SQL", "SIMULATEUR CISCO IOS", "LABO DE CÂBLAGE", "QUIZ DE 438 CARTES",
            "ENTRAÎNEUR TP JAVA", "ATELIER D'ANGLAIS"]
RAW = "https://raw.githubusercontent.com/Gustor1/study-tools/main/img/"


import functools


@functools.lru_cache(maxsize=None)
def thumb(name, size, quality):
    import base64
    import io
    import urllib.request
    from PIL import Image
    with urllib.request.urlopen(RAW + name + ".webp", timeout=30) as r:
        im = Image.open(io.BytesIO(r.read())).convert("RGB")
    im = im.resize(size, Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "WEBP", quality=quality, method=6)
    return "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()


def art_study():
    n, slot = len(STUDY_TOOLS), 3
    total = n * slot
    lx, ly, lw, lh = 742, 58, 352, 220   # écran du portable
    px, py, pw, ph = 1066, 112, 92, 199  # écran du téléphone
    out = [f'<clipPath id="lap"><rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="4"/></clipPath>',
           f'<clipPath id="pho"><rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="10"/></clipPath>']
    # halo derrière les écrans
    out.append(f'<ellipse cx="{lx + lw / 2}" cy="{ly + lh / 2}" rx="230" ry="140" fill="{C["cyan"]}" opacity=".07" filter="url(#glow)"/>')
    # portable
    out.append(f'<rect x="{lx - 10}" y="{ly - 10}" width="{lw + 20}" height="{lh + 20}" rx="12" fill="#0B1222" stroke="#3A4C70" stroke-width="1.4"/>')
    out.append(f'<path d="M{lx - 44} {ly + lh + 14}H{lx + lw + 44}L{lx + lw + 30} {ly + lh + 26}H{lx - 30}Z" fill="#141E33" stroke="#3A4C70"/>')
    out.append(f'<g clip-path="url(#lap)">')
    for i, (name, _) in enumerate(STUDY_TOOLS):
        out.append(f'<image class="slide{' first' if i == 0 else ''}" style="animation-delay:{i * slot}s" href="{thumb(name + "-desktop", (560, 350), 58)}" '
                   f'x="{lx}" y="{ly}" width="{lw}" height="{lh}" preserveAspectRatio="xMidYMin slice"/>')
    out.append(f'<rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" fill="#0A1430" opacity=".18"/></g>')
    # téléphone
    out.append(f'<rect x="{px - 5}" y="{py - 5}" width="{pw + 10}" height="{ph + 10}" rx="14" fill="#0B1222" stroke="#3A4C70" stroke-width="1.4"/>')
    out.append(f'<g clip-path="url(#pho)">')
    for i, (name, _) in enumerate(STUDY_TOOLS):
        out.append(f'<image class="slide{' first' if i == 0 else ''}" style="animation-delay:{i * slot + .4}s" href="{thumb(name + "-mobile", (184, 398), 55)}" '
                   f'x="{px}" y="{py}" width="{pw}" height="{ph}" preserveAspectRatio="xMidYMin slice"/>')
    out.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" fill="#0A1430" opacity=".18"/></g>')
    # légende qui change avec l'outil affiché
    for i, label in enumerate(T([l for _, l in STUDY_TOOLS], STUDY_FR)):
        d, _ = text_path("consola.ttf", f"{i + 1:02d}/{n:02d}  {label}", 11.5, lx - 10, 38, tracking=1.4)
        out.append(f'<path class="slide{' first' if i == 0 else ''}" style="animation-delay:{i * slot}s" d="{d}" fill="{C["gold"]}"/>')
    out.append(f'<circle class="rec" cx="{lx + lw + 4}" cy="34" r="3.5" fill="{C["red"]}" filter="url(#glow)"/>')
    pct = 100 / n
    css = f""".slide {{ opacity: 0; animation: slide {total}s linear infinite; }}
    .rec {{ animation: blink 1.4s steps(1) infinite; }}
    @keyframes slide {{ 0% {{ opacity: 0; }} {pct * .12:.2f}% {{ opacity: 1; }} {pct * .92:.2f}% {{ opacity: 1; }} {pct * 1.08:.2f}% {{ opacity: 0; }} 100% {{ opacity: 0; }} }}
    @keyframes blink {{ 0% {{ opacity: 1; }} 50% {{ opacity: .15; }} }}
    @media (prefers-reduced-motion: reduce) {{ .slide.first {{ opacity: 1; }} }}"""
    return "".join(out), css


CARDS["card-study-tools"] = dict(
        label_fr="OUTILS DE RÉVISION · UN EXAMEN ARRIVE ? JE CODE L'OUTIL",
        title_fr='Outils de révision',
        desc_fr="À chaque examen, je construis l'outil de révision que j'aurais aimé avoir : un entraîneur SQL dans le navigateur, un simulateur Cisco IOS et un labo de câblage, un quiz réseau de 438 cartes, un entraîneur TP Java et un atelier d'anglais. La vitrine est publique, les sources restent privées.",
    num="04", label="STUDY TOOLS · AN EXAM COMING UP? I BUILD THE TOOL", title="Study tools",
    desc="Every time an exam comes up, I build the revision tool I wish I had: an in-browser SQL "
         "trainer, a Cisco IOS simulator and cabling lab, a 438-card networking quiz, a Java lab "
         "trainer and an English workshop. The showcase is public; the sources stay private.",
    tag_list=["SQL", "Cisco IOS", "cabling lab", "438-card quiz", "Java", "English"], art=art_study)


if __name__ == "__main__":
    for LANG in ("en", "fr"):
        for name, spec in CARDS.items():
            spec = dict(spec)
            art_fn = spec.pop("art")
            fr = {k[:-3]: spec.pop(k) for k in [k for k in spec if k.endswith("_fr")]}
            if LANG == "fr":
                spec.update(fr)
            art, css = art_fn()
            svg = card(art=art, art_css=css, fr="", **spec)
            out = OUT / (f"{name}.svg" if LANG == "en" else f"{name}-fr.svg")
            out.write_text(svg, encoding="utf-8")
            print("ok", out.name, len(svg) // 1024, "KB")

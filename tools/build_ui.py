"""Génère les éléments d'interface du profil, en anglais et en français :
boutons, bandeaux de section, carte « à propos », tuiles de dépôts et boîte à outils.

Usage :  python tools/build_ui.py
Mêmes prérequis que build_banner.py.
"""
import random
from pathlib import Path

from build_banner import text_path
from build_cards import C, width

OUT = Path(__file__).resolve().parent.parent / "assets" / "ui"
BLUE, BLUE_TXT = "#2F81F7", "#58A6FF"

HEAD = """<defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#05070F"/><stop offset="1" stop-color="#101A2E"/></linearGradient>
    <radialGradient id="haze" cx=".85" cy=".5" r=".55"><stop offset="0" stop-color="#3B2A55" stop-opacity=".4"/><stop offset="1" stop-color="#3B2A55" stop-opacity="0"/></radialGradient>
    <linearGradient id="rule" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#7FD6FF" stop-opacity=".7"/><stop offset="1" stop-color="#7FD6FF" stop-opacity="0"/></linearGradient>
    <filter id="glow" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="3" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  </defs>"""
BASE_CSS = """.s { animation: tw 5s ease-in-out infinite; }
    .pulse { animation: pulse 2.6s ease-in-out infinite; }
    .blink { animation: blink 1.1s steps(1) infinite; }
    @keyframes tw { 0%, 100% { opacity: .2; } 50% { opacity: .9; } }
    @keyframes pulse { 0%, 100% { opacity: .45; } 50% { opacity: 1; } }
    @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0; } }"""


def svg(w, h, body, css="", label="", bg=True, seed=1, stars=0):
    rng = random.Random(seed)
    st = "".join(f'<circle class="s" style="animation-delay:{rng.uniform(0, 5):.1f}s" cx="{rng.uniform(w * .55, w - 10):.0f}" '
                 f'cy="{rng.uniform(8, h - 8):.0f}" r="{rng.choice([.6, .8, 1])}" fill="#DCE6FF"/>' for _ in range(stars))
    back = (f'<rect width="{w}" height="{h}" rx="16" fill="url(#bg)"/><rect width="{w}" height="{h}" rx="16" fill="url(#haze)"/>'
            f'{st}<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="15.5" fill="none" stroke="{C["edge"]}"/>') if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{label}">\n'
            f'  {HEAD}\n  <style>\n    {BASE_CSS}\n    {css}\n    @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}\n  </style>\n'
            f'  {back}\n  {body}\n</svg>\n')


def save(name, content):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{name}.svg").write_text(content, encoding="utf-8")


# ---------- boutons ----------
def button(name, text, style):
    d, w = text_path("segoeuib.ttf" if style != "ghost" else "segoeui.ttf", text, 17, 22, 29)
    bw = w + 44
    fill, stroke, col = {"on": (BLUE, BLUE, "#FFFFFF"), "blue": ("#0B1222", BLUE, BLUE_TXT),
                         "ghost": ("#0B1222", "#33425E", C["body"])}[style]
    body = (f'<rect x="1" y="1" width="{bw - 2:.1f}" height="42" rx="21" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
            f'<path d="{d}" fill="{col}"/>')
    save(name, svg(round(bw), 44, body, label=text, bg=False))


# ---------- bandeaux de section ----------
def header(name, num, text):
    d, w = text_path("consola.ttf", f"{num} / {text}", 17, 30, 45, tracking=3)
    body = (f'<circle class="pulse" cx="16" cy="39" r="4" fill="{C["gold"]}" filter="url(#glow)"/>{_p(d, C["ink"])}'
            f'<path d="M{30 + w + 24:.0f} 39H1176" stroke="url(#rule)" stroke-width="1.5"/>')
    save(name, svg(1200, 72, body, label=text, bg=True, seed=len(name), stars=10))


def _p(d, col):
    return f'<path d="{d}" fill="{col}"/>'


# ---------- texte enrichi : **gras** en doré ----------
def rich(paragraphs, x, y, maxw, size=19, lh=29, gap=14):
    out = []
    for para in paragraphs:
        words = []
        bold = False
        prev = ""
        for chunk in para.split("**"):
            for k, wd in enumerate(chunk.split()):
                glue = k == 0 and bool(words) and not chunk[:1].isspace() and not prev[-1:].isspace()
                words.append((wd, bold, glue))
            prev = chunk
            bold = not bold
        line, lw = [], 0.0
        space = width("segoeui.ttf", " ", size)

        def flush(line, y):
            cx = x
            for k, (wd, b, g) in enumerate(line):
                if k and not g:
                    cx += space
                f = "segoeuib.ttf" if b else "segoeui.ttf"
                d, ww = text_path(f, wd, size, cx, y)
                out.append(_p(d, C["gold"] if b else C["body"]))
                cx += ww

        for wd, b, g in words:
            ww = width("segoeuib.ttf" if b else "segoeui.ttf", wd, size)
            if line and not g and lw + space + ww > maxw:
                flush(line, y)
                y += lh
                line, lw = [], 0.0
                g = False
            lw += (space if line and not g else 0) + ww
            line.append((wd, b, g))
        flush(line, y)
        y += lh + gap
    return "".join(out), y


# ---------- carte « à propos » ----------
ABOUT = {
    "en": dict(label="00 — ABOUT", paras=[
        "Engineering student at **UTBM**, on a work-study apprenticeship at **Électricité de Strasbourg**: half my week "
        "is spent in the **energy sector**, where power grids, data and the energy transition meet.",
        "I'm into **AI agents**. I write skills, MCP servers and multi-agent workflows, and I work with agents every day. "
        "The rest of the time I build web apps that work offline, and **whenever an exam is coming up, I build myself a tool to revise for it.**",
        "I also have a soft spot for **China**: its cities, the street life, the metro at rush hour, the Huangpu at night."],
        rows=[("ENERGY", "Électricité de Strasbourg"), ("AI AGENTS", "skills · MCP · multi-agent"), ("CHINA", "cities after dark")]),
    "fr": dict(label="00 — À PROPOS", paras=[
        "Élève ingénieur à l'**UTBM**, en alternance chez **Électricité de Strasbourg** : la moitié de ma semaine se passe "
        "dans le **secteur de l'énergie**, là où se rencontrent réseaux électriques, données et transition énergétique.",
        "Je suis passionné par les **agents IA**. J'écris des skills, des serveurs MCP et des workflows multi-agents, et je "
        "travaille avec des agents tous les jours. Le reste du temps, je construis des applis web qui marchent hors-ligne, et "
        "**dès qu'un examen approche, je me code l'outil pour le réviser.**",
        "J'ai aussi un faible pour la **Chine** : ses villes, la vie de rue, le métro à l'heure de pointe, le Huangpu la nuit."],
        rows=[("ÉNERGIE", "Électricité de Strasbourg"), ("AGENTS IA", "skills · MCP · multi-agents"), ("CHINE", "les villes la nuit")]),
}


def icons(i, x, y):
    if i == 0:  # éclair
        return (f'<path class="pulse" d="M{x + 4} {y - 16}L{x - 8} {y + 2}H{x}L{x - 4} {y + 18}L{x + 10} {y - 2}H{x + 1}Z" '
                f'fill="{C["gold"]}" filter="url(#glow)"/>')
    if i == 1:  # mini réseau d'agents
        pts = [(x - 12, y - 8), (x + 12, y - 8), (x, y + 12)]
        lines = "".join(f'<path d="M{x} {y}L{a} {b}" stroke="#3A4C70" stroke-width="1.4"/>' for a, b in pts)
        dots = "".join(f'<circle class="pulse" style="animation-delay:{k * .5}s" cx="{a}" cy="{b}" r="3.6" fill="{C["cyan"]}" filter="url(#glow)"/>'
                       for k, (a, b) in enumerate(pts))
        return lines + f'<circle cx="{x}" cy="{y}" r="5" fill="{C["pink"]}" filter="url(#glow)"/>' + dots
    # mini skyline
    sky = (f'<path d="M{x - 14} {y + 14}V{y + 4}H{x - 8}V{y + 14}M{x - 4} {y + 14}V{y - 12}L{x - 2} {y - 18}L{x} {y - 12}V{y + 14}'
           f'M{x + 4} {y + 14}V{y - 4}H{x + 12}V{y + 14}" fill="none" stroke="#5A6A88" stroke-width="1.4"/>')
    return sky + f'<circle class="pulse" cx="{x - 2}" cy="{y - 5}" r="3" fill="{C["pink"]}" filter="url(#glow)"/>'


def about(lang):
    a = ABOUT[lang]
    label_d, _ = text_path("consola.ttf", a["label"], 12, 56, 58, tracking=1.6)
    body, y = rich(a["paras"], 56, 104, 660)
    h = max(round(y + 16), 330)
    rows = []
    ry = 104
    step = (h - 64 - ry) / 2
    for i, (t, sub) in enumerate(a["rows"]):
        cy = ry + i * step
        rows.append(f'<rect x="790" y="{cy - 34:.0f}" width="350" height="68" rx="12" fill="#0B1222" stroke="#22304A"/>')
        rows.append(icons(i, 830, cy))
        td, _ = text_path("consola.ttf", t, 14, 866, cy - 3, tracking=2)
        sd, _ = text_path("segoeui.ttf", sub, 15, 866, cy + 19)
        rows.append(_p(td, C["ink"]) + _p(sd, C["muted"]))
    body = _p(label_d, C["muted"]) + body + "".join(rows)
    plain = " ".join(p.replace("**", "") for p in a["paras"])
    save(f"about-{lang}", svg(1200, h, body, label=plain, seed=3, stars=24))


# ---------- tuiles de dépôts ----------
LANG_COL = {"Python": "#3572A5", "TypeScript": "#3178C6", "PHP": "#7A86B8", "C": "#A8B9CC", "Jupyter": "#DA5B0B"}
TILES = [
    ("meteo-time-series", "Python", ("DATA · WEATHER", "DATA · MÉTÉO"), ("Strasbourg forecast", "Prévision à Strasbourg"),
     ("Next-day temperature forecasting, where linear regression beats Random Forest.",
      "Température du lendemain : la régression linéaire bat la Random Forest.")),
    ("meteo-ml-insights", "Python", ("DATA · WEATHER", "DATA · MÉTÉO"), ("MeteoInsight", "MeteoInsight"),
     ("Local weather analysis app with ML forecasts and a Streamlit interface.",
      "Appli locale d'analyse météo, prévisions ML et interface Streamlit.")),
    ("analyse-climat-strasbourg", "Jupyter", ("DATA · CLIMATE", "DATA · CLIMAT"), ("Strasbourg climate", "Climat de Strasbourg"),
     ("Exploring Strasbourg's climate data in a Jupyter notebook.",
      "Exploration des données climatiques de Strasbourg en notebook.")),
    ("apprendre-chinois-mandarin", "TypeScript", ("LEARNING MANDARIN", "APPRENDRE LE MANDARIN"), ("Mandarin app", "Appli de mandarin"),
     ("The app I built to learn Mandarin Chinese.", "L'appli que je me suis faite pour apprendre le chinois.")),
    ("projet-bd70", "PHP", ("SCHOOL PROJECT", "PROJET D'ÉCOLE"), ("Warehouse app", "Gestion d'entrepôt"),
     ("Warehouse management web app in PHP and MariaDB.", "Appli web de gestion d'entrepôt en PHP et MariaDB.")),
    ("Projet-LP25-A2025", "C", ("SCHOOL PROJECT", "PROJET D'ÉCOLE"), ("Systems in C", "Système en C"),
     ("Group project in systems programming, written in C.", "Projet de groupe en programmation système, en C.")),
]


def tile(repo, lang_name, cat, title, desc, li):
    w, h = 390, 170
    cat_d, _ = text_path("consola.ttf", cat[li], 11, 24, 36, tracking=1.4)
    t_d, _ = text_path("georgia.ttf", title[li], 25, 23, 72)
    from build_cards import wrap
    lines = wrap("segoeui.ttf", desc[li], 15, w - 48)[:2]
    body = [_p(cat_d, C["muted"]), _p(t_d, C["ink"])]
    for k, ln in enumerate(lines):
        d, _ = text_path("segoeui.ttf", ln, 15, 24, 100 + k * 21)
        body.append(_p(d, C["body"]))
    ld, _ = text_path("consola.ttf", lang_name, 12, 40, 150)
    body.append(f'<circle cx="29" cy="146" r="5" fill="{LANG_COL[lang_name]}"/>{_p(ld, C["muted"])}')
    ad, _ = text_path("segoeui.ttf", "↗", 18, w - 24, 38, anchor="end")
    body.append(_p(ad, BLUE_TXT))
    save(f"tile-{repo}-{['en', 'fr'][li]}", svg(w, h, "".join(body), label=f"{title[li]}: {desc[li]}", seed=len(repo), stars=6))


# ---------- boîte à outils ----------
TOOLBOX = {
    "en": [("LANGUAGES", ["Python", "TypeScript", "JavaScript", "PHP", "C", "SQL"]),
           ("BUILDING", ["React", "Vite", "Supabase", "Streamlit", "Docker", "Vercel"]),
           ("AI", ["agent skills", "MCP", "multi-agent", "Hugging Face", "Whisper", "scikit-learn", "Claude Code", "Codex"])],
    "fr": [("LANGAGES", ["Python", "TypeScript", "JavaScript", "PHP", "C", "SQL"]),
           ("CONSTRUCTION", ["React", "Vite", "Supabase", "Streamlit", "Docker", "Vercel"]),
           ("IA", ["skills d'agents", "MCP", "multi-agents", "Hugging Face", "Whisper", "scikit-learn", "Claude Code", "Codex"])],
}
SIGN = {"en": "One commit at a time.", "fr": "Un commit à la fois."}


def toolbox(lang):
    body = []
    y = 54
    for label, items in TOOLBOX[lang]:
        ld, _ = text_path("consola.ttf", label, 12, 56, y + 18, tracking=1.8)
        body.append(_p(ld, C["muted"]))
        x = 230
        for it in items:
            d, w = text_path("consola.ttf", it, 14, x + 14, y + 19)
            body.append(f'<rect x="{x}" y="{y}" width="{w + 28:.1f}" height="28" rx="14" fill="{C["pill"]}" stroke="#2E3D5C"/>'
                        + _p(d, C["body"]))
            x += w + 28 + 10
        y += 46
    sd, sw = text_path("georgiai.ttf", SIGN[lang], 18, 1124, 232, anchor="end")
    body.append(_p(sd, C["muted"]))
    body.append(f'<rect class="blink" x="1130" y="217" width="9" height="18" fill="{C["gold"]}"/>')
    save(f"toolbox-{lang}", svg(1200, 256, "".join(body), label=" · ".join(i for _, its in TOOLBOX[lang] for i in its),
                                seed=9, stars=14))


if __name__ == "__main__":
    button("btn-en-on", "English", "on")
    button("btn-en-off", "English", "ghost")
    button("btn-fr-on", "Français", "on")
    button("btn-fr-off", "Français", "blue")
    button("btn-linkedin", "LinkedIn ↗", "ghost")
    button("btn-repos-en", "All repositories ↗", "ghost")
    button("btn-repos-fr", "Tous mes dépôts ↗", "ghost")
    for lang, names in {"en": ["SELECTED WORK", "ACTIVITY", "ALSO ON THE SHELF", "TOOLBOX"],
                        "fr": ["PROJETS PHARES", "ACTIVITÉ", "AUSSI DANS L'ATELIER", "BOÎTE À OUTILS"]}.items():
        for k, n in enumerate(names):
            header(f"h{k + 1}-{lang}", f"{k + 1:02d}", n)
        about(lang)
        toolbox(lang)
    for li in (0, 1):
        for t in TILES:
            tile(*t, li)
    print("ok", len(list(OUT.glob("*.svg"))), "files in", OUT)

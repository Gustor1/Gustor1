"""Génère assets/city.svg : le calendrier de contributions en ville la nuit.

Chaque semaine est un immeuble, chaque jour une fenêtre (dimanche en haut,
samedi en bas, comme sur GitHub). Plus il y a de contributions, plus la
fenêtre brille. Les étages au-dessus montrent le volume de la semaine.

Usage :  python tools/build_city.py [login]
Jeton : variable GITHUB_TOKEN, sinon `gh auth token`.
Aucune dépendance hors bibliothèque standard (tourne dans GitHub Actions).
"""
import json
import os
import random
import subprocess
import sys
import urllib.request
from datetime import date
from pathlib import Path

LOGIN = sys.argv[1] if len(sys.argv) > 1 else "Gustor1"
OUT = Path(__file__).resolve().parent.parent / "assets" / "city.svg"

QUERY = """query($login:String!){ user(login:$login){ contributionsCollection{
  contributionCalendar{ totalContributions weeks{ contributionDays{
    date contributionCount contributionLevel weekday } } } } } }"""


def token():
    t = os.environ.get("GITHUB_TOKEN")
    if t:
        return t
    return subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True).stdout.strip()


def fetch():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
        headers={"Authorization": f"bearer {token()}", "Content-Type": "application/json",
                 "User-Agent": "profile-city-builder"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if "errors" in data:
        raise SystemExit(data["errors"])
    return data["data"]["user"]["contributionsCollection"]["contributionCalendar"]


LEVEL = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}
LIT = ["#1A2236", "#7A5A26", "#C88A2E", "#FFC45C", "#FFE7A3"]
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()

W, H = 1200, 330
X0, COL, BW = 40, 21.2, 17   # début, pas entre immeubles, largeur d'un immeuble
CELL, WIN = 13, 9            # hauteur d'étage, taille de fenêtre
GROUND = 262


def build(cal):
    rng = random.Random(7)
    weeks = cal["weeks"][-53:]
    totals = [sum(d["contributionCount"] for d in w["contributionDays"]) for w in weeks]
    peak = max(totals) or 1
    today = date.today().isoformat()
    parts, months, last_m = [], [], None

    for i, w in enumerate(weeks):
        x = X0 + i * COL
        extra = round(5 * (totals[i] / peak) ** 0.7) if totals[i] else 0
        floors = 7 + extra
        top = GROUND - floors * CELL - 4
        roof = ""
        if totals[i] == peak and peak > 0:
            roof = (f'<path d="M{x + BW / 2:.1f} {top}V{top - 16}" stroke="#33425E" stroke-width="1.2"/>'
                    f'<circle class="blink" cx="{x + BW / 2:.1f}" cy="{top - 17}" r="1.8" fill="#FF3B3B"/>')
        parts.append(f'<rect x="{x:.1f}" y="{top}" width="{BW}" height="{GROUND - top}" rx="1.5" '
                     f'fill="#0A1120" stroke="#25324A"/>{roof}')
        # étages de volume (éteints, lueur faible)
        for f in range(extra):
            y = top + 4 + f * CELL + 2
            parts.append(f'<rect x="{x + 4:.1f}" y="{y}" width="{WIN}" height="{WIN - 2}" rx="1" fill="#141C2E"/>')
        # 7 fenêtres = 7 jours, dimanche en haut
        days = {d["weekday"]: d for d in w["contributionDays"]}
        for wd in range(7):
            y = GROUND - (7 - wd) * CELL + 2
            d = days.get(wd)
            if d is None:
                continue
            lvl = LEVEL[d["contributionLevel"]]
            delay = 0.3 + i * 0.045 + rng.random() * 0.25
            title = f'<title>{d["date"]} : {d["contributionCount"]} contribution(s)</title>'
            cls = "w"
            if d["date"] == today:
                cls = "w today"
            elif lvl and rng.random() < 0.08:
                cls = "w f"
            glow = ' filter="url(#g)"' if lvl == 4 else ""
            style = f"animation-delay:{delay:.2f}s" + (f",{delay + rng.uniform(1, 8):.2f}s" if cls == "w f" else "")
            parts.append(f'<rect class="{cls}" style="{style}" x="{x + 4:.1f}" y="{y}" width="{WIN}" height="{WIN - 2}" '
                         f'rx="1" fill="{LIT[lvl]}"{glow}>{title}</rect>')
        m = int(w["contributionDays"][0]["date"][5:7])
        if m != last_m:
            if last_m is not None and i < 52:
                months.append(f'<text x="{x:.1f}" y="{GROUND + 22}">{MONTHS[m - 1]}</text>')
            last_m = m

    total = cal["totalContributions"]
    legend = "".join(f'<rect x="{1040 + k * 16}" y="{H - 27}" width="11" height="9" rx="1" fill="{c}"/>'
                     for k, c in enumerate(LIT))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t d">
  <title id="t">{total} contributions in the last year</title>
  <desc id="d">GitHub contribution calendar drawn as a city at night: one building per week, one window per day; brighter windows mean more contributions.</desc>
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#05070F"/><stop offset="1" stop-color="#111A2E"/></linearGradient>
    <filter id="g" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="2.2" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  </defs>
  <style>
    text {{ font: 12px ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace; fill: #8B95A8; letter-spacing: .06em; }}
    .h {{ font: italic 22px Georgia, "Times New Roman", serif; fill: #F3EEE4; letter-spacing: 0; }}
    .w {{ opacity: 0; animation: on .5s ease-out forwards; }}
    .w.f {{ animation-name: on, flick; animation-duration: .5s, 6s; animation-iteration-count: 1, infinite; animation-timing-function: ease-out, steps(1); }}
    .w.today {{ animation-name: on, pulse; animation-duration: .5s, 1.8s; animation-iteration-count: 1, infinite; }}
    .blink {{ animation: blink 1.6s steps(1) infinite; }}
    @keyframes on {{ to {{ opacity: 1; }} }}
    @keyframes flick {{ 0%, 90%, 93%, 100% {{ opacity: 1; }} 91% {{ opacity: .2; }} }}
    @keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: .35; }} }}
    @keyframes blink {{ 0% {{ opacity: 1; }} 50% {{ opacity: .1; }} }}
    @media (prefers-reduced-motion: reduce) {{ .w, .blink {{ animation: none !important; opacity: 1; }} }}
  </style>
  <rect width="{W}" height="{H}" rx="16" fill="url(#sky)"/>
  <text class="h" x="{X0}" y="44">{total:,} contributions in the last year</text>
  <text x="{X0}" y="68">One building per week, one window per day. The brighter the window, the more I pushed.</text>
  {''.join(parts)}
  <path d="M{X0 - 10} {GROUND}H{W - X0 + 10}" stroke="#2A3650" stroke-width="1.2"/>
  <g>{''.join(months)}</g>
  <text x="{1040 - 40}" y="{H - 18}">less</text>{legend}<text x="{1040 + 5 * 16 + 4}" y="{H - 18}">more</text>
  <text x="{X0}" y="{H - 18}" style="font-size:10px;opacity:.6">updated {date.today().isoformat()}</text>
</svg>
"""


if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    svg = build(fetch())
    OUT.write_text(svg, encoding="utf-8")
    print("ok", OUT, len(svg) // 1024, "KB")

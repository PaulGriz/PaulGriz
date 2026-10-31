#!/usr/bin/env python3
"""Generates the animated SVGs used by the profile README.

Run from the repo root:  python3 scripts/generate.py
Everything is self-hosted in assets/ so no third-party card service can break it.
"""
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "assets"
W = 850

MONO = "ui-monospace,'SF Mono',SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono','Liberation Mono',monospace"
CW = 0.6  # monospace advance per em; textLength pins it where layout depends on it

C = {
    "bg": "#0a0e15",
    "panel": "#0e1520",
    "edge": "#1d2a3b",
    "grid": "#132031",
    "text": "#c9d4e3",
    "dim": "#5f7189",
    "cyan": "#4cc9f0",
    "green": "#39ff88",
    "amber": "#ffb000",
    "red": "#ff4d6d",
    "magenta": "#c77dff",
}


def t(s):
    return escape(s, {"'": "&#39;", '"': "&quot;"})


def svg(h, body, style="", defs=""):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="{W}" height="{h}" role="img">
<style>
text{{font-family:{MONO};}}
{style}
@media (prefers-reduced-motion: reduce){{*{{animation:none!important}}}}
</style>
<defs>
<pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse"><path d="M24 0H0V24" fill="none" stroke="{C['grid']}" stroke-width="1"/></pattern>
<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#fff" opacity=".035"/></pattern>
<linearGradient id="band" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{C['cyan']}" stop-opacity="0"/><stop offset=".5" stop-color="{C['cyan']}" stop-opacity=".07"/><stop offset="1" stop-color="{C['cyan']}" stop-opacity="0"/></linearGradient>
<clipPath id="frame"><rect x="1" y="1" width="{W-2}" height="{h-2}" rx="14"/></clipPath>
{defs}
</defs>
<g clip-path="url(#frame)">
<rect width="{W}" height="{h}" fill="{C['bg']}"/>
<rect width="{W}" height="{h}" fill="url(#grid)" opacity=".55"/>
{body}
<rect width="{W}" height="{h}" fill="url(#scan)"/>
<rect class="sweepband" y="-120" width="{W}" height="120" fill="url(#band)"/>
</g>
<rect x="1" y="1" width="{W-2}" height="{h-2}" rx="14" fill="none" stroke="{C['edge']}" stroke-width="2"/>
</svg>
"""


BAND_STYLE = """
.sweepband{animation:band 7s linear infinite}
@keyframes band{from{transform:translateY(0)}to{transform:translateY(%dpx)}}
.pulse{animation:pulse 1.6s ease-in-out infinite}
@keyframes pulse{0%%,100%%{opacity:1}50%%{opacity:.25}}
"""


def keyframe_track(events, total):
    """events: list of (time, value) sorted; returns (values, keyTimes) for a discrete SMIL animate."""
    pts = {}
    for tm, v in events:
        pts[round(tm / total, 4)] = v
    if 0 not in pts:
        pts[0.0] = events[0][1]
    ks = sorted(k for k in pts if k <= 1)
    return ";".join(f"{pts[k]:g}" for k in ks), ";".join(f"{k:g}" for k in ks)


# --------------------------------------------------------------------------- header

FONT = {
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "G": ["01110", "10001", "10000", "10111", "10001", "10001", "01111"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "I": ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
    "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    " ": ["000"] * 7,  # narrower than a letter so the two words sit closer
}


def pixel_rects(word, x0, y0, px, gap=1.5):
    rects, col = [], 0
    for ch in word:
        for ry, row in enumerate(FONT[ch]):
            for rx, bit in enumerate(row):
                if bit == "1":
                    x = x0 + (col + rx) * px
                    y = y0 + ry * px
                    rects.append(f'<rect x="{x:g}" y="{y:g}" width="{px-gap:g}" height="{px-gap:g}" rx="1.5"/>')
        col += len(FONT[ch][0]) + 1
    return "".join(rects)


def pixel_width(word, px):
    return (sum(len(FONT[ch][0]) + 1 for ch in word) - 1) * px


def header():
    h = 300
    px = 10.5
    tx, ty = 40, 70
    title_w = pixel_width("PAUL GRIZ", px)
    rects = pixel_rects("PAUL GRIZ", tx, ty, px)

    # typing subtitle
    phrases = [
        "professional tinkerer.",
        "runs more AI agents than is reasonable.",
        "senior manager @ Doeren Mayhew by day.",
        "if I do it twice, an agent does it next.",
        "over the top is a valid design spec.",
    ]
    fs = 18
    cw = fs * CW
    x0, by = tx + 2 * cw, 192
    tl, cursor, tracks = 0.0, [], []
    for p in phrases:
        ev = [(tl, 0)]
        for k in range(1, len(p) + 1):
            ev.append((tl, k * cw))
            cursor.append((tl, x0 + k * cw))
            tl += 0.055
        tl += 2.1
        for k in range(len(p) - 1, -1, -1):
            ev.append((tl, k * cw))
            cursor.append((tl, x0 + k * cw))
            tl += 0.022
        tl += 0.35
        tracks.append(ev)
    total = tl
    typing = []
    for i, (p, ev) in enumerate(zip(phrases, tracks)):
        vals, kts = keyframe_track([(0, 0)] + ev + [(ev[-1][0] + 0.001, 0)], total)
        typing.append(
            f'<clipPath id="ty{i}"><rect x="{x0:g}" y="{by-fs}" width="0" height="{fs+8}">'
            f'<animate attributeName="width" values="{vals}" keyTimes="{kts}" dur="{total:.3f}s" calcMode="discrete" repeatCount="indefinite"/></rect></clipPath>'
            f'<text clip-path="url(#ty{i})" x="{x0:g}" y="{by}" font-size="{fs}" fill="{C["text"]}" textLength="{len(p)*cw:g}" lengthAdjust="spacing">{t(p)}</text>'
        )
    cv, ck = keyframe_track([(0, x0)] + cursor, total)
    typing.append(
        f'<rect class="blink" y="{by-fs+3}" x="{x0:g}" width="{cw*0.9:g}" height="{fs}" fill="{C["green"]}">'
        f'<animate attributeName="x" values="{cv}" keyTimes="{ck}" dur="{total:.3f}s" calcMode="discrete" repeatCount="indefinite"/></rect>'
    )

    # tag chips
    tags = [("TINKERER", C["green"]), ("AI MAXIMALIST", C["cyan"]), ("SHIPS AT 3AM", C["magenta"]), ("ALWAYS ON", C["amber"])]
    chips, cx = [], tx
    for label, col in tags:
        tw = len(label) * 11 * CW
        wdt = tw + 30
        chips.append(
            f'<rect x="{cx:g}" y="214" width="{wdt:g}" height="24" rx="4" fill="{col}" fill-opacity=".08" stroke="{col}" stroke-opacity=".55"/>'
            f'<rect x="{cx+9:g}" y="223.5" width="5" height="5" fill="{col}" class="pulse" style="animation-delay:{len(chips)*.4:.1f}s"/>'
            f'<text x="{cx+20:g}" y="230" font-size="11" fill="{col}" letter-spacing="0" textLength="{tw:g}" lengthAdjust="spacing">{label}</text>'
        )
        cx += wdt + 10

    # radar
    rcx, rcy, rr = 728, 148, 80
    trail = "".join(
        f'<path d="M0 0L{rr} 0A{rr} {rr} 0 0 0 {rr*__import__("math").cos(__import__("math").radians(-6)):.2f} {rr*__import__("math").sin(__import__("math").radians(-6)):.2f}Z" '
        f'fill="{C["green"]}" opacity="{0.42*(1-i/10):.3f}" transform="rotate({-i*6})"/>'
        for i in range(10)
    )
    blips = [(35, 0.62, "claude-01"), (128, 0.4, "claude-03"), (205, 0.78, "gpu-01"), (290, 0.55, "claude-02"), (330, 0.85, "gpu-02")]
    import math
    blip_svg = []
    for ang, dist, label in blips:
        bx = rr * dist * math.cos(math.radians(ang))
        by_ = rr * dist * math.sin(math.radians(ang))
        begin = ang / 360 * 4
        anim = f'<animate attributeName="opacity" values="1;.15;0" keyTimes="0;.55;1" dur="4s" begin="{begin:.2f}s" repeatCount="indefinite"/>'
        anchor = "end" if bx < 0 else "start"
        lx = bx - 7 if bx < 0 else bx + 7
        blip_svg.append(
            f'<g opacity="0">{anim}<circle cx="{bx:.1f}" cy="{by_:.1f}" r="3.5" fill="{C["green"]}"/>'
            f'<circle cx="{bx:.1f}" cy="{by_:.1f}" r="7" fill="none" stroke="{C["green"]}" stroke-opacity=".5"/>'
            f'<text x="{lx:.1f}" y="{by_+3.5:.1f}" font-size="9" fill="{C["green"]}" text-anchor="{anchor}">{label}</text></g>'
        )
    radar = f"""
<g transform="translate({rcx},{rcy})">
  <circle r="{rr}" fill="{C['green']}" fill-opacity=".03" stroke="{C['green']}" stroke-opacity=".35"/>
  <circle r="{rr*2/3:.1f}" fill="none" stroke="{C['green']}" stroke-opacity=".18"/>
  <circle r="{rr/3:.1f}" fill="none" stroke="{C['green']}" stroke-opacity=".18"/>
  <path d="M-{rr} 0H{rr}M0 -{rr}V{rr}" stroke="{C['green']}" stroke-opacity=".15"/>
  <g>{trail}<line x2="{rr}" stroke="{C['green']}" stroke-width="1.5"/>
    <animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="4s" repeatCount="indefinite"/></g>
  {''.join(blip_svg)}
  <circle r="3" fill="{C['green']}"/>
</g>
<text x="{rcx}" y="{rcy+rr+20}" font-size="10" fill="{C['dim']}" text-anchor="middle" letter-spacing="2">FLEET SCAN · 5 CONTACTS</text>
"""

    # ticker
    tick = "\u00a0\u00a0▲ AGENTS ONLINE: 7  ▲ HUMANS IN THE LOOP: 1 (CAFFEINATED)  ▲ TASKS DONE BY HAND TODAY: 0  ▲ GPUS: WARM  ▲ MODEL IN USE: THE BEST ONE  ▲ CURRENT STATUS: TINKERING\u00a0"
    tfs = 11
    tlen = len(tick) * tfs * CW * 1.05
    ticker = f"""
<rect x="0" y="256" width="{W}" height="30" fill="{C['panel']}"/>
<line x1="0" x2="{W}" y1="256" y2="256" stroke="{C['edge']}"/>
<g class="ticker">
  <text x="0" y="275" font-size="{tfs}" fill="{C['amber']}" letter-spacing="1" textLength="{tlen:.1f}" lengthAdjust="spacing">{t(tick)}</text>
  <text x="{tlen:.1f}" y="275" font-size="{tfs}" fill="{C['amber']}" letter-spacing="1" textLength="{tlen:.1f}" lengthAdjust="spacing">{t(tick)}</text>
</g>
"""

    title = f"""
<g transform="translate(3.5,3.5)" fill="#0d4b5c">{rects}</g>
<g class="gl gl1" fill="{C['magenta']}">{rects}</g>
<g class="gl gl2" fill="{C['cyan']}">{rects}</g>
<g class="ttl" fill="url(#tgrad)" clip-path="url(#reveal)">{rects}</g>
<g clip-path="url(#tshape)"><rect class="shine" x="{tx-120}" y="{ty-10}" width="60" height="95" fill="#fff" opacity=".35" transform="skewX(-20)"/></g>
"""
    defs = f"""
<linearGradient id="tgrad" gradientUnits="userSpaceOnUse" x1="{tx}" y1="0" x2="{tx+title_w}" y2="0">
  <stop offset="0" stop-color="{C['cyan']}"/><stop offset=".55" stop-color="#7cf5d0"/><stop offset="1" stop-color="{C['green']}"/>
</linearGradient>
<clipPath id="reveal"><rect x="{tx}" y="{ty-5}" width="0" height="90"><animate attributeName="width" from="0" to="{title_w+10:g}" dur="1.1s" fill="freeze" calcMode="discrete" values="{';'.join(str(int(i*px*6)) for i in range(10))};{title_w+10:g}"/></rect></clipPath>
<clipPath id="tshape">{rects}</clipPath>
"""
    style = BAND_STYLE % (h + 120) + f"""
.blink{{animation:blink 1s steps(1) infinite}}
@keyframes blink{{50%{{opacity:0}}}}
.ticker{{animation:tick {tlen/55:.1f}s linear infinite}}
@keyframes tick{{to{{transform:translateX(-{tlen:.1f}px)}}}}
.gl{{opacity:0;animation:glitch 6s steps(1) infinite 1.4s}}
.gl2{{animation-name:glitch2}}
@keyframes glitch{{0%,90%{{opacity:0;transform:none}}91%{{opacity:.75;transform:translate(-5px,1px)}}93%{{opacity:.6;transform:translate(4px,-2px)}}95%{{opacity:.75;transform:translate(-2px,0)}}97%{{opacity:0}}}}
@keyframes glitch2{{0%,90%{{opacity:0;transform:none}}91%{{opacity:.7;transform:translate(5px,-1px)}}93%{{opacity:.5;transform:translate(-4px,2px)}}95%{{opacity:.7;transform:translate(3px,1px)}}97%{{opacity:0}}}}
.ttl{{animation:jit 6s steps(1) infinite 1.4s}}
@keyframes jit{{0%,90%{{transform:none}}91%{{transform:translateX(2px)}}93%{{transform:translateX(-1px)}}95%,100%{{transform:none}}}}
.shine{{animation:shine 6s ease-in-out infinite 1.2s}}
@keyframes shine{{0%{{transform:skewX(-20deg) translateX(0)}}25%,100%{{transform:skewX(-20deg) translateX({title_w+260:g}px)}}}}
"""
    topbar = f"""
<text x="24" y="30" font-size="12" fill="{C['cyan']}" letter-spacing="3">GRIZ://MISSION-CONTROL</text>
<text x="290" y="30" font-size="11" fill="{C['dim']}" letter-spacing="1">34.0°N 81.0°W · SOUTH CAROLINA</text>
<circle class="pulse" cx="{W-78}" cy="26" r="5" fill="{C['red']}"/>
<text x="{W-66}" y="30" font-size="12" fill="{C['red']}" letter-spacing="2">LIVE</text>
<line x1="0" x2="{W}" y1="46" y2="46" stroke="{C['edge']}"/>
<text x="{tx}" y="{by}" font-size="{fs}" fill="{C['green']}">&gt;</text>
"""
    body = topbar + title + "".join(typing) + "".join(chips) + radar + ticker
    return svg(h, body, style, defs)


# --------------------------------------------------------------------------- console

ROWS = [
    ("claude-01", "RUNNING", "green", ["refactoring code that worked fine", "renaming variables. again.", "arguing with the linter (winning)"], 7.0),
    ("claude-02", "RUNNING", "green", ["reconciling 40k rows before coffee", "turning a spreadsheet into an app", "auditing claude-01's homework"], 9.5),
    ("claude-03", "THINKING", "amber", ["writing tests for claude-01", "reading the docs so I don't have to", "planning... (ultrathink)"], 5.5),
    ("claude-04", "RUNNING", "green", ["building a tool to build tools", "opening a PR at 3:47am", "automating a 5-min task (took 6h)"], 11.0),
    ("gpu-01", "RENDERING", "magenta", ["rendering a video nobody asked for", "denoising frame 1,337 of 2,048", "fans at 100%. vibes at 100%."], 14.0),
    ("gpu-02", "SERVING", "cyan", ["serving a local model to one guy", "more VRAM: still not enough", "full weights. no quantizing."], 3.0),
    ("paul", "HUMAN", "amber", ["approving PRs from the couch", "asking for 'one more pass'", "\"make it more over the top\""], 0),
]

LOGS = [
    ("claude-04", "green", "✓", "PR opened: 'small refactor' (+4,812 −37)"),
    ("claude-03", "green", "✓", "tests green on the first try. suspicious."),
    ("gpu-01", "magenta", "!", "GPU fans entering jet-engine mode"),
    ("claude-02", "green", "✓", "replaced a 3-hour report with a script"),
    ("paul", "amber", "?", "\"can we make it more over the top?\""),
    ("claude-01", "cyan", "↻", "starting over with a better model"),
    ("claude-05", "cyan", "+", "spawned. reason: claude-04 looked lonely"),
    ("gpu-02", "green", "✓", "42 tok/s locally. paul: \"could be faster\""),
    ("claude-03", "red", "✗", "build failed. blaming the cache."),
    ("claude-03", "green", "✓", "cleared cache. build passed. vindicated."),
]


def console():
    fs = 13.5
    body = [f"""
<rect width="{W}" height="38" fill="{C['panel']}"/>
<line x1="0" x2="{W}" y1="38" y2="38" stroke="{C['edge']}"/>
<circle cx="22" cy="19" r="6" fill="#ff5f57"/><circle cx="42" cy="19" r="6" fill="#febc2e"/><circle cx="62" cy="19" r="6" fill="#28c840"/>
<text x="{W/2}" y="23" font-size="12" fill="{C['dim']}" text-anchor="middle">pgriz@griz-lab: ~/fleet — watch -n1 fleet status</text>
<text x="24" y="68" font-size="{fs}" fill="{C['green']}">❯</text>
<text x="42" y="68" font-size="{fs}" fill="{C['text']}">fleet status --all --watch</text>
<text x="{W-24}" y="68" font-size="12" fill="{C['dim']}" text-anchor="end">7 online · 0 idle · uptime 412d · load: yes</text>
<g font-size="11" fill="{C['dim']}" letter-spacing="1.5">
<text x="24" y="100">AGENT</text><text x="132" y="100">STATUS</text><text x="250" y="100">CURRENT TASK</text><text x="640" y="100">PROGRESS</text>
</g>
<line x1="24" x2="{W-24}" y1="110" y2="110" stroke="{C['edge']}" stroke-dasharray="3 3"/>
"""]
    y = 136
    for i, (name, status, col, tasks, dur) in enumerate(ROWS):
        c = C[col]
        cyc = 10.5 + i * 0.9
        body.append(f'<text x="24" y="{y}" font-size="{fs}" fill="{C["cyan"] if name != "paul" else C["amber"]}">{name}</text>')
        body.append(f'<circle class="pulse" style="animation-delay:{i*.23:.2f}s" cx="137" cy="{y-4.5}" r="4" fill="{c}"/>')
        body.append(f'<text x="148" y="{y}" font-size="11.5" fill="{c}" letter-spacing="1">{status}</text>')
        for j, task in enumerate(tasks):
            delay = -(j * cyc / 3) - i * 1.3
            body.append(f'<text class="cyc" style="animation-duration:{cyc:.1f}s;animation-delay:{delay:.2f}s" x="250" y="{y}" font-size="{fs}" fill="{C["text"]}">{t(task)}</text>')
        bx, bw = 640, 150
        body.append(f'<rect x="{bx}" y="{y-11}" width="{bw}" height="12" rx="2" fill="{C["panel"]}" stroke="{C["edge"]}"/>')
        if dur == 0:
            # the human: perpetually "almost ready"
            body.append(
                f'<rect x="{bx+1}" y="{y-10}" height="10" rx="1.5" fill="{c}" fill-opacity=".85" width="{bw*0.92:g}">'
                f'<animate attributeName="width" values="{bw*0.9:g};{bw*0.97:g};{bw*0.9:g}" dur="2.4s" repeatCount="indefinite"/></rect>'
            )
        elif name == "gpu-02":
            body.append(f'<rect x="{bx+1}" y="{y-10}" width="{bw-2}" height="10" rx="1.5" fill="url(#stripes{col})"/>')
        else:
            body.append(
                f'<rect x="{bx+1}" y="{y-10}" height="10" rx="1.5" fill="url(#stripes{col})" width="0">'
                f'<animate attributeName="width" values="0;{bw-2};{bw-2};0" keyTimes="0;.86;.97;1" dur="{dur}s" begin="-{i*1.7:.1f}s" repeatCount="indefinite"/></rect>'
            )
        for k, ch in enumerate("|/-\\"):
            body.append(f'<text class="spin" style="animation-delay:{k*0.15 - i*0.07:.2f}s" x="806" y="{y}" font-size="{fs}" fill="{c}">{t(ch)}</text>')
        y += 30

    # log tail: 3 visible lines, then a live prompt
    ly0 = y + 4
    lh = 20
    vis_top = ly0 + 30
    h = vis_top + 3 * lh + 40
    body.append(f'<line x1="0" x2="{W}" y1="{ly0}" y2="{ly0}" stroke="{C["edge"]}"/>')
    body.append(f'<rect x="0" y="{ly0}" width="{W}" height="{h-ly0}" fill="{C["panel"]}" opacity=".6"/>')
    body.append(f'<text x="24" y="{ly0+20}" font-size="10.5" fill="{C["dim"]}" letter-spacing="2">TAIL -F ~/fleet/events.log</text>')
    lines = []
    for n, (who, col, glyph, msg) in enumerate(LOGS + LOGS):
        ts = f"[03:47:{(12 + n * 7) % 60:02d}]"
        yy = vis_top + 14 + n * lh
        lines.append(
            f'<text y="{yy}" font-size="12.5"><tspan x="24" fill="{C["dim"]}">{ts}</tspan>'
            f'<tspan x="130" fill="{C["cyan"] if who != "paul" else C["amber"]}">{who}</tspan>'
            f'<tspan x="226" fill="{C[col]}">{t(glyph)}</tspan>'
            f'<tspan x="246" fill="{C["text"]}">{t(msg)}</tspan></text>'
        )
    n = len(LOGS)
    step = 100 / n
    kf = []
    for s_ in range(n):
        kf.append(f"{s_*step:.2f}%{{transform:translateY(-{s_*lh}px)}}")
        kf.append(f"{s_*step + step*0.82:.2f}%{{transform:translateY(-{s_*lh}px)}}")
    kf.append(f"100%{{transform:translateY(-{n*lh}px)}}")
    body.append(f'<clipPath id="logclip"><rect x="0" y="{vis_top}" width="{W}" height="{3*lh}"/></clipPath>')
    body.append(f'<g clip-path="url(#logclip)"><g class="logs">{"".join(lines)}</g></g>')
    py = vis_top + 3 * lh + 22
    body.append(f'<text x="24" y="{py}" font-size="{fs}" fill="{C["green"]}">❯</text>')
    body.append(f'<rect x="42" y="{py-12}" width="8" height="15" fill="{C["green"]}" class="blink"/>')

    defs = "".join(
        f'<pattern id="stripes{k}" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
        f'<rect width="10" height="10" fill="{C[k]}"/><rect width="4" height="10" fill="#000" opacity=".22"/>'
        f'<animateTransform attributeName="patternTransform" type="translate" from="0 0" to="10 0" additive="sum" dur=".8s" repeatCount="indefinite"/></pattern>'
        for k in ("green", "amber", "magenta", "cyan")
    )
    style = BAND_STYLE % (h + 120) + f"""
.cyc{{opacity:0;animation:cyc linear infinite}}
@keyframes cyc{{0%{{opacity:0}}2%,31%{{opacity:1}}33.3%,100%{{opacity:0}}}}
.spin{{opacity:0;animation:spin .6s steps(1) infinite}}
@keyframes spin{{0%{{opacity:1}}25%,100%{{opacity:0}}}}
.logs{{animation:logs {n*2.2:.1f}s infinite ease-in-out}}
@keyframes logs{{{''.join(kf)}}}
.blink{{animation:blink 1s steps(1) infinite}}
@keyframes blink{{50%{{opacity:0}}}}
"""
    return svg(h, "".join(body), style, defs)


# --------------------------------------------------------------------------- grizfetch

BEAR = [
    "..DD........DD..",
    ".DBBD......DBBD.",
    ".DBLBDDDDDDBLBD.",
    "..DBBBBBBBBBBD..",
    ".DBBBBBBBBBBBBD.",
    ".DBBBBBBBBBBBBD.",
    "DCCCCCCCCCCCCCCD",
    "DCCVCCCCCCCCVCCD",
    ".DBBBBBBBBBBBBD.",
    ".DBBBLLLLLLBBBD.",
    ".DBBLLLKKLLLBBD.",
    "..DBLLLKKLLLBD..",
    "..DBLLKLLKLLBD..",
    "...DBLLLLLLBD...",
    "....DDBBBBDD....",
    "......DDDD......",
]
BEAR_COL = {"D": "#4a2e17", "B": "#8b5a2b", "L": "#d9a066", "K": "#141414", "C": "#0f6f86", "V": "#bff8ff"}

SPECS = [
    ("OS", "Human v1.0 (heavily caffeinated)"),
    ("Location", "South Carolina, USA"),
    ("Day job", "Senior Manager @ Doeren Mayhew"),
    ("Night job", "tinkering until something breaks"),
    ("Copilot", "Claude Code — always on, never idle"),
    ("Fleet", "a few too many agents · a few too many GPUs"),
    ("Langs", "TypeScript · Python · SQL · Bash"),
    ("Stack", "Next.js · React · Node · Postgres · Tailwind"),
    ("AI", "Claude · local LLMs · ComfyUI · RAG · MCP"),
    ("Hobbies", "AI video · 3D · prediction markets"),
    ("Motto", "\"make it more over the top.\""),
    ("Uptime", "9 years on GitHub (since 2017)"),
]


def specs():
    h = 380
    px = 12
    bx, byy = 44, 80
    bear = []
    for ry, row in enumerate(BEAR):
        for rx, ch in enumerate(row):
            if ch in BEAR_COL:
                cls = ' class="eye"' if ch == "V" else ""
                bear.append(f'<rect{cls} x="{bx+rx*px}" y="{byy+ry*px}" width="{px}" height="{px}" fill="{BEAR_COL[ch]}"/>')
    visor_y = byy + 6 * px
    bear_svg = f"""
<g class="bob">
<ellipse cx="{bx+8*px}" cy="{byy+16*px+18}" rx="80" ry="7" fill="#000" opacity=".45"/>
{''.join(bear)}
<clipPath id="visor"><rect x="{bx+px}" y="{visor_y}" width="{14*px}" height="{2*px}"/></clipPath>
<g clip-path="url(#visor)"><rect class="vscan" x="{bx}" y="{visor_y}" width="{2*px}" height="{2*px}" fill="#9ff3ff" opacity=".7"/></g>
<rect x="{bx}" y="{visor_y-1}" width="{16*px}" height="{2*px+2}" fill="none" stroke="{C['cyan']}" stroke-opacity=".5"/>
</g>
<text x="{bx+8*px}" y="{byy+16*px+48}" font-size="11" fill="{C['dim']}" text-anchor="middle" letter-spacing="3">GRIZ.EXE</text>
"""
    kx, vx, y0, lh = 300, 410, 92, 21
    lines = [
        f'<text x="{kx}" y="{y0-26}" font-size="15"><tspan fill="{C["green"]}" font-weight="bold">pgriz</tspan><tspan fill="{C["text"]}">@</tspan><tspan fill="{C["cyan"]}" font-weight="bold">earth</tspan></text>',
        f'<line x1="{kx}" x2="{kx+108}" y1="{y0-17}" y2="{y0-17}" stroke="{C["dim"]}" stroke-dasharray="4 3"/>',
    ]
    for i, (k, v) in enumerate(SPECS):
        y = y0 + i * lh
        lines.append(
            f'<text class="ln" style="animation-delay:{0.15 + i*0.08:.2f}s" y="{y}" font-size="13.5">'
            f'<tspan x="{kx}" fill="{C["amber"]}" font-weight="bold">{t(k)}</tspan><tspan x="{vx}" fill="{C["text"]}">{t(v)}</tspan></text>'
        )
    pal = [C[k] for k in ("red", "amber", "green", "cyan", "magenta")] + ["#e6edf3", "#3b4a5e", "#ff8fab"]
    sy = y0 + len(SPECS) * lh + 6
    sw = [f'<rect x="{kx + i*32}" y="{sy}" width="28" height="16" rx="2" fill="{c}"/>' for i, c in enumerate(pal)]
    top = f"""
<rect width="{W}" height="38" fill="{C['panel']}"/>
<line x1="0" x2="{W}" y1="38" y2="38" stroke="{C['edge']}"/>
<text x="24" y="24" font-size="12.5"><tspan fill="{C['green']}">❯ </tspan><tspan fill="{C['text']}">grizfetch</tspan><tspan fill="{C['dim']}"> --no-filter --verbose</tspan></text>
<text x="{W-24}" y="24" font-size="11" fill="{C['dim']}" text-anchor="end" letter-spacing="2">SYSTEM PROFILE</text>
"""
    style = BAND_STYLE % (h + 120) + f"""
.bob{{animation:bob 3s ease-in-out infinite}}
@keyframes bob{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-5px)}}}}
.vscan{{animation:vscan 2.2s ease-in-out infinite alternate}}
@keyframes vscan{{from{{transform:translateX(0)}}to{{transform:translateX({14*px}px)}}}}
.eye{{animation:pulse 1.6s ease-in-out infinite}}
.ln{{animation:ln .4s ease-out both}}
@keyframes ln{{from{{opacity:0;transform:translateX(-8px)}}to{{opacity:1;transform:none}}}}
"""
    return svg(h, top + bear_svg + "".join(lines) + "".join(sw), style)


# --------------------------------------------------------------------------- buttons + footer

ICONS = {
    "linkedin": "M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 1 1 0-4.125 2.062 2.062 0 0 1 0 4.125zM7.119 20.452H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z",
    "youtube": "M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z",
}


def button(icon, label, col):
    fs = 10.5
    tw = len(label) * fs * CW * 1.15
    w = int(42 + tw + 14)
    h = 28
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img">
<style>text{{font-family:{MONO};}} .g{{animation:g 2.4s ease-in-out infinite}} @keyframes g{{50%{{stroke-opacity:.25}}}}</style>
<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="4" fill="{C['bg']}"/>
<rect x=".5" y=".5" width="32" height="{h-1}" rx="4" fill="{col}"/><rect x="20" y=".5" width="12.5" height="{h-1}" fill="{col}"/>
<g transform="translate(9,7) scale(.6)"><path d="{ICONS[icon]}" fill="#fff"/></g>
<text x="44" y="18" font-size="{fs}" font-weight="bold" fill="#e6edf3" letter-spacing="1.2" textLength="{tw:.1f}" lengthAdjust="spacing">{t(label)}</text>
<rect class="g" x=".5" y=".5" width="{w-1}" height="{h-1}" rx="4" fill="none" stroke="{col}" stroke-opacity=".9"/>
</svg>
"""


def footer():
    h = 74
    bars = []
    for i in range(16):
        x = W / 2 - 16 * 7 / 2 + i * 7
        d = 0.6 + (i * 37 % 11) / 10
        bars.append(
            f'<rect x="{x:.1f}" y="44" width="4" height="14" rx="1" fill="{C["green"]}" opacity=".8">'
            f'<animate attributeName="height" values="3;14;6;11;3" dur="{d:.2f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="y" values="55;44;52;47;55" dur="{d:.2f}s" repeatCount="indefinite"/></rect>'
        )
    body = f"""
<text x="{W/2}" y="30" font-size="12" fill="{C['dim']}" text-anchor="middle" letter-spacing="4">■ END OF TRANSMISSION ■</text>
{''.join(bars)}
<text x="24" y="58" font-size="10.5" fill="{C['dim']}">agents keep working while you're away.</text>
<text x="{W-24}" y="58" font-size="10.5" fill="{C['dim']}" text-anchor="end">built by agents. approved by a human.</text>
"""
    return svg(h, body, BAND_STYLE % (h + 120))


def main():
    OUT.mkdir(exist_ok=True)
    files = {
        "header.svg": header(),
        "console.svg": console(),
        "specs.svg": specs(),
        "footer.svg": footer(),
        "btn-linkedin.svg": button("linkedin", "LINKEDIN", "#0a66c2"),
        "btn-youtube.svg": button("youtube", "YOUTUBE · GRIZOPS", "#e62117"),
    }
    for name, content in files.items():
        (OUT / name).write_text(content)
        print(f"{name:18} {len(content)/1024:6.1f} KB")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Generate the Workshop thumbnail and in-game preview SVGs.

    python3 art/make_art.py
    inkscape art/thumb.svg   --export-type=png --export-filename=About/thumb.png   -w 512  -h 512
    inkscape art/preview.svg --export-type=png --export-filename=About/Preview.png -w 1024 -h 576

thumb.png is the Steam Workshop thumbnail (square, must stay under 1 MB).
Preview.png is shown 16:9 in the in-game Workshop Mods panel.
"""
import math
import random
from pathlib import Path

HERE = Path(__file__).parent

RED = "#E31837"
ACCENT = "#FF4A5E"  # label red, lifted for contrast on the dark background
INK = "#15191C"
HAZARD_YELLOW = "#F2C500"
HAZARD_WHITE = "#F2F4F2"
BODY = ("#8FB0B6", "#DCEFF2", "#F4FCFD")  # dark edge, base, highlight
PANEL_RED = ("#7A1618", "#B8282A")
PANEL_GREY = "#56636A"
COPPER = ("#8E4E36", "#C97C5D", "#E3A487")


def defs():
    return (
        f'<linearGradient id="body" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{BODY[0]}"/><stop offset="0.2" stop-color="{BODY[2]}"/>'
        f'<stop offset="0.7" stop-color="{BODY[1]}"/><stop offset="1" stop-color="{BODY[0]}"/></linearGradient>'
        f'<radialGradient id="copper" cx="0.35" cy="0.35" r="0.7">'
        f'<stop offset="0" stop-color="{COPPER[2]}"/><stop offset="0.6" stop-color="{COPPER[1]}"/>'
        f'<stop offset="1" stop-color="{COPPER[0]}"/></radialGradient>'
        f'<linearGradient id="panel" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="#C83234"/><stop offset="1" stop-color="{PANEL_RED[1]}"/></linearGradient>'
        f'<pattern id="hazard" patternUnits="userSpaceOnUse" width="10" height="10" patternTransform="rotate(45)">'
        f'<rect width="10" height="10" fill="{HAZARD_WHITE}"/><rect width="5" height="10" fill="{INK}"/></pattern>'
        '<radialGradient id="glow" cx="0.5" cy="0.5" r="0.5">'
        '<stop offset="0" stop-color="#FF5A3C" stop-opacity="0.35"/>'
        '<stop offset="1" stop-color="#FF5A3C" stop-opacity="0"/></radialGradient>'
    )


def arc(cx, cy, r, a0, a1):
    """SVG arc path, angles in degrees clockwise from +x."""
    x0, y0 = cx + r * math.cos(math.radians(a0)), cy + r * math.sin(math.radians(a0))
    x1, y1 = cx + r * math.cos(math.radians(a1)), cy + r * math.sin(math.radians(a1))
    large = 1 if a1 - a0 > 180 else 0
    return f"M{x0:.1f},{y0:.1f} A{r},{r} 0 {large} 1 {x1:.1f},{y1:.1f}"


def gauge(cx, cy, r=40):
    """Pressure gauge, green -> yellow -> red over a 270 degree sweep, needle pegged hard past max."""
    band = r * 0.7
    bands = "".join(
        f'<path d="{arc(cx, cy, band, a0, a1)}" fill="none" stroke="{c}" stroke-width="{r * 0.24:.1f}"/>'
        for a0, a1, c in ((135, 285, "#4FA866"), (285, 345, "#D9CF4A"), (345, 405, "#E5574F")))
    peg = 412  # past the end of the scale, against the stop pin
    tx, ty = cx + r * 0.78 * math.cos(math.radians(peg)), cy + r * 0.78 * math.sin(math.radians(peg))
    pin = (cx + r * 0.86 * math.cos(math.radians(418)), cy + r * 0.86 * math.sin(math.radians(418)))
    # jitter marks either side of the needle tip: it is buzzing against the pin
    jitter = "".join(
        f'<path d="{arc(cx, cy, r * 0.9, peg + d - 3, peg + d + 3)}" fill="none" stroke="#E5574F" '
        f'stroke-width="2" stroke-linecap="round"/>' for d in (-12, 12))
    return (f'<circle cx="{cx}" cy="{cy}" r="{r * 1.6:.1f}" fill="url(#glow)"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#F7FBFB" stroke="#2F4A48" stroke-width="{r * 0.16:.1f}"/>'
            + bands + jitter
            + f'<circle cx="{pin[0]:.1f}" cy="{pin[1]:.1f}" r="{r * 0.06:.1f}" fill="{INK}"/>'
            f'<line x1="{cx}" y1="{cy}" x2="{tx:.1f}" y2="{ty:.1f}" stroke="#5A8E92" stroke-width="{r * 0.13:.1f}" '
            f'stroke-linecap="round"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r * 0.12:.1f}" fill="#2F4A48"/>')


def knob(cx, cy, r=26):
    pts = " ".join(
        f"{cx + r * math.cos(math.radians(a)):.1f},{cy + r * 0.92 * math.sin(math.radians(a)):.1f}"
        for a in range(0, 360, 45))
    return (f'<rect x="{cx - 9}" y="{cy + 10}" width="18" height="44" fill="{COPPER[0]}"/>'
            f'<rect x="{cx - 6}" y="{cy + 10}" width="6" height="44" fill="{COPPER[1]}"/>'
            f'<polygon points="{pts}" fill="url(#copper)" stroke="{COPPER[0]}" stroke-width="2" stroke-linejoin="round"/>')


def valve_wheel(cx, cy, r=15):
    spokes = "".join(
        f'<line x1="{cx}" y1="{cy}" x2="{cx + r * 0.8 * math.cos(math.radians(a)):.1f}" '
        f'y2="{cy + r * 0.8 * math.sin(math.radians(a)):.1f}" stroke="#4A555B" stroke-width="2.5"/>'
        for a in (45, 135, 225, 315))
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#8E9AA0" stroke="#4A555B" stroke-width="2"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r * 0.78:.1f}" fill="none" stroke="#B4C0C5" stroke-width="1.5"/>'
            + spokes + f'<circle cx="{cx}" cy="{cy}" r="{r * 0.25:.1f}" fill="#B4C0C5" stroke="#4A555B"/>')


def arrow_left(x, cy, bar_at_tip=False):
    """Yellow arrow pointing left with a bar behind its tail (leaving) or in front of its tip (arriving).

    x is the left edge of the whole glyph.
    """
    y = HAZARD_YELLOW
    tip = x + 8 if bar_at_tip else x
    bar = x if bar_at_tip else x + 34
    return (f'<polygon points="{tip},{cy} {tip + 14},{cy - 12} {tip + 14},{cy - 5} {tip + 30},{cy - 5} {tip + 30},{cy + 5} '
            f'{tip + 14},{cy + 5} {tip + 14},{cy + 12}" fill="{y}"/>'
            f'<rect x="{bar}" y="{cy - 12}" width="4" height="24" fill="{y}"/>')


def furnace(ox, oy, scale):
    """Advanced Furnace front, drawn 320 x 380 in its own coordinates, top-left at (ox, oy)."""
    # Round chamber seen end-on, with the console box standing in front of it.
    body = ('<circle cx="160" cy="200" r="158" fill="url(#body)" stroke="#5F7C82" stroke-width="3"/>'
            '<circle cx="160" cy="200" r="140" fill="none" stroke="#FFFFFF" stroke-opacity="0.5" stroke-width="2"/>'
            '<circle cx="160" cy="200" r="132" fill="none" stroke="#8FB0B6" stroke-width="3"/>'
            '<rect x="62" y="134" width="210" height="250" rx="6" fill="#000" opacity="0.25"/>'
            '<rect x="56" y="128" width="210" height="252" rx="6" fill="url(#body)" stroke="#5F7C82" stroke-width="3"/>')
    feet = "".join(
        f'<rect x="{x}" y="356" width="44" height="40" rx="3" fill="#E9F5F6" stroke="#5F7C82" stroke-width="2"/>'
        for x in (26, 250))
    top = knob(92, 104) + knob(228, 104) + gauge(160, 96)
    vents = "".join(f'<rect x="{84 + i * 9}" y="168" width="5" height="34" rx="1" fill="#4A0E10"/>' for i in range(6))
    switch = ('<rect x="140" y="172" width="48" height="26" rx="2" fill="#2A1012"/>'
              '<rect x="144" y="176" width="40" height="18" rx="1" fill="#3FD45A"/>'
              '<rect x="144" y="176" width="40" height="6" rx="1" fill="#8AF09A"/>')
    button = ('<rect x="198" y="160" width="46" height="46" fill="url(#hazard)" stroke="#2A1012" stroke-width="2"/>'
              f'<rect x="207" y="169" width="28" height="28" rx="2" fill="#D02A2A" stroke="{HAZARD_YELLOW}" stroke-width="2.5"/>')
    # Slot at the top holding a striped crossbar; the arm runs down the left side of the column.
    lever = ('<rect x="86" y="220" width="46" height="128" fill="#3F4A50"/>'
             '<rect x="92" y="226" width="36" height="40" fill="#15191C"/>'
             '<rect x="91" y="238" width="7" height="104" rx="1" fill="#9AB0B6" stroke="#5F7C82" stroke-width="1"/>'
             '<rect x="91" y="238" width="34" height="12" rx="3" fill="url(#hazard)" stroke="#22292D" stroke-width="1"/>')
    controls = (arrow_left(150, 246) + valve_wheel(214, 246) + arrow_left(150, 286, bar_at_tip=True)
                + valve_wheel(214, 286))
    screen_lines = "".join(
        f'<rect x="{164 + c * 24}" y="{318 + r * 7}" width="{18 if (r + c) % 3 else 12}" height="2.5" fill="#C9F5CF"/>'
        for r in range(4) for c in range(3))
    screen = ('<rect x="142" y="308" width="98" height="40" rx="3" fill="#3FAE4F" stroke="#2D3A3F" stroke-width="3"/>'
              '<text x="151" y="330" font-family="DejaVu Sans" font-weight="bold" font-size="13" fill="#C9F5CF">i</text>'
              + screen_lines)
    panel = (f'<rect x="72" y="150" width="182" height="210" rx="4" fill="url(#panel)" stroke="{PANEL_RED[0]}" stroke-width="3"/>'
             + vents + switch + button
             + f'<rect x="80" y="214" width="166" height="140" fill="{PANEL_GREY}" stroke="#2D3A3F" stroke-width="2"/>'
             + lever + controls + screen)
    return (f'<g transform="translate({ox},{oy}) scale({scale})">'
            f'<ellipse cx="160" cy="392" rx="170" ry="10" fill="#000" opacity="0.35"/>'
            + feet + body + panel + top + '</g>')


# Pictograms are drawn in a local box of about -40..40 on both axes, centred on the origin.

def picto_explosive():
    rng = random.Random(11)
    px, py = 0, -6
    burst = []
    for i in range(18):
        a = math.pi * 2 * i / 18 - math.pi / 2
        rr = rng.uniform(19, 26) if i % 2 == 0 else rng.uniform(8, 11)
        burst.append(f"{px + rr * math.cos(a):.1f},{py + rr * math.sin(a):.1f}")
    fragments = []
    for deg, d, k in ((-160, 26, 4), (-125, 27, 5), (-90, 28, 4), (-55, 27, 5), (-20, 26, 4)):
        a = math.radians(deg)
        fx, fy = px + d * math.cos(a), py + d * math.sin(a)
        fragments.append(f'<polygon points="{fx - k:.1f},{fy:.1f} {fx:.1f},{fy - k * 1.2:.1f} {fx + k:.1f},'
                         f'{fy + k * 0.3:.1f} {fx - k * 0.2:.1f},{fy + k:.1f}" fill="{INK}"/>')
    return (f'<polygon points="{" ".join(burst)}" fill="{INK}"/>'
            f'<circle cx="0" cy="16" r="13" fill="{INK}"/>' + "".join(fragments))


def picto_corrosive():
    """A tilted test tube dripping onto a bar that has a bite eaten out of it."""
    tube = (f'<g transform="translate(-8,-14) rotate(-50)">'
            f'<path d="M-6,-24 L-6,6 A6,6 0 0 0 6,6 L6,-24" fill="none" stroke="{INK}" stroke-width="4"/>'
            f'<path d="M-4,-4 L-4,6 A4,4 0 0 0 4,6 L4,-4 Z" fill="{INK}"/>'
            f'<line x1="-9" y1="-24" x2="9" y2="-24" stroke="{INK}" stroke-width="4" stroke-linecap="round"/></g>')
    drops = "".join(
        f'<path d="M{x},{y - 5} Q{x + 4},{y} {x},{y + 3} Q{x - 4},{y} {x},{y - 5} Z" fill="{INK}" '
        f'transform="scale(1.3) translate({-x * 0.23:.1f},{-y * 0.23:.1f})"/>'
        for x, y in ((8, -2), (12, 8)))
    bar = (f'<path d="M-30,18 L2,18 L5,23 L9,19 L13,24 L17,18 L30,18 L30,30 L-30,30 Z" fill="{INK}"/>'
           f'<circle cx="13" cy="15" r="2.5" fill="{INK}"/><circle cx="20" cy="12" r="1.8" fill="{INK}"/>')
    return tube + drops + bar


def gear(cx, cy, r, teeth, rot=0):
    pts = []
    n = teeth * 4
    for i in range(n):
        a = 2 * math.pi * i / n + math.radians(rot)
        rr = r if i % 4 in (1, 2) else r * 0.76
        pts.append(f"{cx + rr * math.cos(a):.1f},{cy + rr * math.sin(a):.1f}")
    return (f'<polygon points="{" ".join(pts)}" fill="{INK}"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r * 0.36:.1f}" fill="#FFFFFF"/>')


def picto_hand_gears():
    """A hand reaching in from the upper left, fingertips caught where two gears mesh."""
    hand = (f'<g transform="translate(-15,-16) rotate(42) scale(1.1)" fill="{INK}">'
            '<rect x="-16" y="-9" width="10" height="18" rx="1"/>'
            '<rect x="-5" y="-10" width="18" height="20" rx="6"/>'
            '<rect x="2" y="-15" width="10" height="6" rx="3" transform="rotate(-25 2 -12)"/>'
            '<rect x="10" y="-9" width="17" height="5" rx="2.5"/>'
            '<rect x="10" y="-2.5" width="19" height="5" rx="2.5"/>'
            '<rect x="10" y="4" width="16" height="5" rx="2.5"/></g>')
    return hand + gear(-7, 15, 19, 10, 8) + gear(19, -7, 15, 8, 0)


def picto_fragile():
    """Broken wine glass, as on shipping labels."""
    return (f'<path d="M-15,-30 L15,-30 Q16,-2 2,3 L2,20 L12,26 L-12,26 L-2,20 L-2,3 Q-16,-2 -15,-30 Z" fill="{INK}"/>'
            '<polyline points="-3,-31 3,-21 -4,-13 3,-6 -1,0" fill="none" stroke="#FFFFFF" stroke-width="3" '
            'stroke-linejoin="miter"/>'
            f'<polygon points="18,-30 24,-26 20,-22" fill="{INK}"/><polygon points="22,-16 27,-14 23,-11" fill="{INK}"/>')


def picto_flammable():
    return (f'<path d="M0,-32 C12,-17 21,-6 16,9 C13,18 7,22 0,22 C-8,22 -18,16 -17,5 C-16,-6 -7,-11 -6,-21 '
            f'C-1,-14 -1,-8 3,-4 C5,-14 3,-23 0,-32 Z" fill="{INK}"/>'
            f'<path d="M0,2 C5,8 6,13 4,17 C2,19 -3,19 -5,16 C-7,12 -4,7 0,2 Z" fill="#FFFFFF"/>'
            f'<rect x="-24" y="25" width="48" height="6" rx="1" fill="{INK}"/>')


def picto_toxic():
    bones = "".join(
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>'
        f'<circle cx="{x1}" cy="{y1 - 3}" r="3.5" fill="{INK}"/><circle cx="{x1 - 3 if x1 < 0 else x1 + 3}" cy="{y1 + 1}" r="3.5" fill="{INK}"/>'
        f'<circle cx="{x2}" cy="{y2 + 3}" r="3.5" fill="{INK}"/><circle cx="{x2 + 3 if x2 > 0 else x2 - 3}" cy="{y2 - 1}" r="3.5" fill="{INK}"/>'
        for x1, y1, x2, y2 in ((-22, 12, 22, 30), (22, 12, -22, 30)))
    skull = (f'<circle cx="0" cy="-12" r="16" fill="{INK}"/>'
             f'<rect x="-9" y="-2" width="18" height="12" rx="3" fill="{INK}"/>'
             '<circle cx="-6.5" cy="-12" r="5" fill="#FFFFFF"/><circle cx="6.5" cy="-12" r="5" fill="#FFFFFF"/>'
             '<polygon points="0,-6 -2.5,-1 2.5,-1" fill="#FFFFFF"/>'
             '<line x1="-4" y1="4" x2="-4" y2="10" stroke="#FFFFFF" stroke-width="1.6"/>'
             '<line x1="0" y1="4" x2="0" y2="10" stroke="#FFFFFF" stroke-width="1.6"/>'
             '<line x1="4" y1="4" x2="4" y2="10" stroke="#FFFFFF" stroke-width="1.6"/>')
    return bones + skull


PICTOS = {
    "explosive": picto_explosive, "corrosive": picto_corrosive, "hands": picto_hand_gears,
    "fragile": picto_fragile, "flammable": picto_flammable, "toxic": picto_toxic,
}


def danger_label(cx, cy, w, kind, angle=0.0):
    """ANSI-style DANGER label: red header with a warning triangle, ringed pictogram, no caption.

    Drawn 120 wide in its own coordinates and scaled to w, centred on (cx, cy).
    """
    W, H = 120, 136
    header = 30
    tri = "11,31 23,10 35,31"
    body = (f'<rect x="0" y="0" width="{W}" height="{H}" rx="5" fill="#FFFFFF" stroke="{INK}" stroke-width="3"/>'
            f'<rect x="5" y="5" width="{W - 10}" height="{H - 10}" fill="none" stroke="{INK}" stroke-width="1.5"/>'
            f'<rect x="5" y="5" width="{W - 10}" height="{header}" fill="{RED}"/>'
            f'<line x1="5" y1="{5 + header}" x2="{W - 5}" y2="{5 + header}" stroke="{INK}" stroke-width="1.5"/>'
            f'<polygon points="{tri}" fill="#FFFFFF" stroke="#FFFFFF" stroke-width="2" stroke-linejoin="round"/>'
            f'<rect x="21.6" y="16" width="2.8" height="8.5" rx="1.2" fill="{RED}"/>'
            f'<circle cx="23" cy="27.6" r="1.7" fill="{RED}"/>'
            f'<text x="40" y="29" font-family="DejaVu Sans" font-weight="bold" font-size="20" fill="#FFFFFF" '
            f'textLength="{W - 50}" lengthAdjust="spacingAndGlyphs">DANGER</text>'
            f'<circle cx="{W / 2}" cy="{5 + header + 48}" r="41" fill="#FFFFFF" stroke="{INK}" stroke-width="5"/>'
            f'<g transform="translate({W / 2},{5 + header + 48}) scale(0.95)">{PICTOS[kind]()}</g>')
    s = w / W
    return (f'<g transform="translate({cx:.1f},{cy:.1f}) rotate({angle}) scale({s:.3f}) translate({-W / 2},{-H / 2})">'
            f'<rect x="3" y="5" width="{W}" height="{H}" rx="5" fill="#000" opacity="0.4"/>{body}</g>')


def label_row(kinds, y_top, width, total_width):
    """Labels spread evenly across total_width, tops at y_top, each tilted a little like a sticker."""
    n = len(kinds)
    gap = (total_width - n * width) / (n + 1)
    h = width * 136 / 120
    tilts = [-3, 2, -1.5, 3, -2.5, 1.5]
    return "".join(
        danger_label(gap + width / 2 + i * (width + gap), y_top + h / 2, width, kind, tilts[i % len(tilts)])
        for i, kind in enumerate(kinds))


def background(w, h, cx, cy):
    grid = "".join(
        f'<line x1="{i}" y1="0" x2="{i}" y2="{h}" stroke="#fff" stroke-opacity="0.04"/>' for i in range(0, w + 1, 32))
    grid += "".join(
        f'<line x1="0" y1="{i}" x2="{w}" y2="{i}" stroke="#fff" stroke-opacity="0.04"/>' for i in range(0, h + 1, 32))
    return (f'<radialGradient id="bg" cx="{cx}" cy="{cy}" r="80%"><stop offset="0" stop-color="#22374A"/>'
            f'<stop offset="1" stop-color="#0C141C"/></radialGradient>', f'<rect width="{w}" height="{h}" fill="url(#bg)"/>{grid}')


def title(x, y, size, subtitle=False):
    out = (f'<text x="{x}" y="{y}" text-anchor="middle" font-family="DejaVu Sans" font-weight="bold" '
           f'font-size="{size}" fill="#FFFFFF" letter-spacing="1">Pb_Magnet\'s</text>'
           f'<text x="{x}" y="{y + size * 1.18:.0f}" text-anchor="middle" font-family="DejaVu Sans" font-weight="bold" '
           f'font-size="{size}" fill="{ACCENT}" letter-spacing="1">Recipes</text>')
    if subtitle:
        out += (f'<text x="{x}" y="{y + size * 1.8:.0f}" text-anchor="middle" font-family="DejaVu Sans" '
                f'font-size="{size * 0.31:.0f}" fill="#9FB0BF" letter-spacing="3">METHANE GOES WHERE?</text>')
    return out


def svg(w, h, body, bg_centre):
    grad, bg = background(w, h, *bg_centre)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'<defs>{defs()}{grad}</defs>{bg}{body}</svg>\n')


def main():
    thumb = svg(512, 512, title(256, 56, 50, subtitle=True) + furnace(256 - 0.55 * 160, 154, 0.55)
                + label_row(["explosive", "corrosive", "hands", "fragile"], 352, 112, 512), ("50%", "45%"))
    (HERE / "thumb.svg").write_text(thumb)

    preview = svg(1024, 576, furnace(250 - 0.95 * 160, 14, 0.95) + title(720, 160, 64, subtitle=True)
                  + label_row(["explosive", "flammable", "corrosive", "toxic", "hands", "fragile"], 396, 140, 1024),
                  ("30%", "40%"))
    (HERE / "preview.svg").write_text(preview)


if __name__ == "__main__":
    main()

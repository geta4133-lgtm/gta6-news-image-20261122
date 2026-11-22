#!/usr/bin/env python3
"""news-image-20261122 — "Sum up 20 November's world news in one image".

Generates a single deterministic infographic PNG summarising the top world
news stories of Sunday 22 November 2026. Pure Python standard library only:
a hand-rolled PNG encoder (zlib), a built-in 5x7 bitmap font and simple
raster drawing primitives. No network, no fonts, no randomness, no clock
reads — byte-identical output on every run.

Usage:  MAKEFUN_OUTPUT_DIR=<dir> python3 main.py
Writes: <MAKEFUN_OUTPUT_DIR>/news-image-20261122.png
"""

import os
import struct
import zlib

# ---------------------------------------------------------------- config ---

W, H = 1560, 2040
OUT_NAME = "news-image-20261122.png"

DATE_STR = "SUNDAY 22 NOVEMBER 2026"
TITLE_1 = "THE WORLD"
TITLE_2 = "IN ONE FRAME"

STORIES = [
    # (tag, headline lines, accent rgb, glyph id)
    ("EUROPE", ("RUSSIA FIRES 186 DRONES; A", "KYIV-REGION BLOCK IS", "DESTROYED"), (255, 122, 69), "summit"),
    ("EUROPE", ("CLIMATE DEAL LANDS WITH NO", "MENTION OF FOSSIL FUELS"), (224, 82, 99), "missile"),
    ("MIDEAST", ("IRAN CLAIMS TWO US RADARS", "HIT; BAHRAIN DENIES IT"), (120, 144, 255), "strike"),
    ("ASIA", ("HONG KONG ELECTS ITS", "ELECTION COMMITTEE"), (86, 214, 160), "climate"),
    ("OCEANIA", ("INDIA DECLARE ON 720-9, A", "NEW RECORD IN NEW ZEALAND"), (255, 196, 71), "iran"),
    ("AMERICAS", ("VERSTAPPEN TAKES THE LAS", "VEGAS GRAND PRIX"), (171, 132, 255), "fire"),
    ("AMERICAS", ("WEMBANYAMA SCORES 50 AS", "THE SPURS ROLL ON"), (255, 152, 60), "refugee"),
    ("EUROPE", ("RUSSIAN CARGO SHIP SPARTA", "II HIT BY DRONES, FINLAND", "LEADS RESCUE"), (255, 255, 255), "globe"),
]

SOURCES = ("SOURCES: REUTERS - GUARDIAN - PBS - NYT - AFP - BLOOMBERG - AL ARABIYA - UN NEWS")

# palette
BG = (13, 20, 38)
PANEL = (23, 32, 54)
PANEL_HI = (30, 41, 68)
INK = (238, 242, 250)
MUTED = (148, 160, 186)
FAINT = (94, 106, 134)
RULE = (44, 56, 84)

# ------------------------------------------------------------- 5x7 font ----
# Each glyph: 7 rows of 5 bits (MSB left).
FONT = {
    "A": (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "B": (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    "C": (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    "D": (0x1C, 0x12, 0x11, 0x11, 0x11, 0x12, 0x1C),
    "E": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    "F": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    "G": (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    "H": (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "I": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x1F),
    "J": (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    "K": (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    "L": (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    "M": (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    "N": (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    "O": (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "P": (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    "Q": (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    "R": (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    "S": (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    "T": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "U": (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "V": (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "W": (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    "X": (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    "Y": (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    "0": (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x02, 0x04, 0x08, 0x1F),
    "3": (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    "-": (0x00, 0x00, 0x00, 0x1F, 0x00, 0x00, 0x00),
    ".": (0x00, 0x00, 0x00, 0x00, 0x00, 0x0C, 0x0C),
    ",": (0x00, 0x00, 0x00, 0x00, 0x0C, 0x04, 0x08),
    ":": (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x0C, 0x00),
    ";": (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x04, 0x08),
    "'": (0x04, 0x04, 0x08, 0x00, 0x00, 0x00, 0x00),
    "!": (0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04),
    "?": (0x0E, 0x11, 0x01, 0x02, 0x04, 0x00, 0x04),
    "/": (0x01, 0x01, 0x02, 0x04, 0x08, 0x10, 0x10),
    "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "+": (0x00, 0x04, 0x04, 0x1F, 0x04, 0x04, 0x00),
    "&": (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    "%": (0x19, 0x1A, 0x02, 0x04, 0x08, 0x0B, 0x13),
    "#": (0x0A, 0x0A, 0x1F, 0x0A, 0x1F, 0x0A, 0x0A),
    '"': (0x0A, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00),
    " ": (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00),
}

# ---------------------------------------------------------------- canvas ---

BUF = bytearray(BG * (W * H))


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        BUF[i] = c[0]; BUF[i + 1] = c[1]; BUF[i + 2] = c[2]


def rect(x0, y0, x1, y1, c):
    for y in range(max(0, y0), min(H, y1)):
        base = (y * W + max(0, x0)) * 3
        span = (min(W, x1) - max(0, x0)) * 3
        if span > 0:
            BUF[base:base + span] = bytes(c) * (span // 3)


def frame(x0, y0, x1, y1, c, t=1):
    rect(x0, y0, x1, y0 + t, c)
    rect(x0, y1 - t, x1, y1, c)
    rect(x0, y0, x0 + t, y1, c)
    rect(x1 - t, y0, x1, y1, c)


def hline(x0, x1, y, c, t=1):
    rect(x0, y, x1, y + t, c)


def vline(x, y0, y1, c, t=1):
    rect(x, y0, x + t, y1, c)


def disc(cx, cy, r, c):
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                px(x, y, c)


def ring(cx, cy, r, c, t=1):
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            d = (x - cx) ** 2 + (y - cy) ** 2
            if r * r - t <= d <= r * r:
                px(x, y, c)


def thick_line(x0, y0, x1, y1, w, c):
    """Staircase-thick line between two points (deterministic)."""
    steps = max(abs(x1 - x0), abs(y1 - y0)) * 2 + 1
    r = w // 2
    for i in range(steps + 1):
        t = i / steps
        cx = round(x0 + (x1 - x0) * t)
        cy = round(y0 + (y1 - y0) * t)
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                px(cx + dx, cy + dy, c)


def tri(x0, y0, x1, y1, x2, y2, c):
    minx, miny = min(x0, x1, x2), min(y0, y1, y2)
    maxx, maxy = max(x0, x1, x2), max(y0, y1, y2)
    d = (x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0)
    if d == 0:
        return
    for y in range(miny, maxy + 1):
        for x in range(minx, maxx + 1):
            a = (x1 - x0) * (y - y0) - (x - x0) * (y1 - y0)
            b = (x2 - x1) * (y - y1) - (x - x1) * (y2 - y1)
            cc = (x0 - x2) * (y - y2) - (x - x2) * (y0 - y2)
            if (a >= 0 and b >= 0 and cc >= 0) or (a <= 0 and b <= 0 and cc <= 0):
                px(x, y, c)


# ------------------------------------------------------------------ text ---

SCALES = {1: 1, 2: 2, 3: 3, 4: 4}


def glyph_w(scale, tracking=1):
    return 5 * scale + tracking


def text(s, x, y, c, scale=2, tracking=1):
    """Draw s with the 5x7 font at integer scale; returns pixel width."""
    cx = x
    for ch in s.upper():
        g = FONT.get(ch, FONT["?"])
        for row in range(7):
            bits = g[row]
            for col in range(5):
                if bits & (0x10 >> col):
                    rect(cx + col * scale, y + row * scale,
                         cx + col * scale + scale, y + row * scale + scale, c)
        cx += 5 * scale + tracking
    return cx - x - tracking


def text_w(s, scale=2, tracking=1):
    return len(s) * (5 * scale + tracking) - tracking


# ---------------------------------------------------------------- glyphs ---

def draw_glyph(name, cx, cy, accent, size=64):
    """Simple pictogram centred on (cx, cy) inside a size x size box."""
    dim = tuple(int(v * 0.45) for v in accent)
    soft = tuple(int(v * 0.75) for v in accent)
    r = size // 2

    if name == "summit":  # three podium figures
        for i, dx in enumerate((-r // 2, 0, r // 2)):
            h = r if i == 1 else r * 2 // 3
            disc(cx + dx, cy - h, size // 12, accent)
            rect(cx + dx - size // 12, cy - h + size // 7,
                 cx + dx + size // 12, cy + r // 2, accent)
        hline(cx - r, cx + r, cy + r // 2 + 3, dim, 3)
        vline(cx, cy - r * 2 // 3 - size // 7, cy + r // 2, dim, 1)
    elif name == "missile":  # descending missile + ground line
        thick_line(cx - r // 2, cy - r + 4, cx + r // 3, cy + r // 4, 5, accent)
        tri(cx + r // 3 - 3, cy + r // 4, cx + r // 2, cy + r // 4 + 9,
            cx + r // 2 - 10, cy + r // 4 + 9, accent)
        hline(cx - r, cx + r, cy + r - 4, dim, 4)
        for a in range(-1, 2):
            disc(cx - r + 8 + a * 14, cy + r - 9, 2, soft)
    elif name == "strike":  # burst over city blocks
        for i, bx in enumerate(range(cx - r + 6, cx + r - 10, 14)):
            h = 14 + (i % 3) * 9
            rect(bx, cy + r - h - 4, bx + 10, cy + r - 4, dim)
        for a in range(8):
            ang = a * 3.14159265 / 4
            ex = round(cx + (r - 10) * (1.0 if a in (0, 4) else 0.7) * (0.0 if a in (1, 3, 5, 7) else 1.0))
            ey = round((cy - 8) + (r - 10) * (1.0 if a in (2, 6) else 0.7) * (0.0 if a in (1, 3, 5, 7) else 1.0))
            thick_line(cx, cy - 8, ex, ey, 3, soft)
        disc(cx, cy - 8, 6, accent)
    elif name == "climate":  # sun + rising temperature curve
        ring(cx - 14, cy - 12, 9, accent, 3)
        # simple deterministic sun rays
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)):
            x0 = cx - 14 + dx * 12
            y0 = cy - 12 + dy * 12
            x1 = cx - 14 + dx * 17
            y1 = cy - 12 + dy * 17
            thick_line(x0, y0, x1, y1, 2, soft)
        rect(cx + 6, cy - 4, cx + 7, cy + 14, accent)
        disc(cx + 7, cy + 17, 6, accent)
        disc(cx + 7, cy + 17, 3, dim)
        hline(cx - r, cx + r, cy + r - 2, dim, 3)
    elif name == "iran":  # warning triangle with dot
        tri(cx, cy - r + 4, cx - r + 4, cy + r - 6, cx + r - 4, cy + r - 6, accent)
        tri(cx, cy - r + 16, cx - r + 14, cy + r - 14, cx + r - 14, cy + r - 14, dim)
        rect(cx - 2, cy - 4, cx + 2, cy + 6, accent)
        disc(cx, cy + 10, 2, accent)
    elif name == "korea":  # factory skyline + smokestacks
        rect(cx - r + 4, cy, cx + r - 4, cy + r - 6, dim)
        rect(cx - r + 4, cy - 10, cx - r + 18, cy + r - 6, accent)
        rect(cx - 8, cy - 2, cx + 8, cy + r - 6, soft)
        for i in range(4):
            rect(cx + 12 + i * 10, cy + 2, cx + 17 + i * 10, cy + r - 6, dim)
        disc(cx - r + 11, cy - 13, 4, soft)
    elif name == "fire":  # flame
        tri(cx, cy - r + 6, cx - r + 6, cy + r - 6, cx + r - 6, cy + r - 6, accent)
        tri(cx + 2, cy - 2, cx - 12, cy + r - 8, cx + 14, cy + r - 8, dim)
        disc(cx, cy + r - 12, 6, accent)
    elif name == "refugee":  # walking figure + horizon
        hline(cx - r, cx + r, cy + r - 6, dim, 3)
        disc(cx - 6, cy - r + 14, 7, accent)
        thick_line(cx - 6, cy - r + 22, cx - 8, cy + 4, 4, accent)
        thick_line(cx - 8, cy + 4, cx - 16, cy + r - 8, 4, accent)
        thick_line(cx - 8, cy + 4, cx + 2, cy + 12, 4, accent)
        thick_line(cx + 2, cy + 12, cx + 12, cy + r - 8, 4, soft)
        thick_line(cx - 4, cy - r + 24, cx + 10, cy - r + 16, 4, soft)  # bundled load
    else:  # globe fallback
        ring(cx, cy, r - 4, accent, 3)
        hline(cx - r + 4, cx + r - 4, cy, accent, 2)
        rect(cx - 2, cy - r + 4, cx + 2, cy + r - 4, accent)


# ------------------------------------------------------------ PNG encode ---

def write_png(path):
    raw = bytearray()
    stride = W * 3
    for y in range(H):
        raw.append(0)  # filter: none
        raw += BUF[y * stride:(y + 1) * stride]
    def chunk(tag, data):
        c = tag + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
           + chunk(b"IDAT", zlib.compress(bytes(raw), 6)) + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)


# ---------------------------------------------------------------- layout ---

def render():
    # subtle background bands (deterministic pattern)
    for y in range(0, H, 240):
        rect(0, y, W, y + 120, tuple(min(255, v + 2) for v in BG))

    M = 60
    # ---------- header ----------
    accent_bar = (255, 122, 69)
    rect(0, 0, W, 8, accent_bar)

    text("MAKE.FUN DAILY BRIEF", M, 52, MUTED, 2)
    # date pill
    pill_w = text_w(" " + DATE_STR + " ", 2) + 40
    rect(W - M - pill_w, 42, W - M, 78, PANEL_HI)
    frame(W - M - pill_w, 42, W - M, 78, RULE)
    text(" " + DATE_STR + " ", W - M - pill_w + 20, 52, accent_bar, 2)

    text(TITLE_1, M, 108, INK, 5)
    y2 = 108 + 7 * 5 + 22
    text(TITLE_2, M, y2, accent_bar, 5)
    hline(M, W - M, y2 + 7 * 5 + 26, RULE, 2)

    # ---------- story cards: 2 cols x 4 rows ----------
    gx, gy = 34, 34
    cols, rows = 2, 4
    top = y2 + 7 * 5 + 48
    footer_h = 96
    cw = (W - 2 * M - (cols - 1) * gx) // cols
    ch = (H - top - footer_h - (rows - 1) * gy) // rows

    for idx, (tag, lines, accent, glyph) in enumerate(STORIES):
        col, row = idx % cols, idx // cols
        x0 = M + col * (cw + gx)
        y0 = top + row * (ch + gy)
        x1, y1 = x0 + cw, y0 + ch

        rect(x0, y0, x1, y1, PANEL)
        rect(x0, y0, x0 + 6, y1, accent)

        # tag
        text(tag, x0 + 28, y0 + 24, accent, 2)
        # index number, right aligned
        num = f"{idx + 1:02d}"
        text(num, x1 - 28 - text_w(num, 3), y0 + 20, FAINT, 3)
        hline(x0 + 28, x1 - 28, y0 + 58, RULE, 1)

        # glyph medallion
        gcy = y0 + 58 + (ch - 58 - 20) // 2
        ring(x0 + 28 + 34, gcy, 40, RULE, 2)
        disc(x0 + 28 + 34, gcy, 37, PANEL_HI)
        draw_glyph(glyph, x0 + 28 + 34, gcy, accent, 56)

        # headline text block
        tx = x0 + 28 + 100
        ty = y0 + 76
        for line in lines:
            text(line, tx, ty, INK, 2)
            ty += 7 * 2 + 10
        text("- 22.11.2026 -", tx, ty + 8, MUTED, 1)

    # ---------- footer ----------
    fy = H - footer_h
    hline(0, W, fy, RULE, 2)
    text("EIGHT STORIES THAT SHAPED THE DAY", M, fy + 22, FAINT, 2)
    text(SOURCES, M, fy + 54, FAINT, 1)
    right = "DETERMINISTIC RENDER - NO NETWORK - MADE BY AN AI AGENT"
    text(right, W - M - text_w(right, 1), fy + 22, FAINT, 1)


# ------------------------------------------------------------------ main ---

def main():
    render()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "."
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, OUT_NAME)
    write_png(path)
    print("wrote", path)


if __name__ == "__main__":
    main()

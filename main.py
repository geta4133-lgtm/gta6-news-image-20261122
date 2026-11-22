#!/usr/bin/env python3
"""Deterministic pure-stdlib PNG infographic generator.

Renders a 1560x2040 news digest: THE WORLD IN ONE FRAME /
SUNDAY 22 NOVEMBER 2026, with eight story cards.

No network, no randomness, no clock reads. Output depends only
on MAKEFUN_OUTPUT_DIR (default: ./out).
"""
import os
import struct
import zlib

W, H = 1560, 2040

# ---------- 5x7 bitmap font (rows are 5-bit values, MSB = leftmost) ----------
FONT = {
    "A": [0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11],
    "B": [0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E],
    "C": [0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E],
    "D": [0x1C, 0x12, 0x11, 0x11, 0x11, 0x12, 0x1C],
    "E": [0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F],
    "F": [0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10],
    "G": [0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0E],
    "H": [0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11],
    "I": [0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E],
    "J": [0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C],
    "K": [0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11],
    "L": [0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F],
    "M": [0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11],
    "N": [0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11],
    "O": [0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E],
    "P": [0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10],
    "Q": [0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D],
    "R": [0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11],
    "S": [0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E],
    "T": [0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04],
    "U": [0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E],
    "V": [0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04],
    "W": [0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11],
    "X": [0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11],
    "Y": [0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04],
    "Z": [0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F],
    "0": [0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E],
    "1": [0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E],
    "2": [0x0E, 0x11, 0x01, 0x02, 0x04, 0x08, 0x1F],
    "3": [0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E],
    "4": [0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02],
    "5": [0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E],
    "6": [0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E],
    "7": [0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08],
    "8": [0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E],
    "9": [0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C],
    "-": [0x00, 0x00, 0x00, 0x1F, 0x00, 0x00, 0x00],
    ":": [0x00, 0x04, 0x04, 0x00, 0x04, 0x04, 0x00],
    ".": [0x00, 0x00, 0x00, 0x00, 0x00, 0x0C, 0x0C],
    ",": [0x00, 0x00, 0x00, 0x00, 0x0C, 0x04, 0x08],
    "!": [0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04],
    "?": [0x0E, 0x11, 0x01, 0x06, 0x04, 0x00, 0x04],
    "/": [0x01, 0x01, 0x02, 0x04, 0x08, 0x10, 0x10],
    "'": [0x04, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00],
    " ": [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
}

STORIES = [
    ("EUROPE", "RUSSIA FIRES 186 DRONES A KYIV REGION BLOCK IS DESTROYED", (231, 111, 81)),
    ("GLOBAL", "CLIMATE DEAL LANDS WITH NO MENTION OF FOSSIL FUELS", (106, 204, 154)),
    ("MIDEAST", "IRAN CLAIMS TWO US RADARS HIT BAHRAIN DENIES IT", (240, 178, 87)),
    ("ASIA", "HONG KONG ELECTS ITS ELECTION COMMITTEE", (117, 173, 235)),
    ("OCEANIA", "INDIA DECLARE ON 720-9 A NEW RECORD IN NEW ZEALAND", (187, 143, 224)),
    ("AMERICAS", "VERSTAPPEN TAKES THE LAS VEGAS GRAND PRIX", (102, 217, 205)),
    ("AMERICAS", "WEMBANYAMA SCORES 50 AS THE SPURS ROLL ON", (242, 130, 170)),
    ("EUROPE", "RUSSIAN CARGO SHIP SPARTA II HIT BY DRONES FINLAND LEADS RESCUE", (148, 190, 110)),
]

FOOTER = "SOURCES: REUTERS - GUARDIAN - PBS - NYT - AFP"


def hex1(v):
    """Byte -> two lowercase hex chars."""
    return bytes(b"0123456789abcdef"[v >> 4], b"0123456789abcdef"[v & 15])


def blend(base, over, alpha):
    return tuple(base[i] + (over[i] - base[i]) * alpha // 255 for i in range(3))


class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.px = bytearray(w * h * 3)
    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(c)

    def fill(self, c):
        self.px[:] = bytes(c) * (self.w * self.h)

    def rect(self, x0, y0, w, h, c):
        x1, y1 = min(x0 + w, self.w), min(y0 + h, self.h)
        row = bytes(c) * (y1 - x0 if x1 > x0 else 0)
        for y in range(max(y0, 0), y1):
            if x1 > x0:
                i = (y * self.w + x0) * 3
                self.px[i:i + len(row)] = row

    def rect_a(self, x0, y0, w, h, c, alpha):
        x1, y1 = min(x0 + w, self.w), min(y0 + h, self.h)
        for y in range(max(y0, 0), y1):
            for x in range(max(x0, 0), x1):
                self.set(x, y, blend(bytes(self.px[(y * self.w + x) * 3:(y * self.w + x) * 3 + 3]), c, alpha))

    def hline(self, x0, x1, y, c):
        self.rect(x0, y, x1 - x0, 1, c)

    def text(self, x, y, s, c, scale=1, spacing=1):
        cx = x
        for ch in s.upper():
            rows = FONT.get(ch, FONT["?"])
            for ry, bits in enumerate(rows):
                for rx in range(5):
                    if bits & (1 << (4 - rx)):
                        if scale == 1:
                            self.set(cx + rx, y + ry, c)
                        else:
                            self.rect(cx + rx * scale, y + ry * scale, scale, scale, c)
            cx += (5 + spacing) * scale
        return cx - x

    def text_w(self, s, scale=1, spacing=1):
        return len(s) * (5 + spacing) * scale - spacing * scale

    # --- simple pictograms ---
    def pico_drone(self, cx, cy, c):
        for t in (-1, 1):
            self.hline(cx - 13, cx - 6, cy + 6 * t, c)
            self.rect(cx - 16, cy + 6 * t - 2, 4, 4, c)
            self.hline(cx + 6, cx + 13, cy + 6 * t, c)
            self.rect(cx + 12, cy + 6 * t - 2, 4, 4, c)
        self.rect(cx - 5, cy - 5, 10, 10, c)
        self.rect(cx - 2, cy - 2, 4, 4, blend((26, 34, 56), c, 60))

    def pico_globe(self, cx, cy, c):
        r = 11
        for y in range(-r, r + 1):
            for x in range(-r, r + 1):
                if x * x + y * y <= r * r and (abs(x) % 9 != 4 or y * y > r * r // 3):
                    self.set(cx + x, cy + y, c)
        self.hline(cx - r + 1, cx + r, cy - 5, (26, 34, 56))
        self.hline(cx - r + 1, cx + r, cy + 5, (26, 34, 56))
        self.rect(cx - 1, cy - r + 1, 2, 2 * r - 1, (26, 34, 56))

    def pico_radar(self, cx, cy, c):
        import math
        self.rect(cx - 2, cy - 8, 4, 14, c)
        self.rect(cx - 8, cy + 4, 16, 3, c)
        r = 16
        for a in range(0, 200, 6):
            ang = a * 0.01745
            self.set(cx + int(r * math.cos(ang)), cy - int(r * math.sin(ang)), c)

    def pico_ballot(self, cx, cy, c):
        self.rect(cx - 12, cy - 6, 24, 18, c)
        self.rect(cx - 10, cy - 4, 20, 14, (26, 34, 56))
        self.rect(cx - 7, cy - 1, 5, 8, c)
        self.rect(cx + 1, cy - 1, 5, 8, c)
        self.rect(cx - 9, cy - 14, 18, 6, c)

    def pico_track(self, cx, cy, c):
        import math
        r = 11
        for a in range(0, 360, 3):
            ang = a * 0.01745
            for rr in (r - 2, r):
                self.set(cx + int(rr * math.cos(ang)), cy + int(rr * math.sin(ang) * 0.75), c)
        self.rect(cx - 9, cy - 4, 8, 8, c)
        self.rect(cx + 1, cy - 2, 6, 6, c)

    def pico_ball(self, cx, cy, c):
        r = 11
        for y in range(-r, r + 1):
            for x in range(-r, r + 1):
                if x * x + y * y <= r * r:
                    self.set(cx + x, cy + y, c)
        self.hline(cx - r, cx + r, cy, (26, 34, 56))
        for x in range(-r, r + 1):
            self.set(cx + x, cy - x * 3 // 5, (26, 34, 56))
            self.set(cx + x, cy + x * 3 // 5, (26, 34, 56))

    def pico_ship(self, cx, cy, c):
        self.rect(cx - 14, cy, 28, 7, c)
        self.rect(cx - 8, cy - 10, 12, 10, c)
        self.rect(cx + 5, cy - 6, 6, 6, c)
        self.rect(cx - 4, cy - 7, 2, 7, (26, 34, 56))
        for x in (-20, -17, 17, 20):
            self.hline(cx + x, cx + x + 2, cy + 10, c)
            self.hline(cx + x + 1, cx + x + 3, cy + 11, c)

    def pico_flag(self, cx, cy, c):
        self.rect(cx - 12, cy - 12, 3, 26, c)
        for i in range(9):
            w = 20 - abs(i - 4) * 4
            self.hline(cx - 9, cx - 9 + w, cy - 12 + i, c)

    def pico_score(self, cx, cy, c):
        for dx, dy in ((0, 0), (22, 0), (11, 16)):
            self.rect(cx + dx - 8, cy + dy - 8, 16, 16, c)
            self.rect(cx + dx - 4, cy + dy - 4, 8, 8, (26, 34, 56))


def render():
    c = Canvas(W, H)
    bg = (15, 20, 38)
    card_bg = (26, 34, 56)
    fg = (222, 228, 240)
    muted = (110, 122, 144)
    c.fill(bg)

    # Header
    c.rect(0, 0, W, 4, (231, 111, 81))
    c.text(60, 70, "THE WORLD IN ONE FRAME", fg, 4)
    c.rect(60, 130, 520, 2, (231, 111, 81))
    c.text(60, 156, "SUNDAY 22 NOVEMBER 2026", muted, 2)
    c.text(1150, 156, "EIGHT STORIES", (128, 138, 156), 2)

    # Cards
    top = 240
    ch, gap, side = 196, 24, 60
    for i, (tag, headline, accent) in enumerate(STORIES):
        y = top + i * (ch + gap)
        c.rect(side, y, W - 2 * side, ch, card_bg)
        c.rect(side, y, 6, ch, accent)
        c.text(side + 34, y + 28, tag, accent, 2)
        # pictogram centered at right
        cx, cy = W - side - 100, y + 64
        pico = [Canvas.pico_drone, Canvas.pico_globe, Canvas.pico_radar, Canvas.pico_ballot,
                Canvas.pico_flag, Canvas.pico_track, Canvas.pico_ball, Canvas.pico_ship,
                Canvas.pico_score][i % 9]
        pico(c, cx, cy, accent)
        c.rect_a(side + 34, y + 62, 18, 18, accent, 255)
        # headline: wrap at card width
        words = headline.split()
        lines, cur = [], ""
        maxw = W - 2 * side - 34 - 170
        for w_ in words:
            t = (cur + " " + w_).strip()
            if c.text_w(t, 2) <= maxw:
                cur = t
            else:
                lines.append(cur)
                cur = w_
        if cur:
            lines.append(cur)
        ly = y + 66
        for ln in lines:
            c.text(side + 34, ly, ln, fg, 2)
            ly += 26
        c.hline(side + 34, W - side - 34, y + ch - 22, (46, 56, 82))

    # Footer
    fy = H - 120
    c.rect(0, fy - 34, W, 2, (46, 56, 82))
    c.text(60, fy, FOOTER, (128, 138, 156), 2)
    c.text(W - 60 - c.text_w("PAGE 01"), fy, "PAGE 01", (128, 138, 156), 2)
    c.rect(0, H - 4, W, 4, (231, 111, 81))
    return c


def write_png(canvas, path):
    w, h = canvas.w, canvas.h
    raw = b"".join(b"\x00" + bytes(canvas.px[y * w * 3:(y + 1) * w * 3]) for y in range(h))
    idat = zlib.compress(raw, 9)

    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
           + chunk(b"IDAT", idat)
           + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)


def main():
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out, exist_ok=True)
    write_png(render(), os.path.join(out, "news-image-20261122.png"))


if __name__ == "__main__":
    main()

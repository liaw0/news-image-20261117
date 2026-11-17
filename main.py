#!/usr/bin/env python3
"""news-image-20261117 — "The World, Tuesday 17 November 2026".

Draws a newspaper front page summing up the world news of Tuesday
17 November 2026, as one 1024x1024 PNG written to /output/entry.png.

Pure standard library: own PNG encoder (zlib + struct), own 5x7 bitmap
font, own shape drawing. No network, no randomness, no timestamps —
two runs write byte-identical output.

The day's news (researched 18 Nov 2026 from BBC, Reuters, AP,
Al Jazeera, Just Security):
  LEAD  Ukraine strikes the Kerch Bridge to Crimea; a road span
        collapses. Zelenskyy calls it an "unprecedented operation".
        Russia vows to rebuild and hits Kyiv's bridges in reply.
  2     Trump arrives in Manila for the ASEAN summit, opening a
        three-day Asia trip ending in talks with Xi and Putin.
  3     Two oil tankers hit mines and catch fire in the Strait of
        Hormuz; a third U.S. carrier arrives in the region.
  4     ULA's Vulcan rocket fails in flight, destroying 40 Amazon
        Leo internet satellites.
  BRIEFS Nvidia reports after the close (first results since Jensen
        Huang's exit); JPMorgan blames a software bug, not a hack,
        for Monday's banking outage; UK sanctions Israeli settlement
        firms; Japan scrambles jets as Russian planes enter its
        airspace.
"""
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- font
# 5x7 bitmap font, '#' = ink. Uppercase, digits, common punctuation.
FONT = {
    'A': (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    '0': (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    '3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    '.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ';': (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '-': (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    '(': ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ')': (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    '/': ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    '+': (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
}


def text_width(s, scale):
    return len(s) * 6 * scale - scale


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg) * (w * h)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = c

    def fill_rect(self, x0, y0, x1, y1, c):
        x0 = max(0, x0); y0 = max(0, y0)
        x1 = min(self.w, x1); y1 = min(self.h, y1)
        for y in range(y0, y1):
            i = (y * self.w + x0) * 3
            row = bytes(c) * (x1 - x0)
            self.px[i:i + len(row)] = row

    def rect(self, x0, y0, x1, y1, c, t=1):
        self.fill_rect(x0, y0, x1, y0 + t, c)
        self.fill_rect(x0, y1 - t, x1, y1, c)
        self.fill_rect(x0, y0, x0 + t, y1, c)
        self.fill_rect(x1 - t, y0, x1, y1, c)

    def line(self, x0, y0, x1, y1, c):
        dx = abs(x1 - x0); dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy; x0 += sx
            if e2 <= dx:
                err += dx; y0 += sy

    def circle(self, cx, cy, r, c):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.fill_rect(cx - dx, cy + dy, cx + dx + 1, cy + dy + 1, c)

    def ellipse(self, cx, cy, rx, ry, c):
        for dy in range(-ry, ry + 1):
            dx = int(rx * (1 - (dy * dy) / (ry * ry)) ** 0.5) if ry else 0
            self.fill_rect(cx - dx, cy + dy, cx + dx + 1, cy + dy + 1, c)

    def vgrad(self, x0, y0, x1, y1, c0, c1):
        span = max(1, y1 - y0)
        for y in range(y0, y1):
            t = (y - y0) / span
            c = bytes(int(c0[k] + (c1[k] - c0[k]) * t) for k in range(3))
            self.fill_rect(x0, y, x1, y + 1, c)

    def poly(self, pts, c):
        # scanline fill for a simple polygon
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    if y1 != y0:
                        xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.fill_rect(int(xs[i]), y, int(xs[i + 1]) + 1, y + 1, c)

    def text(self, x, y, s, scale, c):
        cx = x
        for ch in s.upper():
            g = FONT.get(ch, FONT[' '])
            for r, row in enumerate(g):
                for col, bit in enumerate(row):
                    if bit == '#':
                        self.fill_rect(cx + col * scale, y + r * scale,
                                       cx + (col + 1) * scale,
                                       y + (r + 1) * scale, c)
            cx += 6 * scale

    def text_center(self, cx, y, s, scale, c):
        self.text(cx - text_width(s, scale) // 2, y, s, scale, c)

    def wrap(self, s, scale, maxw):
        words = s.split(' ')
        lines, cur = [], ''
        for w in words:
            t = (cur + ' ' + w).strip()
            if text_width(t, scale) <= maxw or not cur:
                cur = t
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        return lines


# ---------------------------------------------------------------- PNG
def write_png(cv, path):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        out = struct.pack('>I', len(data)) + tag + data
        out += struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
        return out

    ihdr = struct.pack('>IIBBBBB', cv.w, cv.h, 8, 2, 0, 0, 0)
    data = b'\x89PNG\r\n\x1a\n'
    data += chunk(b'IHDR', ihdr)
    data += chunk(b'IDAT', comp)
    data += chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(data)
    return len(data)


# ---------------------------------------------------------------- palette
PAPER = bytes((250, 246, 236))
INK = bytes((17, 17, 17))
NAVY = bytes((22, 35, 63))
RED = bytes((200, 16, 46))
AMBER = bytes((232, 163, 61))
GREY = bytes((120, 124, 130))
LGREY = bytes((201, 205, 211))
WHITE = bytes((255, 255, 255))
DUSK_TOP = bytes((35, 43, 69))
DUSK_MID = bytes((150, 84, 66))
DUSK_LOW = bytes((232, 163, 61))
SEA = bytes((22, 50, 74))
SEA_LT = bytes((42, 107, 138))
FLAME = bytes((255, 122, 26))
FLAME_Y = bytes((255, 200, 60))
SMOKE = bytes((110, 110, 112))
SMOKE_LT = bytes((150, 150, 152))


# ---------------------------------------------------------------- scenes
def scene_bridge(cv, x0, y0, x1, y1):
    """Kerch Bridge at dusk: deck, two pylons, collapsed middle span."""
    cv.vgrad(x0, y0, x1, y1, DUSK_TOP, DUSK_LOW)
    # low sun
    cv.circle(x0 + 130, y0 + 58, 26, bytes((255, 214, 130)))
    cv.circle(x0 + 130, y0 + 58, 18, bytes((255, 232, 170)))
    # sea
    sea_y = y0 + (y1 - y0) * 2 // 3
    cv.fill_rect(x0, sea_y, x1, y1, SEA)
    for i, yy in enumerate(range(sea_y + 8, y1 - 6, 14)):
        cv.fill_rect(x0 + 20 + (i % 3) * 90, yy, x0 + 120 + (i % 3) * 90, yy + 3, SEA_LT)
    # far shore
    cv.fill_rect(x0, sea_y - 6, x1, sea_y, bytes((60, 48, 52)))
    # deck
    deck_y = sea_y - 46
    cv.fill_rect(x0, deck_y, x0 + 430, deck_y + 12, LGREY)
    cv.fill_rect(x0 + 560, deck_y, x1, deck_y + 12, LGREY)
    # pylons
    for px in (x0 + 300, x0 + 700):
        cv.fill_rect(px - 8, deck_y - 120, px + 8, deck_y, bytes((232, 232, 228)))
        cv.fill_rect(px - 14, deck_y - 128, px + 14, deck_y - 120, bytes((232, 232, 228)))
        # cables
        cv.line(px, deck_y - 118, px - 120, deck_y, bytes((210, 210, 206)))
        cv.line(px, deck_y - 118, px + 120, deck_y, bytes((210, 210, 206)))
    # collapsed span: a deck segment torn loose, sliding down at ~35 degrees
    cv.poly([(x0 + 430, deck_y + 2), (x0 + 512, deck_y + 59),
             (x0 + 505, deck_y + 69), (x0 + 423, deck_y + 12)], bytes((140, 144, 150)))
    cv.poly([(x0 + 496, deck_y + 78), (x0 + 522, deck_y + 84),
             (x0 + 516, deck_y + 96), (x0 + 492, deck_y + 90)], bytes((110, 114, 120)))
    # jagged break edges
    cv.poly([(x0 + 424, deck_y), (x0 + 438, deck_y + 4), (x0 + 430, deck_y + 12),
             (x0 + 420, deck_y + 8)], bytes((90, 94, 100)))
    # fire + smoke at the break
    cv.circle(x0 + 495, deck_y - 6, 22, FLAME)
    cv.circle(x0 + 495, deck_y - 6, 13, FLAME_Y)
    cv.circle(x0 + 480, deck_y - 34, 16, SMOKE)
    cv.circle(x0 + 505, deck_y - 58, 20, SMOKE_LT)
    cv.circle(x0 + 488, deck_y - 84, 24, SMOKE)
    cv.circle(x0 + 512, deck_y - 108, 18, SMOKE_LT)
    # railing posts on intact deck
    for xx in range(x0 + 12, x0 + 420, 28):
        cv.fill_rect(xx, deck_y - 10, xx + 3, deck_y, bytes((90, 94, 100)))
    for xx in range(x0 + 572, x1 - 10, 28):
        cv.fill_rect(xx, deck_y - 10, xx + 3, deck_y, bytes((90, 94, 100)))


def scene_manila(cv, x0, y0, x1, y1):
    """Airliner over a Manila skyline at morning."""
    cv.vgrad(x0, y0, x1, y1, bytes((126, 178, 214)), bytes((214, 232, 244)))
    cv.circle(x0 + 270, y0 + 26, 18, bytes((255, 236, 170)))
    # skyline
    base = y1 - 8
    heights = [52, 84, 64, 104, 74, 96, 58, 88, 70, 110, 62, 80]
    bw = (x1 - x0) // len(heights)
    for i, hh in enumerate(heights):
        bx = x0 + i * bw
        cv.fill_rect(bx + 3, base - hh, bx + bw - 3, base, bytes((70, 86, 108)))
        # lit windows
        for wy in range(base - hh + 10, base - 10, 16):
            cv.fill_rect(bx + 8, wy, bx + 12, wy + 6, AMBER)
    # airplane
    ax, ay = x0 + 60, y0 + 42
    cv.ellipse(ax, ay, 52, 9, WHITE)
    cv.poly([(ax + 30, ay - 4), (ax + 62, ay - 8), (ax + 58, ay + 2)], WHITE)
    cv.poly([(ax - 6, ay - 6), (ax + 8, ay - 26), (ax + 18, ay - 6)], WHITE)
    cv.poly([(ax - 2, ay + 4), (ax + 10, ay + 22), (ax + 20, ay + 4)], WHITE)
    cv.fill_rect(ax + 52, ay - 12, ax + 58, ay + 6, WHITE)
    for wx in range(ax - 34, ax + 30, 12):
        cv.fill_rect(wx, ay - 3, wx + 5, ay + 2, NAVY)
    # contrail
    cv.line(ax - 52, ay + 6, x0 + 4, ay + 26, WHITE)
    # sunlit sea strip
    cv.fill_rect(x0, base, x1, y1, bytes((38, 92, 122)))


def scene_hormuz(cv, x0, y0, x1, y1):
    """Oil tanker ablaze in the Strait of Hormuz, carrier behind."""
    cv.vgrad(x0, y0, x1, y1, bytes((214, 140, 66)), bytes((240, 196, 120)))
    cv.circle(x0 + 60, y0 + 30, 22, bytes((255, 226, 150)))
    sea_y = y0 + (y1 - y0) * 3 // 5
    cv.fill_rect(x0, sea_y, x1, y1, bytes((18, 64, 84)))
    for i, yy in enumerate(range(sea_y + 6, y1 - 4, 12)):
        cv.fill_rect(x0 + 10 + (i % 4) * 60, yy, x0 + 70 + (i % 4) * 60, yy + 2, bytes((40, 110, 140)))
    # aircraft carrier silhouette, on the water at right
    cv.fill_rect(x0 + 224, sea_y - 8, x0 + 312, sea_y + 4, bytes((52, 62, 74)))
    cv.fill_rect(x0 + 266, sea_y - 24, x0 + 284, sea_y - 8, bytes((52, 62, 74)))
    # tanker hull
    hull_y = sea_y + 6
    cv.fill_rect(x0 + 16, hull_y, x0 + 200, hull_y + 26, bytes((20, 20, 22)))
    cv.fill_rect(x0 + 16, hull_y + 26, x0 + 200, hull_y + 30, bytes((120, 30, 24)))
    # tanker deck structures
    cv.fill_rect(x0 + 36, hull_y - 22, x0 + 76, hull_y, bytes((200, 200, 196)))
    cv.fill_rect(x0 + 164, hull_y - 26, x0 + 182, hull_y, bytes((200, 200, 196)))
    cv.fill_rect(x0 + 168, hull_y - 38, x0 + 178, hull_y - 26, bytes((160, 40, 30)))
    # flames midship + smoke (kept inside the scene)
    cv.circle(x0 + 118, hull_y - 10, 20, FLAME)
    cv.circle(x0 + 118, hull_y - 10, 11, FLAME_Y)
    cv.circle(x0 + 96, hull_y - 22, 12, FLAME)
    cv.circle(x0 + 106, hull_y - 38, 13, SMOKE)
    cv.circle(x0 + 126, hull_y - 54, 15, SMOKE_LT)
    cv.circle(x0 + 110, hull_y - 68, 12, SMOKE)


def scene_vulcan(cv, x0, y0, x1, y1):
    """Vulcan rocket failing: fireball, debris, scattered satellites."""
    cv.vgrad(x0, y0, x1, y1, bytes((10, 14, 34)), bytes((30, 42, 80)))
    # stars
    for sx, sy in ((30, 18), (90, 40), (150, 14), (220, 30), (280, 60),
                   (40, 70), (120, 90), (250, 100), (300, 20), (180, 70)):
        cv.fill_rect(x0 + sx, y0 + sy, x0 + sx + 3, y0 + sy + 3, WHITE)
    # rocket body, diagonal
    cx, cy = x0 + 165, y0 + 70
    cv.poly([(cx - 8, cy - 34), (cx + 8, cy - 34), (cx + 6, cy + 26), (cx - 6, cy + 26)], WHITE)
    cv.poly([(cx - 8, cy - 34), (cx, cy - 52), (cx + 8, cy - 34)], RED)
    cv.poly([(cx - 6, cy + 26), (cx - 20, cy + 44), (cx - 6, cy + 36)], bytes((180, 180, 180)))
    cv.poly([(cx + 6, cy + 26), (cx + 20, cy + 44), (cx + 6, cy + 36)], bytes((180, 180, 180)))
    cv.fill_rect(cx - 8, cy - 6, cx + 8, cy + 2, NAVY)
    # fireball below
    cv.circle(cx, cy + 58, 26, FLAME)
    cv.circle(cx, cy + 58, 15, FLAME_Y)
    cv.circle(cx - 18, cy + 74, 12, FLAME)
    cv.circle(cx + 20, cy + 76, 10, FLAME)
    # debris + satellites scattering
    for dx, dy, s in ((60, 30, 1), (240, 44, 1), (90, 110, 1), (270, 96, 1),
                      (40, 60, 0), (300, 70, 0)):
        cv.fill_rect(x0 + dx, y0 + dy, x0 + dx + 8, y0 + dy + 8, LGREY)
        cv.fill_rect(x0 + dx - 10, y0 + dy + 2, x0 + dx, y0 + dy + 6, bytes((40, 90, 160)))
        cv.fill_rect(x0 + dx + 8, y0 + dy + 2, x0 + dx + 18, y0 + dy + 6, bytes((40, 90, 160)))
    # falling trail
    cv.line(cx - 4, cy + 84, cx - 30, y1 - 6, SMOKE_LT)
    cv.line(cx + 6, cy + 84, cx + 34, y1 - 6, SMOKE_LT)


# ---------------------------------------------------------------- layout
def build():
    cv = Canvas(W, H, PAPER)

    # ---- masthead
    cv.fill_rect(0, 0, W, 88, NAVY)
    cv.text(20, 12, "THE WORLD", 9, WHITE)
    cv.text(1024 - 20 - text_width("17 NOV 2026", 5), 26, "17 NOV 2026", 5, AMBER)
    cv.fill_rect(0, 88, W, 94, RED)

    # ---- lead headline + deck
    cv.text(20, 104, "KERCH BRIDGE HIT", 9, INK)
    cv.text(20, 172, "UKRAINE STRIKES CRIMEA LINK AS ROAD SPAN COLLAPSES", 3, RED)

    # ---- lead scene
    cv.rect(20, 206, 1004, 496, INK, 2)
    scene_bridge(cv, 22, 208, 1002, 494)

    # ---- secondary row
    panels = [
        (16, scene_manila,
         "TRUMP LANDS IN MANILA",
         "ASEAN summit opens Asia trip; Xi, Putin talks ahead"),
        (347, scene_hormuz,
         "TANKERS HIT IN HORMUZ",
         "Two tankers hit by mines; third U.S. carrier arrives"),
        (678, scene_vulcan,
         "ROCKET FAILS, 40 SATELLITES LOST",
         "ULA Vulcan anomaly destroys Amazon Leo payload"),
    ]
    for px, scene, head, deck in panels:
        cv.fill_rect(px, 510, px + 330, 790, bytes((242, 239, 230)))
        cv.rect(px, 510, px + 330, 790, INK, 2)
        cv.rect(px + 6, 516, px + 324, 646, INK, 1)
        scene(cv, px + 7, 517, px + 323, 645)
        lines = cv.wrap(head, 3, 330 - 20)
        y = 654
        for ln in lines[:2]:
            cv.text(px + 10, y, ln, 3, INK)
            y += 24
        dlines = cv.wrap(deck, 2, 330 - 20)
        y = 706
        for ln in dlines[:4]:
            cv.text(px + 10, y, ln, 2, bytes((60, 60, 60)))
            y += 18

    # ---- briefs
    cv.fill_rect(16, 800, 1008, 802, GREY)
    cv.text(20, 812, "ALSO TODAY", 2, RED)
    briefs = [
        "NVIDIA REPORTS AFTER CLOSE - FIRST RESULTS SINCE HUANG EXIT",
        "JPMORGAN BLAMES SOFTWARE BUG FOR MONDAY BANKING OUTAGE",
        "UK SANCTIONS ISRAELI SETTLEMENT FIRMS OVER WEST BANK",
        "JAPAN SCRAMBLES JETS AS RUSSIAN PLANES ENTER AIRSPACE",
    ]
    y = 838
    for b in briefs:
        cv.fill_rect(20, y + 4, 32, y + 16, RED)
        cv.text(40, y, b, 2, INK)
        y += 30

    # ---- footer
    cv.fill_rect(0, 956, W, H, NAVY)
    cv.text(20, 978, "TUESDAY 17 NOVEMBER 2026", 3, WHITE)
    cv.text(1024 - 20 - text_width("BBC / REUTERS / AP / AL JAZEERA", 2),
            988, "BBC / REUTERS / AP / AL JAZEERA", 2, AMBER)
    return cv


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    cv = build()
    n = write_png(cv, path)
    print("wrote", path, n, "bytes")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Draw the front page for Friday 27 November 2026.

Fresh build for make.fun news-image-20261127. Pure standard library:
a small stroke font, a software canvas, and a hand-rolled PNG encoder.
No network, no randomness, no timestamps in the output bytes, so every
run writes identical bytes.

Layout: a neat broadsheet, "THE WORLD TODAY". One lead story, then
29 more stories in three columns, a markets strip, a briefs strip and
a source footer. All text is set in capitals with the stroke font
below, so there is no tiny body copy to garble.
"""

import os
import struct
import sys
import zlib

# ---------------------------------------------------------------- font
# Each glyph is a list of strokes; a stroke is a list of (x, y) points
# on a 7 wide by 12 tall grid (cap height y=0..10, descenders to y=11).
# Strokes are written as "x,y x,y; x,y x,y" strings and parsed at load.
_RAW = {
    "A": "0,10 3,0 6,10;1,7 5,7",
    "B": "0,0 0,10 4,10 6,8 6,6 4,5 0,5;4,5 6,3 6,1 4,0 0,0",
    "C": "6,2 5,0 2,0 0,2 0,8 2,10 5,10 6,8",
    "D": "0,0 0,10 4,10 6,8 6,2 4,0 0,0",
    "E": "6,0 0,0 0,10 6,10;0,5 4,5",
    "F": "0,10 0,0 6,0;0,5 4,5",
    "G": "6,2 4,0 2,0 0,2 0,8 2,10 5,10 6,9 6,5 4,5",
    "H": "0,0 0,10;6,0 6,10;0,5 6,5",
    "I": "0,0 6,0;3,0 3,10;0,10 6,10",
    "J": "6,0 6,8 4,10 2,10 0,8",
    "K": "0,0 0,10;6,0 0,5 6,10",
    "L": "0,0 0,10 6,10",
    "M": "0,10 0,0 3,5 6,0 6,10",
    "N": "0,10 0,0 6,10 6,0",
    "O": "2,0 4,0 6,2 6,8 4,10 2,10 0,8 0,2 2,0",
    "P": "0,10 0,0 5,0 6,1 6,4 5,5 0,5",
    "Q": "2,0 4,0 6,2 6,8 4,10 2,10 0,8 0,2 2,0;4,7 6,10",
    "R": "0,10 0,0 5,0 6,1 6,4 5,5 0,5;4,5 6,10",
    "S": "6,2 5,0 2,0 0,2 0,4 2,5 4,5 6,6 6,8 4,10 2,10 0,8",
    "T": "0,0 6,0;3,0 3,10",
    "U": "0,0 0,8 2,10 4,10 6,8 6,0",
    "V": "0,0 3,10 6,0",
    "W": "0,0 2,10 3,5 4,10 6,0",
    "X": "0,0 6,10;6,0 0,10",
    "Y": "0,0 3,5 6,0;3,5 3,10",
    "Z": "0,0 6,0 0,10 6,10",
    "0": "2,0 4,0 6,2 6,8 4,10 2,10 0,8 0,2 2,0",
    "1": "2,1 3,0 3,10;1,10 5,10",
    "2": "0,2 1,0 4,0 6,2 6,4 0,10 6,10",
    "3": "0,1 2,0 4,0 6,2 6,4 4,5;4,5 6,6 6,8 4,10 2,10 0,9",
    "4": "5,0 5,10;0,6 6,6;0,6 5,0",
    "5": "6,0 0,0 0,5 4,5 6,6 6,8 4,10 1,10 0,9",
    "6": "6,1 4,0 2,0 0,2 0,8 2,10 4,10 6,8 6,6 4,5 2,5 0,7",
    "7": "0,0 6,0 3,10",
    "8": "2,0 4,0 6,2 6,4 4,5 2,5 0,4 0,2 2,0;2,5 4,5 6,6 6,8 4,10 2,10 0,8 0,6 2,5",
    "9": "0,8 0,3 1,1 3,0 5,0 6,2 6,8 4,10 2,10 0,9;0,5 6,5",
    ".": "3,9 3,10",
    ",": "3,8 3,10;3,10 1,11",
    ":": "3,2 3,3;3,8 3,9",
    ";": "3,2 3,3;3,8 3,10;3,10 1,11",
    "!": "3,0 3,7;3,9 3,10",
    "?": "1,2 2,0 4,0 5,1 5,3 3,5 3,7;3,9 3,10",
    "'": "3,0 2,3",
    '"': "2,0 1,3;5,0 4,3",
    "-": "0,5 6,5",
    "(": "5,0 3,2 3,8 5,10",
    ")": "1,0 3,2 3,8 1,10",
    "$": "3,0 3,10;6,2 5,0 2,0 0,2 0,4 2,5 4,5 6,6 6,8 4,10 2,10 0,8",
    "%": "6,0 0,10;0,2 2,2 2,0 0,0;4,10 6,10 6,8 4,8",
    "+": "3,2 3,8;0,5 6,5",
    "/": "6,10 0,0",
    "=": "0,3 6,3;0,7 6,7",
    "*": "3,0 3,10;0,3 6,7;6,3 0,7",
    "<": "6,0 0,5 6,10",
    ">": "0,0 6,5 0,10",
}


def _parse(raw):
    out = {}
    for ch, spec in raw.items():
        strokes = []
        for part in spec.split(";"):
            pts = []
            for tok in part.split():
                x, y = tok.split(",")
                pts.append((int(x), int(y)))
            strokes.append(pts)
        out[ch] = strokes
    return out


FONT = _parse(_RAW)
ADVANCE = 8.0  # grid units per character, including spacing


# ---------------------------------------------------------------- canvas
W, H = 1024, 1024
PAPER = (247, 243, 234)
INK = (18, 18, 20)
RED = (158, 28, 32)
NAVY = (28, 58, 96)
GREY = (110, 108, 100)
LIGHT = (238, 232, 220)
GREEN = (32, 96, 58)


class Canvas:
    def __init__(self, w=W, h=H, bg=PAPER):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(c)

    def dot(self, x, y, c, t):
        r = t // 2
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                self.set(x + dx, y + dy, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.dot(x0, y0, c, t)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, c)

    def hline(self, x, y, w, c, t=1):
        for yy in range(y, y + t):
            for xx in range(x, x + w):
                self.set(xx, yy, c)

    def vline(self, x, y, h, c, t=1):
        for xx in range(x, x + t):
            for yy in range(y, y + h):
                self.set(xx, yy, c)

    def box(self, x, y, w, h, c, t=1):
        self.hline(x, y, w, c, t)
        self.hline(x, y + h - t, w, c, t)
        self.vline(x, y, h, c, t)
        self.vline(x + w - t, y, h, c, t)


# ---------------------------------------------------------------- text
def text_width(text, unit):
    return len(text) * ADVANCE * unit - unit


def draw_glyph(cv, x, y, ch, unit, color):
    strokes = FONT.get(ch)
    if strokes is None:
        return
    t = max(1, int(round(unit * 0.45)))
    for pts in strokes:
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            cv.line(round(x + ax * unit), round(y + ay * unit),
                    round(x + bx * unit), round(y + by * unit),
                    color, t)


def draw_text(cv, x, y, text, unit, color, align="left"):
    """Draw one line; (x, y) is the top-left, or the centre/right anchor."""
    w = text_width(text, unit)
    if align == "center":
        x = x - w / 2
    elif align == "right":
        x = x - w
    cx = x
    for ch in text:
        if ch == " ":
            cx += ADVANCE * unit
            continue
        draw_glyph(cv, cx, y, ch, unit, color)
        cx += ADVANCE * unit
    return w


def wrap(text, unit, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    words = text.split(" ")
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, unit) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_block(cv, x, y, text, unit, color, max_w, leading):
    """Draw wrapped text; returns the y just below the last line."""
    for line in wrap(text, unit, max_w):
        draw_text(cv, x, y, line, unit, color)
        y += leading
    return y


# ---------------------------------------------------------------- png
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(cv, path):
    raw = bytearray()
    stride = cv.w * 3
    for yy in range(cv.h):
        raw.append(0)  # filter: none
        raw += cv.px[yy * stride:(yy + 1) * stride]
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0))
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


# ---------------------------------------------------------------- stories
# 30 stories, all first reported on 27 November 2026 in some time zone
# or on the evening of 26 November, as carried by Reuters, AP, BBC,
# CNN and the Wall Street Journal. Headlines are kept short on purpose:
# two lines each in the columns, so nothing is set in tiny type.
# (kicker, headline)
COL_A = [
    ("WORLD", "RUSSIA HITS TWO GRAIN SHIPS OFF ODESA"),
    ("WORLD", "KUSHNER: PUTIN SHOWED RESTRAINT ON NUKES"),
    ("WORLD", "SABOTAGE IN EUROPE RISKS MASS CASUALTIES"),
    ("MIDDLE EAST", "TWO ITALIANS KILLED IN KUWAIT STRIKE"),
    ("MIDDLE EAST", "OIL CLIMBS AS HOUTHIS HIT SAUDI REFINERY"),
    ("TRADE", "US UNVEILS NEW TARIFFS ON CHINA AND EU"),
    ("MARKETS", "STOCKS RALLY AS TARIFFS LOOK MILDER"),
    ("ECONOMY", "US INFLATION 3.3%; FED SEEN RAISING RATES"),
    ("ECONOMY", "BANK OF KOREA LIFTS RATE TO 3.25%"),
    ("ECONOMY", "BRAZIL INFLATION EASES TO 4.64%"),
]
COL_B = [
    ("AMERICA", "IOWA BLAST A SUCCESS; NO LEAD IN THE AIR"),
    ("AMERICA", "MACY'S PARADE POSTPONED, A FIRST"),
    ("AMERICA", "STORMS LEAVE 900,000 WITHOUT POWER"),
    ("SPORT", "BEARS STUN LIONS 39-35 ON THANKSGIVING"),
    ("SPORT", "RAMS BEAT PACKERS IN FIRST EVE GAME"),
    ("SPORT", "STEELERS CUT AARON RODGERS"),
    ("TECH", "SPACEX CLEARED FOR 1M AI SATELLITES"),
    ("TECH", "NVIDIA FACES SENATE OVER HUANG RETURN"),
    ("MIDDLE EAST", "NETANYAHU JUDGES URGE DROPPING CHARGES"),
    ("SPACE", "CHINA LAUNCHES SHENZHOU 24 CREW"),
]
COL_C = [
    ("AMERICA", "ABREGO GARCIA REACHES SPAIN"),
    ("BRITAIN", "TRAIN ATTACKER GUILTY ON 14 COUNTS"),
    ("BRITAIN", "UK MIGRATION LOWEST SINCE 1997"),
    ("CULTURE", "DEPARDIEU TO STAND TRIAL OVER 2018 RAPE CLAIM"),
    ("EUROPE", "TANKER CAPSIZES OFF IBIZA; ONE DEAD"),
    ("AFRICA", "CAIRO TANKER FIRE KILLS 31"),
    ("ASIA", "BANGKOK REFINERY BLAST INJURES NINE"),
    ("ASIA", "MYANMAR REJECTS ICJ GENOCIDE RULING"),
    ("MIDDLE EAST", "GAZA STRIKES KILL HAMAS OFFICIAL, WIFE"),
]

KICKER_COLOR = {
    "WORLD": NAVY, "MIDDLE EAST": RED, "TRADE": NAVY, "MARKETS": GREEN,
    "ECONOMY": GREEN, "AMERICA": NAVY, "SPORT": RED, "TECH": NAVY,
    "SPACE": NAVY, "BRITAIN": NAVY, "CULTURE": RED, "EUROPE": NAVY,
    "AFRICA": NAVY, "ASIA": NAVY,
}

LEAD_KICKER = "UKRAINE WAR - KYIV"
LEAD_HEAD = ["ZELENSKY: TRUMP-PUTIN", "FRIENDSHIP 'STRANGE'"]
LEAD_DECK = ("PUTIN IS 'AN AGGRESSOR, AND A KILLER', KYIV LEADER TELLS BBC. "
             "US 'TOO FOCUSED ON MIDDLE EAST' AS PATRIOT SHORTAGE COSTS LIVES.")
ALSO = [
    "TRUMP: I ASKED PUTIN TO 'PULL BACK'",
    "OIL: BRENT $95.36 AS OPEC+ MEETS SUNDAY",
    "EU SEEKS DECEMBER DEAL ON UKRAINE AID",
]
MARKETS = ("MARKETS: BRENT $95.36 - WTI $84.73 - NASDAQ FELL 2% ON "
           "WEDNESDAY - KOSPI FELL 6%")
BRIEFS = ("ALSO IN THE NEWS: CIA SYSTEM BREACHED IN CYBERATTACK - GERMAN "
          "BOAT DEALER HELD OVER SMUGGLER BOATS - UK-EU TREATY HAS "
          "10-YEAR EXIT CLAUSE - JOLIE AND PITT SETTLE WINERY CASE - "
          "RAMSAY TO HOST TOP GEAR - NORTH KOREA EXPELS SWISS DIPLOMAT")
FOOTER = ("SOURCES: REUTERS - AP - BBC - CNN - WSJ - "
          "THE WORLD TODAY - FRIDAY 27 NOVEMBER 2026")


def draw_column(cv, x, y_top, y_bottom, stories):
    y = y_top
    for kicker, head in stories:
        draw_text(cv, x, y, kicker, 1.05, KICKER_COLOR[kicker])
        y += 11
        y = draw_block(cv, x, y, head, 1.45, INK, 306, 17)
        y += 4
        cv.hline(x, y, 306, LIGHT, 1)
        y += 5
    if y > y_bottom + 2:
        print("WARNING: column at x=%d overflows by %d px" % (x, y - y_bottom),
              file=sys.stderr)
    return y


# ---------------------------------------------------------------- build
def build(path):
    cv = Canvas()
    # Masthead.
    cv.hline(28, 12, 968, INK, 3)
    cv.hline(28, 18, 968, INK, 1)
    draw_text(cv, 512, 28, "THE WORLD TODAY", 5.8, INK, align="center")
    cv.hline(28, 98, 968, INK, 1)
    draw_text(cv, 28, 104, "FRIDAY 27 NOVEMBER 2026", 1.7, INK)
    draw_text(cv, 996, 104, "WORLD EDITION", 1.7, INK, align="right")
    cv.hline(28, 124, 968, INK, 3)

    # Lead story.
    draw_text(cv, 28, 136, LEAD_KICKER, 1.5, RED)
    y = 154
    for line in LEAD_HEAD:
        draw_text(cv, 28, y, line, 3.8, INK)
        y += 44
    y += 4
    y = draw_block(cv, 28, y, LEAD_DECK, 1.75, INK, 620, 22)
    lead_bottom = y + 8
    cv.hline(28, lead_bottom, 968, INK, 1)

    # "Also today" box on the right of the lead.
    cv.box(668, 136, 328, lead_bottom - 136, INK, 1)
    cv.rect(668, 136, 328, 24, INK)
    draw_text(cv, 680, 141, "ALSO TODAY", 1.5, PAPER)
    by = 168
    for item in ALSO:
        by = draw_block(cv, 680, by, item, 1.4, INK, 304, 17)
        by += 5

    # Three columns of stories: 10 + 10 + 9 = 29, plus the lead = 30.
    col_top, col_bottom = lead_bottom + 8, 882
    draw_column(cv, 28, col_top, col_bottom, COL_A)
    draw_column(cv, 359, col_top, col_bottom, COL_B)
    draw_column(cv, 690, col_top, col_bottom, COL_C)
    cv.vline(346, col_top, col_bottom - col_top, GREY, 1)
    cv.vline(677, col_top, col_bottom - col_top, GREY, 1)

    # Markets strip, briefs, footer.
    cv.hline(28, 890, 968, INK, 3)
    draw_text(cv, 28, 898, MARKETS, 1.5, INK)
    cv.hline(28, 924, 968, INK, 1)
    draw_block(cv, 28, 932, BRIEFS, 1.45, INK, 968, 18)
    cv.hline(28, 990, 968, INK, 1)
    draw_text(cv, 512, 996, FOOTER, 1.2, GREY, align="center")

    n = write_png(cv, path)
    total = 1 + len(COL_A) + len(COL_B) + len(COL_C)
    print("wrote %s (%d bytes, %d stories)" % (path, n, total))
    return n


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    build(out)

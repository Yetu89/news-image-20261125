"""Render THE DAILY GLOBE front page for Wednesday 25 November 2026.

Reads tools/stories.json and draws a 1024x1024 newspaper front page
into entry.png at the repository root. Pillow plus the standard library.
The output is deterministic: identical input always yields identical bytes.
"""

import json
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA_PATH = os.path.join(HERE, "stories.json")
OUT_PATH = os.path.join(ROOT, "entry.png")

W, H = 1024, 1024
MX = 42                      # side margin
CW = W - 2 * MX              # content width

PAPER = (247, 243, 232)
INK = (22, 22, 22)
GREY = (72, 72, 72)
RULE = (150, 145, 130)
RED = (139, 26, 26)
PANEL = (238, 233, 219)
EDGE = (180, 172, 150)

FONTS = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    try:
        return ImageFont.truetype(os.path.join(FONTS, name), size)
    except OSError:
        return ImageFont.load_default()


def serif_b(s):
    return font("DejaVuSerif-Bold.ttf", s)


def serif(s):
    return font("DejaVuSerif.ttf", s)


def sans(s):
    return font("DejaVuSans.ttf", s)


def sans_b(s):
    return font("DejaVuSans-Bold.ttf", s)


def fit_font(draw, name, text, size, max_w):
    """Largest size at or below `size` whose rendering fits max_w."""
    while size > 8:
        f = font(name, size)
        if draw.textlength(text, font=f) <= max_w:
            return f
        size -= 1
    return font(name, 8)


def wrap(draw, text, f, max_w):
    lines, cur = [], ""
    for word in text.split():
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(draw, x, y, text, f, fill, max_w, leading, limit=None):
    lines = wrap(draw, text, f, max_w)
    if limit is not None and len(lines) > limit:
        lines = lines[:limit]
        lines[-1] = lines[-1].rstrip() + " ..."
    for line in lines:
        draw.text((x, y), line, font=f, fill=fill)
        y += leading
    return y


def hline(draw, y, weight=2, color=RULE):
    draw.line([(MX, y), (W - MX, y)], fill=color, width=weight)
    return y + weight


def draw_chart(draw, x, y, w, h):
    """Falling bar chart with a bold red arrow pointing down: Brent slides."""
    base = y + h - 8
    bars = [1.0, 0.94, 0.88, 0.78, 0.72, 0.60, 0.55, 0.44, 0.38, 0.26, 0.16]
    bw = w // len(bars)
    for i, frac in enumerate(bars):
        bh = int((h - 40) * frac)
        bx = x + i * bw + 3
        draw.rectangle([bx, base - bh, bx + bw - 6, base], fill=RED)
    draw.line([(x, base), (x + w, base)], fill=INK, width=3)
    # Arrow from the first bar top down to above the last bar.
    ax0, ay0 = x + 6, base - int((h - 40) * 1.0) - 6
    ax1, ay1 = x + w - 16, base - int((h - 40) * 0.16) - 12
    draw.line([(ax0, ay0), (ax1, ay1)], fill=RED, width=5)
    draw.polygon(
        [(ax1 - 4, ay1 - 16), (ax1 + 18, ay1 + 10), (ax1 - 18, ay1 + 8)],
        fill=RED,
    )
    return base


def draw_lead(draw, lead, x, y, width):
    art_w = 300
    text_w = width - art_w - 26
    draw.text((x, y), lead["kicker"], font=sans_b(20), fill=RED)
    y += 30
    y = para(draw, x, y, lead["headline"], serif_b(31), INK, text_w, 37)
    y += 8
    y = para(draw, x, y, lead["body"], sans(17), GREY, text_w, 23, limit=2)
    top = y - 120
    art_x = x + text_w + 26
    bottom = draw_chart(draw, art_x, top, art_w, 120)
    cap = sans(15)
    label = lead["chart_label"]
    tw = draw.textlength(label, font=cap)
    draw.text((art_x + (art_w - tw) / 2, bottom + 6), label, font=cap, fill=GREY)
    return max(y, bottom + 24)


def draw_story(draw, story, x, y, width):
    draw.text((x, y), story["kicker"], font=sans_b(16), fill=RED)
    y += 20
    y = para(draw, x, y, story["headline"], serif_b(20), INK, width, 23)
    y += 4
    y = para(draw, x, y, story["body"], sans(15), GREY, width, 19, limit=2)
    return y


def draw_briefs(draw, items, x, y, width):
    draw.text((x, y), "IN BRIEF", font=sans_b(18), fill=INK)
    y += 24
    for item in items:
        draw.text((x, y), "\u2022", font=sans(18), fill=RED)
        y = para(draw, x + 20, y, item, sans(17), GREY, width - 20, 19)
        y += 1
    return y


def draw_markets(draw, markets, x, y, width):
    box_h = 72
    draw.rectangle(
        [x, y, x + width, y + box_h], fill=PANEL, outline=EDGE, width=2
    )
    draw.text((x + 14, y + 7), "MARKETS  —  WEDNESDAY CLOSE", font=sans_b(16), fill=INK)
    cell_w = width // len(markets)
    for i, m in enumerate(markets):
        cx = x + i * cell_w + cell_w // 2
        lab = sans(15)
        lw = draw.textlength(m["label"], font=lab)
        draw.text((cx - lw / 2, y + 27), m["label"], font=lab, fill=GREY)
        fig = fit_font(draw, "DejaVuSans-Bold.ttf", m["text"], 22, cell_w - 12)
        fw = draw.textlength(m["text"], font=fig)
        draw.text((cx - fw / 2, y + 45), m["text"], font=fig, fill=INK)
    return y + box_h


def build():
    with open(DATA_PATH, encoding="utf-8") as handle:
        data = json.load(handle)

    page = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(page)

    y = 20
    title = serif_b(54)
    tw = draw.textlength(data["paper"], font=title)
    draw.text(((W - tw) / 2, y), data["paper"], font=title, fill=INK)
    y += 62
    y = hline(draw, y, 2)
    y += 8
    date_f = sans_b(23)
    draw.text((MX, y), data["date"].upper(), font=date_f, fill=RED)
    tag = sans(19)
    tag_w = draw.textlength(data["tagline"], font=tag)
    draw.text((W - MX - tag_w, y + 2), data["tagline"], font=tag, fill=GREY)
    y += 30
    y = hline(draw, y, 3, INK)
    y += 14

    y = draw_lead(draw, data["lead"], MX, y, CW)
    y += 8
    y = hline(draw, y, 2)
    y += 10

    col_w = (CW - 24) // 2
    left_y = right_y = y
    for i, story in enumerate(data["stories"]):
        if i % 2 == 0:
            left_y = draw_story(draw, story, MX, left_y, col_w)
            left_y += 8
        else:
            right_y = draw_story(draw, story, MX + col_w + 24, right_y, col_w)
            right_y += 8
    y = max(left_y, right_y)
    y = hline(draw, y, 2)
    y += 8

    y = draw_briefs(draw, data["briefs"], MX, y, CW)
    y += 6
    y = draw_markets(draw, data["markets"], MX, y, CW)
    y += 8

    foot = sans(13)
    fw = draw.textlength(data["footer"], font=foot)
    draw.text(((W - fw) / 2, H - 28), data["footer"], font=foot, fill=GREY)

    print("layout: content ends at y =", y)
    assert y < H - 40, f"layout overflow: content ends at y={y}"
    page.save(OUT_PATH, "PNG")
    print("wrote", OUT_PATH)


if __name__ == "__main__":
    build()

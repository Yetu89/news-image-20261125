"""Paint THE DAILY GLOBE front page for Wednesday 25 November 2026.

The day's stories live in tools/stories.json. This script turns them
into a 1024 by 1024 newspaper front page and saves it as entry.png in
the repository root. Only Pillow and the standard library are used.
There is no network, no clock and no randomness anywhere, so running
the script twice over the same stories file paints identical bytes.
"""

import json
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
STORIES_PATH = os.path.join(HERE, "stories.json")
IMAGE_PATH = os.path.join(ROOT, "entry.png")

PAGE = 1024
MARGIN = 42
CONTENT = PAGE - 2 * MARGIN

PAPER = (248, 244, 233)
INK = (24, 24, 24)
MUTED = (74, 74, 74)
FAINT = (152, 147, 132)
ACCENT = (140, 28, 28)
LEAF = (26, 112, 62)
PANEL = (239, 234, 220)
EDGE = (182, 174, 152)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
STYLES = {
    "serif_b": "DejaVuSerif-Bold.ttf",
    "serif": "DejaVuSerif.ttf",
    "sans": "DejaVuSans.ttf",
    "sans_b": "DejaVuSans-Bold.ttf",
}


def face(style, size):
    """A TrueType face at the asked size, or the bitmap default."""
    try:
        return ImageFont.truetype(os.path.join(FONT_DIR, STYLES[style]), size)
    except OSError:
        return ImageFont.load_default()


def shrink_to_fit(draw, style, text, size, width):
    """Biggest size at or under `size` whose text fits `width`."""
    while size > 8:
        candidate = face(style, size)
        if draw.textlength(text, font=candidate) <= width:
            return candidate
        size -= 1
    return face(style, 8)


def wrap_text(draw, text, fnt, width):
    """Split `text` into lines no wider than `width`."""
    rows = []
    current = ""
    for word in text.split():
        trial = word if not current else current + " " + word
        if draw.textlength(trial, font=fnt) <= width:
            current = trial
        else:
            if current:
                rows.append(current)
            current = word
    if current:
        rows.append(current)
    return rows


def block(draw, x, y, text, fnt, colour, width, leading, limit=None):
    """Draw a wrapped paragraph; return the y below its last line."""
    rows = wrap_text(draw, text, fnt, width)
    if limit is not None and len(rows) > limit:
        rows = rows[:limit]
        rows[-1] = rows[-1].rstrip() + " ..."
    for row in rows:
        draw.text((x, y), row, font=fnt, fill=colour)
        y += leading
    return y


def rule(draw, y, weight=2, colour=FAINT):
    """A horizontal rule across the content column."""
    draw.line([(MARGIN, y), (PAGE - MARGIN, y)], fill=colour, width=weight)
    return y + weight


def falling_chart(draw, x, y, w, h):
    """Falling red bars with a downward trend arrow: Brent slides."""
    base = y + h - 8
    levels = [1.0, 0.9, 0.94, 0.76, 0.8, 0.62, 0.66, 0.48, 0.52, 0.34, 0.24]
    step = w // len(levels)
    for i, frac in enumerate(levels):
        top = base - int((h - 40) * frac)
        left = x + i * step + 3
        draw.rectangle([left, top, left + step - 6, base], fill=ACCENT)
    draw.line([(x, base), (x + w, base)], fill=INK, width=3)
    start = (x + 6, base - int((h - 40) * levels[0]) - 6)
    end = (x + w - 14, base - int((h - 40) * levels[-1]) + 8)
    draw.line([start, end], fill=ACCENT, width=5)
    draw.polygon(
        [(end[0] - 16, end[1] - 14), (end[0] + 4, end[1] + 2),
         (end[0] - 18, end[1] + 12)],
        fill=ACCENT,
    )
    return base


def lead_block(draw, lead, x, y, width):
    """Lead story: kicker, headline, body, falling-chart picture."""
    art_w = 320
    text_w = width - art_w - 26
    draw.text((x, y), lead["kicker"], font=face("sans_b", 20), fill=ACCENT)
    y += 30
    y = block(draw, x, y, lead["headline"], face("serif_b", 33), INK,
              text_w, 40)
    y += 8
    y = block(draw, x, y, lead["body"], face("sans", 18), MUTED, text_w,
              24, limit=2)
    art_top = y - 140
    art_x = x + text_w + 26
    bottom = falling_chart(draw, art_x, art_top, art_w, 140)
    caption = face("sans", 15)
    label = lead["chart_label"]
    label_w = draw.textlength(label, font=caption)
    draw.text((art_x + (art_w - label_w) / 2, bottom + 6), label,
              font=caption, fill=MUTED)
    return max(y, bottom + 24)


def story_block(draw, story, x, y, width):
    """One smaller story: kicker, headline, two lines of body."""
    draw.text((x, y), story["kicker"], font=face("sans_b", 16), fill=ACCENT)
    y += 20
    y = block(draw, x, y, story["headline"], face("serif_b", 21), INK,
              width, 25)
    y += 4
    y = block(draw, x, y, story["body"], face("sans", 15), MUTED, width,
              19, limit=2)
    return y


def briefs_block(draw, items, x, y, width):
    """The IN BRIEF list of one-line briefs."""
    draw.text((x, y), "IN BRIEF", font=face("sans_b", 18), fill=INK)
    y += 26
    for item in items:
        draw.text((x, y), "\u2022", font=face("sans", 18), fill=ACCENT)
        y = block(draw, x + 20, y, item, face("sans", 17), MUTED,
                  width - 20, 20)
        y += 2
    return y


def markets_block(draw, markets, x, y, width):
    """A boxed strip of the day's market closes."""
    box_h = 78
    draw.rectangle([x, y, x + width, y + box_h], fill=PANEL,
                   outline=EDGE, width=2)
    draw.text((x + 14, y + 8), "MARKETS  \u2014  WEDNESDAY CLOSE",
              font=face("sans_b", 16), fill=INK)
    cell_w = width // len(markets)
    for i, m in enumerate(markets):
        centre = x + i * cell_w + cell_w // 2
        lab = face("sans", 15)
        lab_w = draw.textlength(m["label"], font=lab)
        draw.text((centre - lab_w / 2, y + 30), m["label"], font=lab,
                  fill=MUTED)
        fig = shrink_to_fit(draw, "sans_b", m["text"], 22, cell_w - 12)
        fig_w = draw.textlength(m["text"], font=fig)
        draw.text((centre - fig_w / 2, y + 48), m["text"], font=fig,
                  fill=INK)
    return y + box_h


def paint():
    """Read the stories and paint the whole front page."""
    with open(STORIES_PATH, encoding="utf-8") as handle:
        data = json.load(handle)

    page = Image.new("RGB", (PAGE, PAGE), PAPER)
    draw = ImageDraw.Draw(page)
    draw.rectangle([6, 6, PAGE - 7, PAGE - 7], outline=EDGE, width=2)

    y = 20
    title = face("serif_b", 54)
    title_w = draw.textlength(data["paper"], font=title)
    draw.text(((PAGE - title_w) / 2, y), data["paper"], font=title,
              fill=INK)
    y += 62
    y = rule(draw, y, 2)
    y += 8
    date_f = face("sans_b", 23)
    draw.text((MARGIN, y), data["date"].upper(), font=date_f, fill=ACCENT)
    tag = face("sans", 19)
    tag_w = draw.textlength(data["tagline"], font=tag)
    draw.text((PAGE - MARGIN - tag_w, y + 2), data["tagline"], font=tag,
              fill=MUTED)
    y += 30
    y = rule(draw, y, 3, INK)
    y += 14

    y = lead_block(draw, data["lead"], MARGIN, y, CONTENT)
    y += 10
    y = rule(draw, y, 2)
    y += 12

    col_w = (CONTENT - 24) // 2
    left_y = right_y = y
    for i, story in enumerate(data["stories"]):
        if i % 2 == 0:
            left_y = story_block(draw, story, MARGIN, left_y, col_w)
            left_y += 10
        else:
            right_y = story_block(draw, story, MARGIN + col_w + 24,
                                  right_y, col_w)
            right_y += 10
    y = max(left_y, right_y)
    y = rule(draw, y, 2)
    y += 10

    y = briefs_block(draw, data["briefs"], MARGIN, y, CONTENT)
    y += 6
    y = markets_block(draw, data["markets"], MARGIN, y, CONTENT)
    y += 10

    foot = face("sans", 13)
    foot_w = draw.textlength(data["footer"], font=foot)
    draw.text(((PAGE - foot_w) / 2, PAGE - 28), data["footer"], font=foot,
              fill=MUTED)

    print("layout: content ends at y =", y)
    assert y < PAGE - 40, f"layout overflow: content ends at y={y}"
    page.save(IMAGE_PATH, "PNG")
    print("wrote", IMAGE_PATH)


if __name__ == "__main__":
    paint()

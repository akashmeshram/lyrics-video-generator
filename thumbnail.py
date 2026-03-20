#!/usr/bin/env python3
"""YouTube thumbnail generator for lyrics videos.

Uses the same background blending as make_video.py with title text overlay.
"""

from PIL import Image, ImageDraw, ImageFont
import os
import sys

# ============================================================
# CONFIGURATION — Match these with your make_video.py settings
# ============================================================

WIDTH, HEIGHT = 3840, 2160
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

IMG_BASE = os.path.join(BASE_DIR, "background1.jpg")
IMG_OVERLAY = os.path.join(BASE_DIR, "background2.jpg")  # or None
OVERLAY_OPACITY = 0.4
OVERLAY_CROP_BOTTOM = 0.0
DARK_OVERLAY = 0.20  # slightly lighter than video for thumbnail visibility

OUTPUT_FILE = os.path.join(BASE_DIR, "thumbnail.jpg")

SONG_TITLE = "Song Title Here"
SONG_SUBTITLE = "Artist or Description"
TAG_LINE = "Turkish & English Lyrics"  # small text below subtitle, or ""

# Fonts
FONT_REGULAR = "/System/Library/Fonts/Supplemental/Georgia.ttf"
FONT_ITALIC = "/System/Library/Fonts/Supplemental/Georgia Italic.ttf"
FONT_BOLD = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"

# Font sizes (for 4K, halve for 1080p)
TITLE_FONT_SIZE = 168
SUBTITLE_FONT_SIZE = 100
TAG_FONT_SIZE = 60

# Colors
TITLE_COLOR = (255, 255, 255, 255)
SUBTITLE_COLOR = (220, 200, 160, 255)
TAG_COLOR = (200, 200, 200, 230)

# ============================================================
# END CONFIGURATION
# ============================================================


def cover_fit(img, tw, th):
    ow, oh = img.size
    scale = max(tw / ow, th / oh)
    nw, nh = int(ow * scale), int(oh * scale)
    img = img.resize((nw, nh), Image.LANCZOS)
    left = (nw - tw) // 2
    top = (nh - th) // 2
    return img.crop((left, top, left + tw, top + th))


def generate_thumbnail():
    if not os.path.exists(IMG_BASE):
        sys.exit(f"Missing: {IMG_BASE}")

    base = Image.open(IMG_BASE).convert("RGBA")
    base = cover_fit(base, WIDTH, HEIGHT)

    if IMG_OVERLAY and os.path.exists(IMG_OVERLAY):
        overlay = Image.open(IMG_OVERLAY).convert("RGBA")
        if OVERLAY_CROP_BOTTOM > 0:
            ow, oh = overlay.size
            overlay = overlay.crop((0, 0, ow, int(oh * (1 - OVERLAY_CROP_BOTTOM))))
        overlay = cover_fit(overlay, WIDTH, HEIGHT)
        overlay_with_alpha = overlay.copy()
        r, g, b, a = overlay_with_alpha.split()
        a = a.point(lambda x: int(x * OVERLAY_OPACITY))
        overlay_with_alpha = Image.merge("RGBA", (r, g, b, a))
        base.paste(overlay_with_alpha, (0, 0), overlay_with_alpha)

    dark = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, int(255 * DARK_OVERLAY)))
    base.paste(dark, (0, 0), dark)

    # Bottom gradient for text readability
    gradient = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw_grad = ImageDraw.Draw(gradient)
    for y in range(HEIGHT // 3, HEIGHT):
        alpha = int(180 * (y - HEIGHT // 3) / (HEIGHT - HEIGHT // 3))
        draw_grad.line([(0, y), (WIDTH, y)], fill=(0, 0, 0, alpha))
    base = Image.alpha_composite(base, gradient)

    # Text
    text_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(text_layer)

    title_font = ImageFont.truetype(FONT_BOLD, TITLE_FONT_SIZE)
    bbox = draw.textbbox((0, 0), SONG_TITLE, font=title_font)
    tw = bbox[2] - bbox[0]
    x = (WIDTH - tw) // 2
    y = HEIGHT - 480

    draw.text((x + 5, y + 5), SONG_TITLE, font=title_font, fill=(0, 0, 0, 200))
    draw.text((x, y), SONG_TITLE, font=title_font, fill=TITLE_COLOR)

    sub_font = ImageFont.truetype(FONT_ITALIC, SUBTITLE_FONT_SIZE)
    bbox2 = draw.textbbox((0, 0), SONG_SUBTITLE, font=sub_font)
    sw = bbox2[2] - bbox2[0]
    sx = (WIDTH - sw) // 2
    sy = y + 190

    draw.text((sx + 3, sy + 3), SONG_SUBTITLE, font=sub_font, fill=(0, 0, 0, 180))
    draw.text((sx, sy), SONG_SUBTITLE, font=sub_font, fill=SUBTITLE_COLOR)

    if TAG_LINE:
        tag_font = ImageFont.truetype(FONT_ITALIC, TAG_FONT_SIZE)
        bbox3 = draw.textbbox((0, 0), TAG_LINE, font=tag_font)
        tagw = bbox3[2] - bbox3[0]
        tx = (WIDTH - tagw) // 2
        ty = sy + 130

        draw.text((tx + 2, ty + 2), TAG_LINE, font=tag_font, fill=(0, 0, 0, 150))
        draw.text((tx, ty), TAG_LINE, font=tag_font, fill=TAG_COLOR)

    result = Image.alpha_composite(base, text_layer).convert("RGB")
    result.save(OUTPUT_FILE, "JPEG", quality=95)
    print(f"Thumbnail saved: {OUTPUT_FILE} ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    generate_thumbnail()

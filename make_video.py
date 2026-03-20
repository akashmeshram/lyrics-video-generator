#!/usr/bin/env python3
"""Lyrics video generator — customizable template.

Usage:
    1. Configure the settings below (files, fonts, timing, resolution)
    2. Run: python3 make_video.py
    3. Output: output.mp4
"""

from PIL import Image, ImageDraw, ImageFont
import subprocess
import os
import sys
import json

# ============================================================
# CONFIGURATION — Edit this section for your project
# ============================================================

# Resolution: (3840, 2160) for 4K, (1920, 1080) for 1080p
WIDTH, HEIGHT = 3840, 2160
FPS = 30

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Input files (set IMG_OVERLAY to None for single background image)
AUDIO_FILE = os.path.join(BASE_DIR, "audio.mp3")
IMG_BASE = os.path.join(BASE_DIR, "background1.jpg")
IMG_OVERLAY = os.path.join(BASE_DIR, "background2.jpg")  # or None
OVERLAY_OPACITY = 0.4       # 0.0-1.0, how visible the overlay image is
OVERLAY_CROP_BOTTOM = 0.0   # 0.0-1.0, crop this fraction off the bottom
DARK_OVERLAY = 0.3          # 0.0-1.0, darken background for text readability
LYRICS_FILE = os.path.join(BASE_DIR, "lyrics.txt")
OUTPUT_FILE = os.path.join(BASE_DIR, "output.mp4")

# Song info (shown on title screen)
SONG_TITLE = "Song Title Here"
SONG_SUBTITLE = "Artist or Description"

# Fonts — find serif fonts on your system:
#   macOS:   /System/Library/Fonts/Supplemental/Georgia.ttf
#   Linux:   /usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf
#   Windows: C:/Windows/Fonts/georgia.ttf
FONT_REGULAR = "/System/Library/Fonts/Supplemental/Georgia.ttf"
FONT_ITALIC = "/System/Library/Fonts/Supplemental/Georgia Italic.ttf"

# Font sizes — scale with resolution
#   1080p: title=64,  line1=48,  line2=36,  spacing=12, shadow=2
#   4K:    title=160, line1=120, line2=90,  spacing=24, shadow=4
TITLE_SIZE = 160
LINE1_SIZE = 120
LINE2_SIZE = 90
LINE_SPACING = 24
SHADOW_OFFSET = 4

# Colors (R, G, B)
LINE1_COLOR = (255, 255, 255)       # white for original language
LINE2_COLOR = (220, 200, 160)       # warm yellow for translation
TITLE_COLOR = (255, 255, 255)       # white
SUBTITLE_COLOR = (220, 200, 160)    # warm yellow

# Text position (fraction of HEIGHT, 0.0=top, 1.0=bottom)
TITLE_POSITION = 0.50     # center for title screen
LYRICS_POSITION = 0.70    # lower area for lyrics

# Timing: (label, start_seconds, end_seconds)
# - "title": shown at the start
# - "couplet1", "couplet2", etc.: verse lines (matched to lyrics.txt order)
# - "end": fade to black
# Listen to your audio and set timestamps for each verse.
TIMING = [
    ("title",    0.0,   5.0),
    ("couplet1", 10.0,  25.0),
    ("couplet2", 27.0,  42.0),
    # Add more couplets as needed...
    ("end",      0.0,   0.0),  # Set to last few seconds of audio
]

# Fade durations (seconds)
FADE_DURATION = 0.5     # fade in/out for lyrics
TITLE_FADE_IN = 1.0     # slower fade in for title

# Repeat groups: pairs of couplets with identical text.
# Transitions are skipped between these so text stays on screen.
# Example: [("couplet2", "couplet3"), ("couplet5", "couplet6")]
REPEAT_GROUPS = []

# ============================================================
# END CONFIGURATION — No need to edit below this line
# ============================================================

_measure_draw = ImageDraw.Draw(Image.new("RGBA", (1, 1)))

_no_fade_out = set()
_no_fade_in = set()
for first, second in REPEAT_GROUPS:
    _no_fade_out.add(first)
    _no_fade_in.add(second)


def cover_fit(img, target_w, target_h):
    """Resize and center-crop image to cover target dimensions."""
    orig_w, orig_h = img.size
    scale = max(target_w / orig_w, target_h / orig_h)
    new_w = int(orig_w * scale)
    new_h = int(orig_h * scale)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    return img.crop((left, top, left + target_w, top + target_h))


def create_background():
    """Create background image, optionally blending two images."""
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

    if DARK_OVERLAY > 0:
        dark = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, int(255 * DARK_OVERLAY)))
        base.paste(dark, (0, 0), dark)

    return base.convert("RGB")


def parse_lyrics(filepath):
    """Parse lyrics file into list of (line1, line2) couplets.

    Expected format:
        Song Title

        First line original language
        First line translation

        Second line original language
        Second line translation
    """
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    couplets = []
    i = 1  # skip title line
    while i < len(lines) and not lines[i].strip():
        i += 1

    while i < len(lines):
        while i < len(lines) and not lines[i].strip():
            i += 1
        if i >= len(lines):
            break
        line1 = lines[i].strip()
        i += 1
        while i < len(lines) and not lines[i].strip():
            i += 1
        if i >= len(lines):
            couplets.append((line1, ""))
            break
        line2 = lines[i].strip()
        i += 1
        if line1 and line2:
            couplets.append((line1, line2))

    return couplets


def render_text_on_bg(bg, text_lines, alpha=255, vertical_center=0.70):
    """Render text lines centered on background."""
    img = bg.copy().convert("RGBA")

    rendered = []
    total_h = 0
    for text, font_path, size, color in text_lines:
        font = ImageFont.truetype(font_path, size)
        bbox = _measure_draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        rendered.append((text, font, tw, th, color))
        total_h += th

    total_h += LINE_SPACING * (len(rendered) - 1)

    center_y = int(HEIGHT * vertical_center)
    y = center_y - total_h // 2

    text_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(text_layer)

    for text, font, tw, th, color in rendered:
        x = (WIDTH - tw) // 2
        if len(color) == 3:
            r, g, b = color
            a_val = alpha
        else:
            r, g, b, a_val = color
            a_val = int(a_val * alpha / 255)

        draw.text(
            (x + SHADOW_OFFSET, y + SHADOW_OFFSET),
            text, font=font, fill=(0, 0, 0, int(a_val * 0.7))
        )
        draw.text((x, y), text, font=font, fill=(r, g, b, a_val))
        y += th + LINE_SPACING

    img = Image.alpha_composite(img, text_layer)
    return img.convert("RGB")


def render_title_frame(bg, alpha=255):
    """Render the title screen."""
    text_lines = [
        (SONG_TITLE, FONT_REGULAR, TITLE_SIZE, TITLE_COLOR),
        (SONG_SUBTITLE, FONT_ITALIC, LINE1_SIZE, SUBTITLE_COLOR),
    ]
    return render_text_on_bg(bg, text_lines, alpha=alpha, vertical_center=TITLE_POSITION)


def render_couplet_frame(bg, line1, line2, alpha=255):
    """Render a lyrics couplet."""
    text_lines = [
        (line1, FONT_REGULAR, LINE1_SIZE, LINE1_COLOR),
        (line2, FONT_ITALIC, LINE2_SIZE, LINE2_COLOR),
    ]
    return render_text_on_bg(bg, text_lines, alpha=alpha, vertical_center=LYRICS_POSITION)


def get_duration(audio_file):
    """Get audio duration in seconds using ffprobe."""
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json",
         "-show_format", audio_file],
        capture_output=True, text=True, check=True,
    )
    data = json.loads(result.stdout)
    return float(data["format"]["duration"])


def generate_video():
    """Main pipeline to generate the lyrics video."""
    for path in [IMG_BASE, AUDIO_FILE, LYRICS_FILE]:
        if not os.path.exists(path):
            sys.exit(f"Missing required file: {path}")
    for font_path in [FONT_REGULAR, FONT_ITALIC]:
        if not os.path.exists(font_path):
            sys.exit(f"Missing required font: {font_path}")

    print("Creating background...")
    bg = create_background()

    print("Parsing lyrics...")
    couplets = parse_lyrics(LYRICS_FILE)
    print(f"  Found {len(couplets)} couplets")
    for i, (l1, l2) in enumerate(couplets):
        print(f"  [{i+1}] L1: {l1[:60]}")
        print(f"       L2: {l2[:60]}")

    print("Getting audio duration...")
    duration = get_duration(AUDIO_FILE)
    total_frames = int(duration * FPS)
    print(f"  Duration: {duration:.2f}s, Total frames: {total_frames}")

    couplet_map = {}
    for seg_name, start, end in TIMING:
        if seg_name.startswith("couplet"):
            couplet_map[seg_name] = int(seg_name.replace("couplet", "")) - 1

    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{WIDTH}x{HEIGHT}",
        "-pix_fmt", "rgb24",
        "-r", str(FPS),
        "-i", "pipe:0",
        "-i", AUDIO_FILE,
        "-map", "0:v",
        "-map", "1:a",
        "-vcodec", "libx264",
        "-crf", "18",
        "-preset", "medium",
        "-pix_fmt", "yuv420p",
        "-acodec", "aac",
        "-b:a", "192k",
        "-shortest",
        OUTPUT_FILE,
    ]

    print("Starting FFmpeg...")
    proc = subprocess.Popen(
        ffmpeg_cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE
    )

    last_report_time = 0.0
    bg_bytes = bg.tobytes()

    try:
        for frame_idx in range(total_frames):
            t = frame_idx / FPS

            if t - last_report_time >= 10.0:
                pct = 100.0 * frame_idx / total_frames
                print(f"  Progress: {t:.1f}s / {duration:.1f}s ({pct:.1f}%)")
                last_report_time = t

            active_seg = None
            for seg_name, seg_start, seg_end in TIMING:
                if seg_start <= t < seg_end:
                    active_seg = (seg_name, seg_start, seg_end)
                    break

            if active_seg is None:
                proc.stdin.write(bg_bytes)
                continue

            seg_name, seg_start, seg_end = active_seg
            seg_duration = seg_end - seg_start
            t_in_seg = t - seg_start

            if seg_name == "title":
                if t_in_seg < TITLE_FADE_IN:
                    alpha = int(255 * t_in_seg / TITLE_FADE_IN)
                elif t_in_seg > seg_duration - FADE_DURATION:
                    alpha = int(255 * (seg_duration - t_in_seg) / FADE_DURATION)
                else:
                    alpha = 255
                frame = render_title_frame(bg, alpha=alpha)

            elif seg_name.startswith("couplet"):
                idx = couplet_map.get(seg_name, 0)
                if idx < len(couplets):
                    line1, line2 = couplets[idx]
                else:
                    line1, line2 = "", ""

                no_fi = seg_name in _no_fade_in
                no_fo = seg_name in _no_fade_out

                if not no_fi and t_in_seg < FADE_DURATION:
                    alpha = int(255 * t_in_seg / FADE_DURATION)
                elif not no_fo and t_in_seg > seg_duration - FADE_DURATION:
                    alpha = int(255 * (seg_duration - t_in_seg) / FADE_DURATION)
                else:
                    alpha = 255
                frame = render_couplet_frame(bg, line1, line2, alpha=alpha)

            elif seg_name == "end":
                black_opacity = int(255 * t_in_seg / seg_duration)
                frame_img = bg.copy().convert("RGBA")
                black = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, black_opacity))
                frame_img = Image.alpha_composite(frame_img, black)
                frame = frame_img.convert("RGB")
            else:
                proc.stdin.write(bg_bytes)
                continue

            proc.stdin.write(frame.tobytes())

    except BrokenPipeError:
        print("FFmpeg pipe closed unexpectedly.")
    finally:
        proc.stdin.close()

    stderr_output = proc.stderr.read()
    proc.wait()

    if proc.returncode != 0:
        print("FFmpeg error output:")
        print(stderr_output.decode("utf-8", errors="replace"))
        sys.exit(1)
    else:
        print(f"\nDone! Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    generate_video()

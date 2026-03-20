#!/usr/bin/env python3
"""SRT subtitle file generator for lyrics videos.

Reads the same lyrics.txt and TIMING config to produce a .srt file
for YouTube closed captions.
"""

import os

# ============================================================
# CONFIGURATION — Match these with your make_video.py settings
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LYRICS_FILE = os.path.join(BASE_DIR, "lyrics.txt")
OUTPUT_FILE = os.path.join(BASE_DIR, "subtitles.srt")

SONG_TITLE = "Song Title Here"
SONG_SUBTITLE = "Artist or Description"

# Same TIMING array as make_video.py
TIMING = [
    ("title",    0.0,   5.0),
    ("couplet1", 10.0,  25.0),
    ("couplet2", 27.0,  42.0),
    ("end",      0.0,   0.0),
]

# Repeat groups — merged into single subtitle entries
REPEAT_GROUPS = []

# ============================================================
# END CONFIGURATION
# ============================================================


def parse_lyrics(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    couplets = []
    i = 1
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


def format_time(seconds):
    """Format seconds as SRT timestamp HH:MM:SS,mmm"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def generate_subtitles():
    couplets = parse_lyrics(LYRICS_FILE)

    # Build repeat lookup: map second couplet to first
    repeat_second_to_first = {}
    for first, second in REPEAT_GROUPS:
        first_num = int(first.replace("couplet", ""))
        second_num = int(second.replace("couplet", ""))
        repeat_second_to_first[second_num] = first_num

    # Build couplet timing map
    couplet_timing = {}
    for seg_name, start, end in TIMING:
        if seg_name.startswith("couplet"):
            num = int(seg_name.replace("couplet", ""))
            couplet_timing[num] = (start, end)

    entries = []
    idx = 1

    # Title entry
    for seg_name, start, end in TIMING:
        if seg_name == "title":
            entries.append((idx, start, end, f"{SONG_TITLE}\n{SONG_SUBTITLE}"))
            idx += 1
            break

    # Couplet entries — merge repeats
    processed = set()
    for seg_name, start, end in TIMING:
        if not seg_name.startswith("couplet"):
            continue
        num = int(seg_name.replace("couplet", ""))
        if num in processed:
            continue

        couplet_idx = num - 1
        if couplet_idx >= len(couplets):
            continue

        line1, line2 = couplets[couplet_idx]

        # Check if this couplet has a repeat following it
        merged_end = end
        for first, second in REPEAT_GROUPS:
            first_num = int(first.replace("couplet", ""))
            second_num = int(second.replace("couplet", ""))
            if first_num == num and second_num in couplet_timing:
                merged_end = couplet_timing[second_num][1]
                processed.add(second_num)

        entries.append((idx, start, merged_end, f"{line1}\n{line2}"))
        processed.add(num)
        idx += 1

    # Write SRT
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for entry_idx, start, end, text in entries:
            f.write(f"{entry_idx}\n")
            f.write(f"{format_time(start)} --> {format_time(end)}\n")
            f.write(f"{text}\n\n")

    print(f"Subtitles saved: {OUTPUT_FILE} ({len(entries)} entries)")


if __name__ == "__main__":
    generate_subtitles()

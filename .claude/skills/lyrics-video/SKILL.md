---
name: lyrics-video
description: Generate a polished lyrics video from audio, lyrics, and background images. Use when the user wants to create a lyrics video, music video with subtitles, or karaoke-style video.
user-invocable: true
---

# Lyrics Video Generator

Create a polished lyrics video with bilingual subtitles, blended background images, and fade transitions. Outputs a YouTube-ready MP4 with optional 4K resolution, thumbnail, and SRT subtitle file.

## Requirements

- Python 3 with Pillow (`pip install Pillow`)
- FFmpeg installed and on PATH

## User Inputs Needed

Ask the user for the following. Be conversational — one question at a time:

1. **Audio source** — audio or video file to extract audio from (mp3, wav, mkv, mp4, etc.)
2. **Lyrics file** — text file with alternating lines: original language, then translation. Format:
   ```
   Song Title

   First line in original language
   Translation of first line

   Second line in original language
   Translation of second line
   ```
3. **Background images** — 1 or 2 images. If 2, they'll be blended (double-exposure style)
4. **Song title and subtitle** — for the title screen
5. **Verse timing** — when each verse starts. The user should listen to the audio and provide timestamps. Help them by listing each verse line and asking for the start time.
6. **Resolution** — 1080p (1920x1080) or 4K (3840x2160). Default: 4K for YouTube upload quality.

## How to Generate

Use the template script at `TEMPLATE.py` in this skill's directory. Copy it to the user's working directory as `make_video.py` and customize the config section at the top based on user inputs:

- Set `AUDIO_FILE`, `IMG_BASE`, `IMG_OVERLAY` (or `None` if single image), `OUTPUT_FILE`
- Set `SONG_TITLE`, `SONG_SUBTITLE`
- Set `WIDTH`, `HEIGHT` based on resolution choice
- Set font sizes: for 1080p use 64/48/36, for 4K use 160/120/90
- Set `line_spacing`: 12 for 1080p, 24 for 4K
- Set `shadow_offset`: 2 for 1080p, 4 for 4K
- Set `TIMING` array based on user-provided verse timestamps
- Set `REPEAT_GROUPS` to list pairs of couplets that share the same text (e.g., `[("couplet2", "couplet3")]`) so transitions are skipped between repeats

### Font Selection

Find available serif fonts on the user's system:
- **macOS**: Check `/System/Library/Fonts/Supplemental/` for Georgia, Times New Roman
- **Linux**: Check `/usr/share/fonts/` or use `fc-list | grep -i serif`
- **Windows**: Check `C:\Windows\Fonts\` for georgia.ttf, times.ttf

The font must support the character set of the lyrics (e.g., Turkish, Arabic, CJK).

### Timing Workflow

1. List each verse line and ask the user when it starts
2. For the end time of each verse, estimate ~15-20 seconds after start, or until the next verse starts
3. For repeated verses (same text sung twice), overlap the timing so text stays on screen continuously
4. Add a title segment at 0-5 seconds and an end fade-to-black for the last 3-5 seconds

### After Generation

Offer to also create:
- **YouTube thumbnail** (same resolution) — blended background with title text and gradient
- **SRT subtitle file** — for YouTube closed captions
- **YouTube metadata** — title, description with lyrics, tags, and category suggestions

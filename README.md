# Lyrics Video Generator

Generate polished lyrics videos from audio, lyrics, and background images. Perfect for YouTube uploads with bilingual subtitles, fade transitions, and blended backgrounds.

## Features

- 4K (3840x2160) or 1080p (1920x1080) output
- Bilingual lyrics (original + translation) with fade-in/fade-out
- Double-exposure background blending from two images
- Configurable timing, fonts, colors, and positioning
- YouTube thumbnail generator
- SRT subtitle file generator
- Smooth transitions with repeat-verse awareness

## Requirements

- Python 3.8+
- [Pillow](https://pillow.readthedocs.io/) (`pip install Pillow`)
- [FFmpeg](https://ffmpeg.org/download.html) installed and on PATH

## Quick Start

```bash
# Clone the repo
git clone https://github.com/akashmeshram/lyrics-video-generator.git
cd lyrics-video-generator

# Install Python dependency
pip install Pillow

# Copy the template to your project folder
cp make_video.py /path/to/your/project/
cp thumbnail.py /path/to/your/project/

# Edit the config section at the top of make_video.py
# Then run:
python3 make_video.py

# Generate thumbnail:
python3 thumbnail.py

# Generate subtitles:
python3 subtitles.py
```

## Project Setup

Place these files in your project folder:

```
my-lyrics-video/
├── make_video.py       # Copy from this repo, edit config section
├── thumbnail.py        # Copy from this repo, edit config section
├── subtitles.py        # Copy from this repo, edit config section
├── audio.mp3           # Your audio file (mp3, wav, mkv, mp4, etc.)
├── lyrics.txt          # Your lyrics file (see format below)
├── background1.jpg     # Primary background image
└── background2.jpg     # Optional: second image for double-exposure blend
```

## Lyrics File Format

```
Song Title

First verse in original language
Translation of first verse

Second verse in original language
Translation of second verse

Third verse (repeat of second)
Translation (repeat)
```

Each verse is a pair of lines (original + translation) separated by blank lines. The first line is the song title.

## Configuration

All settings are in the config section at the top of each script. Key settings:

| Setting | Description | Default |
|---------|-------------|---------|
| `WIDTH, HEIGHT` | Resolution | `3840, 2160` (4K) |
| `AUDIO_FILE` | Path to audio source | `audio.mp3` |
| `IMG_BASE` | Primary background image | `background1.jpg` |
| `IMG_OVERLAY` | Second image (or `None`) | `background2.jpg` |
| `OVERLAY_OPACITY` | Blend opacity (0.0-1.0) | `0.4` |
| `DARK_OVERLAY` | Darken for readability (0.0-1.0) | `0.3` |
| `FONT_REGULAR` | Path to regular font .ttf | Georgia |
| `FONT_ITALIC` | Path to italic font .ttf | Georgia Italic |
| `LINE1_COLOR` | Original lyrics color | `(255, 255, 255)` white |
| `LINE2_COLOR` | Translation color | `(220, 200, 160)` warm yellow |
| `LYRICS_POSITION` | Vertical position (0.0-1.0) | `0.70` |
| `TIMING` | Verse start/end timestamps | See below |
| `REPEAT_GROUPS` | Verse pairs with same text | `[]` |

### Timing

Listen to your audio and note when each verse starts and ends:

```python
TIMING = [
    ("title",    0.0,   5.0),     # Title screen
    ("couplet1", 10.0,  25.0),    # First verse
    ("couplet2", 27.0,  42.0),    # Second verse
    ("couplet3", 44.0,  59.0),    # Third verse
    ("end",      117.0, 120.0),   # Fade to black
]
```

### Repeat Groups

If verses repeat (same lyrics sung twice), skip transitions between them:

```python
REPEAT_GROUPS = [
    ("couplet2", "couplet3"),   # Verses 2 and 3 have identical text
]
```

### Font Paths by OS

| OS | Path |
|----|------|
| macOS | `/System/Library/Fonts/Supplemental/Georgia.ttf` |
| Linux | `/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf` |
| Windows | `C:/Windows/Fonts/georgia.ttf` |

## Claude Code Skill

This repo includes a Claude Code skill for interactive video creation. Install it:

```bash
# Copy to your global skills directory
cp -r .claude/skills/lyrics-video ~/.claude/skills/

# Then in any project, run:
# /lyrics-video
```

Claude will walk you through the entire process interactively.

## Examples

See the `examples/` directory for a sample lyrics video project.

## License

MIT

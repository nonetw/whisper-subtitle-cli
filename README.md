# Video Subtitle Extractor

Extract subtitles from video files using AI transcription (OpenAI Whisper). Generates both SRT files for video playback and plain text files for easy reading.

## Features

- **AI-Powered Transcription**: Uses Faster Whisper for accurate speech-to-text
- **Dual Output**: Creates both SRT (with timestamps) and TXT (plain text) files
- **Multiple Languages**: Auto-detects language or accepts manual specification
- **Flexible Models**: Choose from 5 model sizes balancing speed vs accuracy
- **CLI Interface**: Simple command-line tool with helpful options

## Requirements

- Python 3.11 or 3.12
- ffmpeg (for audio extraction)
- Poetry (for package management)

### Install ffmpeg

```bash
# macOS
brew install ffmpeg

# Linux (Ubuntu/Debian)
sudo apt install ffmpeg

# Linux (Fedora)
sudo dnf install ffmpeg
```

## Installation

1. Clone or download this project

2. Install dependencies with Poetry:
```bash
poetry install --no-root
```

## Usage

### Basic Usage

Extract subtitles from a video file:

```bash
python main.py video.mp4
```

This creates two files:
- `video.srt` - Subtitle file with timestamps (for video players)
- `video.txt` - Plain text transcript (for reading)

### Advanced Options

```bash
# Use a more accurate model (takes longer)
python main.py video.mp4 --model medium

# Specify the language (faster than auto-detect)
python main.py video.mp4 --language en

# Save output to a specific directory
python main.py video.mp4 --output ./subtitles

# Keep the extracted audio file
python main.py video.mp4 --keep-audio
```

### Model Options

| Model | Size | Speed | Accuracy | Use Case |
|-------|------|-------|----------|----------|
| tiny | ~39MB | Fastest | Basic | Quick tests, simple audio |
| base | ~140MB | Fast | Good | **Default - balanced** |
| small | ~470MB | Moderate | Better | Clear speech, important content |
| medium | ~1.5GB | Slow | High | Professional use |
| large | ~2.9GB | Slowest | Best | Maximum accuracy needed |

### Language Codes

Common language codes (or use auto-detect by omitting):
- `en` - English
- `zh` - Chinese
- `es` - Spanish
- `fr` - French
- `de` - German
- `ja` - Japanese
- `ko` - Korean

[Full list of supported languages](https://github.com/openai/whisper#available-models-and-languages)

## Examples

```bash
# Process an English video with the base model (default)
python main.py lecture.mp4

# Process a Chinese video with high accuracy
python main.py chinese_video.mp4 --model medium --language zh

# Process multiple videos (one at a time)
python main.py video1.mp4
python main.py video2.mp4

# Save all outputs to a subtitles folder
mkdir subtitles
python main.py video.mp4 --output ./subtitles
```

## Output Format

### SRT Format (video.srt)
```
1
00:00:00,000 --> 00:00:02,500
Hello, world!

2
00:00:02,500 --> 00:00:05,000
This is a test.
```

### Plain Text Format (video.txt)
```
Hello, world!

This is a test.
```

## Supported Video Formats

Any format supported by ffmpeg:
- MP4
- MKV
- AVI
- MOV
- WebM
- FLV
- and many more

## Development

### Running Tests

```bash
# Run all tests
poetry run pytest -v

# Run specific test file
poetry run pytest tests/test_transcriber.py -v
```

### Project Structure

```
video-subtitle/
├── src/
│   ├── audio_extractor.py    # Extract audio from video
│   ├── transcriber.py         # AI transcription
│   └── subtitle_writer.py     # Write SRT and TXT files
├── tests/                     # Unit tests
├── main.py                    # CLI entry point
├── pyproject.toml             # Poetry dependencies
└── CLAUDE.md                  # Project documentation
```

## Troubleshooting

### "ffmpeg not found"
Install ffmpeg using your package manager (see Requirements section).

### "No module named 'src'"
Make sure you're running the script from the project root directory.

### Slow transcription
Use a smaller model (`--model tiny` or `--model base`) or specify the language to avoid auto-detection.

### Out of memory
Use a smaller model. The `base` model uses ~1GB RAM, while `large` needs ~10GB.

## License

This project uses:
- faster-whisper (MIT License)
- OpenAI Whisper models (MIT License)
- ffmpeg (LGPL/GPL)

## Acknowledgments

Built with:
- [Faster Whisper](https://github.com/guillaumekln/faster-whisper) - Fast Whisper implementation
- [OpenAI Whisper](https://github.com/openai/whisper) - Original Whisper models
- [FFmpeg](https://ffmpeg.org/) - Audio/video processing

#!/usr/bin/env python
"""
Video Subtitle Extractor

Extract subtitles from video files using AI transcription (Whisper).
Outputs both SRT format (for video players) and plain text (for reading).
"""

import click
import os
import sys
from pathlib import Path

from src.audio_extractor import AudioExtractor
from src.transcriber import Transcriber
from src.subtitle_writer import SubtitleWriter


@click.command()
@click.argument('video_file', type=click.Path(exists=True))
@click.option(
    '--model',
    default='base',
    type=click.Choice(['tiny', 'base', 'small', 'medium', 'large'], case_sensitive=False),
    help='Whisper model size (larger = more accurate but slower)'
)
@click.option(
    '--language',
    default=None,
    help='Language code (e.g., en, zh, es). Auto-detect if not specified.'
)
@click.option(
    '--output',
    '-o',
    default=None,
    type=click.Path(),
    help='Output directory (default: same as video file)'
)
@click.option(
    '--keep-audio',
    is_flag=True,
    default=False,
    help='Keep the extracted audio file (WAV)'
)
def main(video_file, model, language, output, keep_audio):
    """
    Extract subtitles from VIDEO_FILE using AI transcription.

    Generates two files:
    - .srt file (for video players with timestamps)
    - .txt file (plain text for easy reading)

    Example:
        python main.py video.mp4
        python main.py video.mp4 --model medium --language en
    """
    try:
        video_path = Path(video_file).resolve()
        click.echo(f"Processing: {video_path.name}")

        # Determine output directory
        if output:
            output_dir = Path(output)
            output_dir.mkdir(parents=True, exist_ok=True)
        else:
            output_dir = video_path.parent

        # Generate output file paths
        base_name = video_path.stem
        audio_path = output_dir / f"{base_name}.wav"
        srt_path = output_dir / f"{base_name}.srt"
        txt_path = output_dir / f"{base_name}.txt"

        # Step 1: Extract audio
        click.echo("\n[1/3] Extracting audio from video...")
        extractor = AudioExtractor()
        extractor.extract_audio(str(video_path), str(audio_path))
        click.echo(f"✓ Audio extracted to: {audio_path.name}")

        # Step 2: Transcribe audio
        click.echo(f"\n[2/3] Transcribing audio (model: {model})...")
        if language:
            click.echo(f"      Language: {language}")
        else:
            click.echo("      Language: auto-detect")

        transcriber = Transcriber(model_size=model)
        segments = transcriber.transcribe(str(audio_path), language=language)
        click.echo(f"✓ Transcription complete ({len(segments)} segments)")

        # Step 3: Write subtitle files
        click.echo("\n[3/3] Writing subtitle files...")
        writer = SubtitleWriter()

        writer.write_srt(segments, str(srt_path))
        click.echo(f"✓ SRT file created: {srt_path}")

        writer.write_txt(segments, str(txt_path))
        click.echo(f"✓ Text file created: {txt_path}")

        # Clean up audio file if not keeping it
        if not keep_audio and audio_path.exists():
            audio_path.unlink()
            click.echo(f"\n✓ Cleaned up temporary audio file")
        elif keep_audio:
            click.echo(f"\n✓ Audio file kept: {audio_path}")

        click.echo("\n✅ Done! Subtitle extraction complete.")
        click.echo(f"\nOutput files:")
        click.echo(f"  • {srt_path.name} (for video playback)")
        click.echo(f"  • {txt_path.name} (for reading)")

    except FileNotFoundError as e:
        click.echo(f"\n❌ Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"\n❌ Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()

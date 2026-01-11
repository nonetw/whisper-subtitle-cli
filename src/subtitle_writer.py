from typing import List, Dict
from pathlib import Path


class SubtitleWriter:
    """Writes subtitle files in SRT and plain text formats."""

    def write_srt(self, segments: List[Dict], output_path: str) -> None:
        """
        Write segments to an SRT (SubRip) subtitle file.

        SRT format:
        1
        00:00:00,000 --> 00:00:02,500
        Hello, world!

        2
        00:00:02,500 --> 00:00:05,000
        This is a test.

        Args:
            segments: List of segments with 'start', 'end', 'text' keys
            output_path: Path to save the SRT file
        """
        if not segments:
            Path(output_path).write_text("")
            return

        lines = []
        for i, segment in enumerate(segments, start=1):
            # Sequence number
            lines.append(str(i))

            # Timestamp line
            start_time = self._format_timestamp(segment['start'])
            end_time = self._format_timestamp(segment['end'])
            lines.append(f"{start_time} --> {end_time}")

            # Text content
            lines.append(segment['text'])

            # Blank line between entries
            lines.append("")

        content = "\n".join(lines)
        Path(output_path).write_text(content, encoding='utf-8')

    def write_txt(self, segments: List[Dict], output_path: str) -> None:
        """
        Write segments to a plain text file.

        Format: Just the text content, one segment per paragraph.

        Args:
            segments: List of segments with 'text' key
            output_path: Path to save the text file
        """
        if not segments:
            Path(output_path).write_text("")
            return

        # Extract just the text from each segment
        text_lines = [segment['text'] for segment in segments]

        # Join with double newlines for readability
        content = "\n\n".join(text_lines)

        Path(output_path).write_text(content, encoding='utf-8')

    def _format_timestamp(self, seconds: float) -> str:
        """
        Format seconds as SRT timestamp: HH:MM:SS,mmm

        Args:
            seconds: Time in seconds

        Returns:
            Formatted timestamp string
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds % 1) * 1000)

        return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"

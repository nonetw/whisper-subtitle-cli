from typing import List, Dict
from pathlib import Path
import re
import math


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

    def write_timestamped_txt(self, segments: List[Dict], output_path: str) -> None:
        """
        Write segments to a timestamped text file.

        Format: One line per segment with inline timestamp.
        Perfect for copying to translation tools while preserving timing.

        Example:
        [00:00:00,000 --> 00:00:02,500] Hello, world!
        [00:00:02,500 --> 00:00:05,000] This is a test.

        Args:
            segments: List of segments with 'start', 'end', 'text' keys
            output_path: Path to save the timestamped text file
        """
        if not segments:
            Path(output_path).write_text("")
            return

        lines = []
        for segment in segments:
            start_time = self._format_timestamp(segment['start'])
            end_time = self._format_timestamp(segment['end'])
            text = segment['text']
            lines.append(f"[{start_time} --> {end_time}] {text}")

        content = "\n".join(lines)
        Path(output_path).write_text(content, encoding='utf-8')

    def split_timestamped_txt(
        self,
        timestamped_txt_path: str,
        segments_per_chunk: int = 100
    ) -> List[str]:
        """
        Split a timestamped text file into smaller chunks for AI translation.

        Args:
            timestamped_txt_path: Path to the timestamped.txt file to split
            segments_per_chunk: Number of segments per chunk (default: 100)

        Returns:
            List of created chunk file paths

        Example:
            Input: 20260112_video.timestamped.txt (250 segments)
            Output with segments_per_chunk=100:
                - 20260112_video.timestamped.chunk001of003.txt (100 segments)
                - 20260112_video.timestamped.chunk002of003.txt (100 segments)
                - 20260112_video.timestamped.chunk003of003.txt (50 segments)
        """
        # Read the timestamped file
        timestamped_path = Path(timestamped_txt_path)
        if not timestamped_path.exists():
            raise FileNotFoundError(f"Timestamped file not found: {timestamped_txt_path}")

        lines = timestamped_path.read_text(encoding='utf-8').splitlines()

        # Handle empty file
        if not lines:
            return []

        # Calculate number of chunks
        total_chunks = math.ceil(len(lines) / segments_per_chunk)

        # Extract base filename (remove .timestamped.txt extension)
        # Example: 20260112_video.timestamped.txt -> 20260112_video
        base_name = timestamped_path.stem  # Removes .txt
        if base_name.endswith('.timestamped'):
            base_name = base_name[:-len('.timestamped')]

        # Get the directory where the original file is located
        output_dir = timestamped_path.parent

        # Create chunk files
        chunk_files = []
        for chunk_idx in range(total_chunks):
            start_idx = chunk_idx * segments_per_chunk
            end_idx = min((chunk_idx + 1) * segments_per_chunk, len(lines))
            chunk_lines = lines[start_idx:end_idx]

            # Generate chunk filename
            chunk_num = chunk_idx + 1
            chunk_filename = f"{base_name}.timestamped.chunk{chunk_num:03d}of{total_chunks:03d}.txt"
            chunk_path = output_dir / chunk_filename

            # Write chunk file
            chunk_content = "\n".join(chunk_lines)
            chunk_path.write_text(chunk_content, encoding='utf-8')

            chunk_files.append(str(chunk_path))

        return chunk_files

    @staticmethod
    def parse_srt(srt_path: str) -> List[Dict]:
        """
        Parse an SRT file into a list of segments.

        Args:
            srt_path: Path to the SRT file

        Returns:
            List of segments with 'start', 'end', 'text' keys

        Raises:
            FileNotFoundError: If SRT file doesn't exist
        """
        content = Path(srt_path).read_text(encoding='utf-8')

        # Split into blocks (separated by double newlines)
        blocks = re.split(r'\n\n+', content.strip())

        segments = []
        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) < 3:
                continue  # Skip malformed blocks

            # Line 0: sequence number (ignore)
            # Line 1: timestamp
            # Line 2+: text content

            timestamp_line = lines[1]
            text = '\n'.join(lines[2:])

            # Parse timestamp: "00:00:00,000 --> 00:00:02,500"
            match = re.match(r'(\d{2}):(\d{2}):(\d{2}),(\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2}),(\d{3})', timestamp_line)
            if match:
                start_h, start_m, start_s, start_ms, end_h, end_m, end_s, end_ms = match.groups()

                start_seconds = (
                    int(start_h) * 3600 +
                    int(start_m) * 60 +
                    int(start_s) +
                    int(start_ms) / 1000
                )

                end_seconds = (
                    int(end_h) * 3600 +
                    int(end_m) * 60 +
                    int(end_s) +
                    int(end_ms) / 1000
                )

                segments.append({
                    'start': start_seconds,
                    'end': end_seconds,
                    'text': text
                })

        return segments

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

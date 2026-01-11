import pytest
import os
import tempfile
from pathlib import Path
from src.subtitle_writer import SubtitleWriter


class TestSubtitleWriter:
    @pytest.fixture
    def sample_segments(self):
        """Sample transcription segments for testing."""
        return [
            {'start': 0.0, 'end': 2.5, 'text': 'Hello, world!'},
            {'start': 2.5, 'end': 5.0, 'text': 'This is a test.'},
            {'start': 5.0, 'end': 8.3, 'text': 'Testing subtitle generation.'},
        ]

    def test_writer_initialization(self):
        """Test that writer can be initialized."""
        writer = SubtitleWriter()
        assert writer is not None

    def test_write_srt_creates_file(self, sample_segments):
        """Test that SRT file is created."""
        writer = SubtitleWriter()

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.srt"
            writer.write_srt(sample_segments, str(output_path))

            assert output_path.exists()

    def test_write_srt_correct_format(self, sample_segments):
        """Test that SRT file has correct format."""
        writer = SubtitleWriter()

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.srt"
            writer.write_srt(sample_segments, str(output_path))

            content = output_path.read_text()

            # SRT format should have:
            # 1. Sequence numbers
            # 2. Timestamps in format: HH:MM:SS,mmm --> HH:MM:SS,mmm
            # 3. Text content
            # 4. Blank lines between entries

            assert "1\n" in content
            assert "00:00:00,000 --> 00:00:02,500" in content
            assert "Hello, world!" in content
            assert "2\n" in content
            assert "This is a test." in content

    def test_write_txt_creates_file(self, sample_segments):
        """Test that plain text file is created."""
        writer = SubtitleWriter()

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.txt"
            writer.write_txt(sample_segments, str(output_path))

            assert output_path.exists()

    def test_write_txt_correct_format(self, sample_segments):
        """Test that plain text file has correct format."""
        writer = SubtitleWriter()

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.txt"
            writer.write_txt(sample_segments, str(output_path))

            content = output_path.read_text()

            # Plain text should just have the text content
            # without timestamps or sequence numbers
            assert "Hello, world!" in content
            assert "This is a test." in content
            assert "Testing subtitle generation." in content

            # Should NOT contain timestamps or numbers
            assert "00:00:00" not in content
            assert "1\n" not in content or content.count("1\n") == 0

    def test_format_timestamp(self):
        """Test timestamp formatting for SRT."""
        writer = SubtitleWriter()

        # Test various timestamps
        assert writer._format_timestamp(0.0) == "00:00:00,000"
        assert writer._format_timestamp(2.5) == "00:00:02,500"
        assert writer._format_timestamp(65.123) == "00:01:05,123"
        assert writer._format_timestamp(3661.5) == "01:01:01,500"

    def test_empty_segments(self):
        """Test handling of empty segments list."""
        writer = SubtitleWriter()

        with tempfile.TemporaryDirectory() as tmpdir:
            srt_path = Path(tmpdir) / "empty.srt"
            txt_path = Path(tmpdir) / "empty.txt"

            writer.write_srt([], str(srt_path))
            writer.write_txt([], str(txt_path))

            assert srt_path.exists()
            assert txt_path.exists()
            assert srt_path.read_text() == ""
            assert txt_path.read_text() == ""

    def test_write_timestamped_txt_creates_file(self, sample_segments):
        """Test that timestamped text file is created."""
        writer = SubtitleWriter()

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.timestamped.txt"
            writer.write_timestamped_txt(sample_segments, str(output_path))

            assert output_path.exists()

    def test_write_timestamped_txt_correct_format(self, sample_segments):
        """Test that timestamped text file has correct format."""
        writer = SubtitleWriter()

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.timestamped.txt"
            writer.write_timestamped_txt(sample_segments, str(output_path))

            content = output_path.read_text()

            # Should have timestamps in brackets followed by text
            assert "[00:00:00,000 --> 00:00:02,500] Hello, world!" in content
            assert "[00:00:02,500 --> 00:00:05,000] This is a test." in content
            assert "[00:00:05,000 --> 00:00:08,300] Testing subtitle generation." in content

            # Should NOT have sequence numbers
            assert not content.startswith("1\n")

    def test_parse_srt_reads_file(self, sample_segments):
        """Test that SRT file can be parsed back to segments."""
        writer = SubtitleWriter()

        with tempfile.TemporaryDirectory() as tmpdir:
            srt_path = Path(tmpdir) / "test.srt"
            writer.write_srt(sample_segments, str(srt_path))

            # Parse it back
            parsed_segments = SubtitleWriter.parse_srt(str(srt_path))

            assert len(parsed_segments) == 3
            assert parsed_segments[0]['text'] == 'Hello, world!'
            assert parsed_segments[1]['text'] == 'This is a test.'
            assert parsed_segments[2]['text'] == 'Testing subtitle generation.'

    def test_parse_srt_preserves_timestamps(self, sample_segments):
        """Test that parsing SRT preserves timestamp information."""
        writer = SubtitleWriter()

        with tempfile.TemporaryDirectory() as tmpdir:
            srt_path = Path(tmpdir) / "test.srt"
            writer.write_srt(sample_segments, str(srt_path))

            # Parse it back
            parsed_segments = SubtitleWriter.parse_srt(str(srt_path))

            # Check timestamps are preserved (with small tolerance for float precision)
            assert abs(parsed_segments[0]['start'] - 0.0) < 0.01
            assert abs(parsed_segments[0]['end'] - 2.5) < 0.01
            assert abs(parsed_segments[1]['start'] - 2.5) < 0.01
            assert abs(parsed_segments[1]['end'] - 5.0) < 0.01

    def test_parse_srt_roundtrip(self, sample_segments):
        """Test that write_srt -> parse_srt -> write_srt produces same content."""
        writer = SubtitleWriter()

        with tempfile.TemporaryDirectory() as tmpdir:
            srt_path1 = Path(tmpdir) / "test1.srt"
            srt_path2 = Path(tmpdir) / "test2.srt"

            # Write original
            writer.write_srt(sample_segments, str(srt_path1))

            # Parse and write again
            parsed = SubtitleWriter.parse_srt(str(srt_path1))
            writer.write_srt(parsed, str(srt_path2))

            # Content should be identical
            content1 = srt_path1.read_text()
            content2 = srt_path2.read_text()

            assert content1 == content2

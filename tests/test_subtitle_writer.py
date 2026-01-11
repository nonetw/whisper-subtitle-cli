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

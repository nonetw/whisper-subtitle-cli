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

    def test_split_timestamped_txt_creates_chunks(self):
        """Test splitting creates multiple chunk files with correct naming."""
        writer = SubtitleWriter()

        # Create 250 segments for testing
        segments = []
        for i in range(250):
            segments.append({
                'start': i * 2.0,
                'end': (i + 1) * 2.0,
                'text': f'Segment {i + 1}'
            })

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create original timestamped.txt file
            timestamped_path = Path(tmpdir) / "20260112_test_video.timestamped.txt"
            writer.write_timestamped_txt(segments, str(timestamped_path))

            # Split into chunks of 100 segments
            chunk_files = writer.split_timestamped_txt(str(timestamped_path), segments_per_chunk=100)

            # Should create 3 chunks (100, 100, 50)
            assert len(chunk_files) == 3

            # Verify chunk files exist and have correct naming
            chunk1 = Path(tmpdir) / "20260112_test_video.timestamped.chunk001of003.txt"
            chunk2 = Path(tmpdir) / "20260112_test_video.timestamped.chunk002of003.txt"
            chunk3 = Path(tmpdir) / "20260112_test_video.timestamped.chunk003of003.txt"

            assert chunk1.exists()
            assert chunk2.exists()
            assert chunk3.exists()

            # Verify returned paths match
            assert str(chunk1) in chunk_files
            assert str(chunk2) in chunk_files
            assert str(chunk3) in chunk_files

    def test_split_timestamped_txt_correct_distribution(self):
        """Test segments are distributed correctly across chunks."""
        writer = SubtitleWriter()

        # Create 250 segments
        segments = []
        for i in range(250):
            segments.append({
                'start': i * 2.0,
                'end': (i + 1) * 2.0,
                'text': f'Segment {i + 1}'
            })

        with tempfile.TemporaryDirectory() as tmpdir:
            timestamped_path = Path(tmpdir) / "test.timestamped.txt"
            writer.write_timestamped_txt(segments, str(timestamped_path))

            # Split into chunks of 100
            chunk_files = writer.split_timestamped_txt(str(timestamped_path), segments_per_chunk=100)

            # Check first chunk has 100 lines
            chunk1_content = Path(chunk_files[0]).read_text().splitlines()
            assert len(chunk1_content) == 100

            # Check second chunk has 100 lines
            chunk2_content = Path(chunk_files[1]).read_text().splitlines()
            assert len(chunk2_content) == 100

            # Check third chunk has 50 lines (remainder)
            chunk3_content = Path(chunk_files[2]).read_text().splitlines()
            assert len(chunk3_content) == 50

    def test_split_timestamped_txt_preserves_format(self):
        """Test each chunk maintains timestamped format."""
        writer = SubtitleWriter()

        segments = []
        for i in range(150):
            segments.append({
                'start': i * 1.5,
                'end': (i + 1) * 1.5,
                'text': f'Text segment {i + 1}'
            })

        with tempfile.TemporaryDirectory() as tmpdir:
            timestamped_path = Path(tmpdir) / "test.timestamped.txt"
            writer.write_timestamped_txt(segments, str(timestamped_path))

            chunk_files = writer.split_timestamped_txt(str(timestamped_path), segments_per_chunk=100)

            # Check each chunk maintains the [HH:MM:SS,mmm --> HH:MM:SS,mmm] format
            for chunk_file in chunk_files:
                content = Path(chunk_file).read_text()
                lines = content.splitlines()

                # Every line should have timestamp format
                for line in lines:
                    assert line.startswith('[')
                    assert '-->' in line
                    assert ']' in line

    def test_split_timestamped_txt_small_file(self):
        """Test splitting file smaller than chunk size."""
        writer = SubtitleWriter()

        # Create only 30 segments
        segments = []
        for i in range(30):
            segments.append({
                'start': i * 2.0,
                'end': (i + 1) * 2.0,
                'text': f'Segment {i + 1}'
            })

        with tempfile.TemporaryDirectory() as tmpdir:
            timestamped_path = Path(tmpdir) / "small.timestamped.txt"
            writer.write_timestamped_txt(segments, str(timestamped_path))

            # Split with chunk size 100 (larger than file)
            chunk_files = writer.split_timestamped_txt(str(timestamped_path), segments_per_chunk=100)

            # Should create only 1 chunk
            assert len(chunk_files) == 1

            # Check filename pattern: chunk001of001
            chunk_filename = Path(chunk_files[0]).name
            assert 'chunk001of001' in chunk_filename

            # Verify it has all 30 lines
            content = Path(chunk_files[0]).read_text().splitlines()
            assert len(content) == 30

    def test_split_timestamped_txt_exact_multiple(self):
        """Test splitting file that's exact multiple of chunk size."""
        writer = SubtitleWriter()

        # Create exactly 200 segments
        segments = []
        for i in range(200):
            segments.append({
                'start': i * 2.0,
                'end': (i + 1) * 2.0,
                'text': f'Segment {i + 1}'
            })

        with tempfile.TemporaryDirectory() as tmpdir:
            timestamped_path = Path(tmpdir) / "exact.timestamped.txt"
            writer.write_timestamped_txt(segments, str(timestamped_path))

            # Split with chunk size 100 (exactly 2 chunks)
            chunk_files = writer.split_timestamped_txt(str(timestamped_path), segments_per_chunk=100)

            # Should create exactly 2 chunks
            assert len(chunk_files) == 2

            # Both chunks should have 100 lines
            chunk1_content = Path(chunk_files[0]).read_text().splitlines()
            chunk2_content = Path(chunk_files[1]).read_text().splitlines()
            assert len(chunk1_content) == 100
            assert len(chunk2_content) == 100

            # Check filenames
            assert 'chunk001of002' in Path(chunk_files[0]).name
            assert 'chunk002of002' in Path(chunk_files[1]).name

    def test_split_timestamped_txt_returns_file_paths(self):
        """Test method returns list of created file paths."""
        writer = SubtitleWriter()

        segments = []
        for i in range(50):
            segments.append({
                'start': i * 2.0,
                'end': (i + 1) * 2.0,
                'text': f'Segment {i + 1}'
            })

        with tempfile.TemporaryDirectory() as tmpdir:
            timestamped_path = Path(tmpdir) / "test.timestamped.txt"
            writer.write_timestamped_txt(segments, str(timestamped_path))

            chunk_files = writer.split_timestamped_txt(str(timestamped_path), segments_per_chunk=100)

            # Should return a list
            assert isinstance(chunk_files, list)

            # Should contain strings (file paths)
            assert all(isinstance(path, str) for path in chunk_files)

            # All paths should exist
            assert all(Path(path).exists() for path in chunk_files)

    def test_split_timestamped_txt_filename_format(self):
        """Test chunk filename format is correct."""
        writer = SubtitleWriter()

        segments = []
        for i in range(150):
            segments.append({
                'start': i * 2.0,
                'end': (i + 1) * 2.0,
                'text': f'Segment {i + 1}'
            })

        with tempfile.TemporaryDirectory() as tmpdir:
            # Test with date prefix in filename
            timestamped_path = Path(tmpdir) / "20260112_my_video.timestamped.txt"
            writer.write_timestamped_txt(segments, str(timestamped_path))

            chunk_files = writer.split_timestamped_txt(str(timestamped_path), segments_per_chunk=100)

            # Should create 2 chunks
            assert len(chunk_files) == 2

            # Verify filename format preserves base name
            chunk1_name = Path(chunk_files[0]).name
            chunk2_name = Path(chunk_files[1]).name

            assert chunk1_name == "20260112_my_video.timestamped.chunk001of002.txt"
            assert chunk2_name == "20260112_my_video.timestamped.chunk002of002.txt"

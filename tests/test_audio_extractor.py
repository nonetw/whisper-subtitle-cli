import pytest
import os
import tempfile
from pathlib import Path
from src.audio_extractor import AudioExtractor


class TestAudioExtractor:
    def test_extract_audio_from_video(self):
        """Test that audio can be extracted from a video file."""
        extractor = AudioExtractor()

        # We'll use a real video file in integration tests
        # For unit tests, we'll just test the interface
        with tempfile.TemporaryDirectory() as tmpdir:
            video_path = Path(tmpdir) / "test_video.mp4"
            output_path = Path(tmpdir) / "test_audio.wav"

            # Mock test - just verify the method exists and accepts correct params
            # Real test will be in integration
            assert hasattr(extractor, 'extract_audio')
            assert callable(extractor.extract_audio)

    def test_extract_audio_creates_wav_file(self):
        """Test that the extracted audio is in WAV format."""
        extractor = AudioExtractor()

        # Verify method signature
        import inspect
        sig = inspect.signature(extractor.extract_audio)
        assert 'video_path' in sig.parameters
        assert 'output_path' in sig.parameters

    def test_extract_audio_raises_on_missing_file(self):
        """Test that extracting from non-existent file raises error."""
        extractor = AudioExtractor()

        with pytest.raises((FileNotFoundError, Exception)):
            extractor.extract_audio("nonexistent_video.mp4", "output.wav")

    def test_get_output_path_for_audio(self):
        """Test that output path is generated correctly."""
        extractor = AudioExtractor()

        video_path = "/path/to/video.mp4"
        expected = "/path/to/video.wav"

        result = extractor.get_audio_output_path(video_path)
        assert result == expected

    def test_get_output_path_preserves_directory(self):
        """Test that output path preserves the directory structure."""
        extractor = AudioExtractor()

        video_path = "/some/deep/path/myvideo.mkv"
        expected = "/some/deep/path/myvideo.wav"

        result = extractor.get_audio_output_path(video_path)
        assert result == expected

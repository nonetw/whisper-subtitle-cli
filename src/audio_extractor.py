import os
import ffmpeg
from pathlib import Path


class AudioExtractor:
    """Extracts audio from video files using ffmpeg."""

    def extract_audio(self, video_path: str, output_path: str) -> str:
        """
        Extract audio from a video file and save as WAV.

        Args:
            video_path: Path to the input video file
            output_path: Path to save the extracted audio

        Returns:
            Path to the extracted audio file

        Raises:
            FileNotFoundError: If the video file doesn't exist
            Exception: If ffmpeg extraction fails
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        try:
            # Extract audio using ffmpeg
            # Convert to WAV format for better compatibility with Whisper
            stream = ffmpeg.input(video_path)
            stream = ffmpeg.output(stream, output_path, acodec='pcm_s16le', ac=1, ar='16000')
            ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)

            return output_path
        except ffmpeg.Error as e:
            stderr = e.stderr.decode() if e.stderr else "Unknown error"
            raise Exception(f"Failed to extract audio: {stderr}")

    def get_audio_output_path(self, video_path: str) -> str:
        """
        Generate the output path for the extracted audio file.

        Args:
            video_path: Path to the input video file

        Returns:
            Path for the output audio file (same directory, .wav extension)
        """
        path = Path(video_path)
        return str(path.with_suffix('.wav'))

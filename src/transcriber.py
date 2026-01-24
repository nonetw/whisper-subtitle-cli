from faster_whisper import WhisperModel
from typing import List, Dict, Optional


class Transcriber:
    """Transcribes audio files using Faster Whisper."""

    def __init__(self, model_size: str = "medium"):
        """
        Initialize the transcriber with a Whisper model.
        Automatically detects GPU availability and uses CUDA if possible.

        Args:
            model_size: Size of the Whisper model (tiny, base, small, medium, large)
        """
        self.model_size = model_size
        self.device, self.compute_type = self._detect_device()
        self.model = None

    @staticmethod
    def _detect_device():
        """Detect whether CUDA is available and return appropriate device settings."""
        try:
            import ctranslate2
            if ctranslate2.get_cuda_device_count() > 0:
                return "cuda", "float16"
        except Exception:
            pass
        return "cpu", "int8"

    def _load_model(self):
        """Lazy load the Whisper model when needed."""
        if self.model is None:
            self.model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type,
            )

    def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None
    ) -> List[Dict[str, any]]:
        """
        Transcribe an audio file.

        Args:
            audio_path: Path to the audio file
            language: Language code (e.g., 'en', 'zh'). None for auto-detect.

        Returns:
            List of segments, each containing:
                - start: Start time in seconds
                - end: End time in seconds
                - text: Transcribed text

        Raises:
            FileNotFoundError: If audio file doesn't exist
            Exception: If transcription fails
        """
        import os
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        # Load model lazily
        self._load_model()

        try:
            # Transcribe using faster-whisper
            segments, info = self.model.transcribe(
                audio_path,
                language=language,
                beam_size=5,
                vad_filter=True,  # Voice activity detection to filter silence
            )

            # Convert segments to list of dictionaries
            result = []
            for segment in segments:
                result.append({
                    'start': segment.start,
                    'end': segment.end,
                    'text': segment.text.strip()
                })

            return result

        except Exception as e:
            raise Exception(f"Transcription failed: {str(e)}")

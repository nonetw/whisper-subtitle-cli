"""Ollama-based subtitle translator."""

import json
import requests
from pathlib import Path
from typing import List, Dict, Optional


def load_config() -> dict:
    """
    Load configuration from config.json file.

    Returns:
        Configuration dictionary with default values merged with file values.
    """
    config_path = Path(__file__).parent.parent / 'config.json'
    default_config = {
        "ollama": {
            "model": "qwen2.5:7b",
            "base_url": "http://localhost:11434"
        }
    }

    if config_path.exists():
        with open(config_path) as f:
            file_config = json.load(f)
            # Deep merge for ollama section
            if 'ollama' in file_config:
                default_config['ollama'].update(file_config['ollama'])
            return default_config

    return default_config


class OllamaTranslator:
    """Translator using local Ollama API for subtitle translation."""

    def __init__(self, model: str = None, base_url: str = None):
        """
        Initialize the translator with Ollama settings.

        Args:
            model: Ollama model name (e.g., 'qwen2.5:7b'). Loads from config if not provided.
            base_url: Ollama API base URL. Loads from config if not provided.
        """
        config = load_config()
        self.model = model or config['ollama']['model']
        self.base_url = base_url or config['ollama']['base_url']

    def translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Translate a single text string using Ollama.

        Args:
            text: Text to translate
            source_lang: Source language (e.g., 'English')
            target_lang: Target language (e.g., 'Chinese')

        Returns:
            Translated text

        Raises:
            ConnectionError: If Ollama API is not available
            RuntimeError: If translation fails
        """
        prompt = f"Translate the following from {source_lang} to {target_lang}. Only output the translation, nothing else:\n\n{text}"

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "").strip()
        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                f"Cannot connect to Ollama at {self.base_url}. "
                "Make sure Ollama is running (ollama serve)."
            )
        except requests.exceptions.Timeout:
            raise RuntimeError("Translation request timed out")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Translation failed: {e}")

    def translate_segments(
        self,
        segments: List[Dict],
        source_lang: str,
        target_lang: str,
        progress_callback: Optional[callable] = None
    ) -> List[Dict]:
        """
        Translate all segments, preserving timestamps.

        Args:
            segments: List of segments with 'start', 'end', 'text' keys
            source_lang: Source language (e.g., 'English')
            target_lang: Target language (e.g., 'Chinese')
            progress_callback: Optional callback function(current, total) for progress updates

        Returns:
            List of translated segments with preserved timestamps

        Raises:
            ConnectionError: If Ollama API is not available
            RuntimeError: If translation fails
        """
        translated_segments = []
        total = len(segments)

        for i, segment in enumerate(segments):
            if progress_callback:
                progress_callback(i + 1, total)

            translated_text = self.translate_text(
                segment['text'],
                source_lang,
                target_lang
            )

            translated_segments.append({
                'start': segment['start'],
                'end': segment['end'],
                'text': translated_text
            })

        return translated_segments

    def check_connection(self) -> bool:
        """
        Check if Ollama API is available.

        Returns:
            True if connection is successful, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

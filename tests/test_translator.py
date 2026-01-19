import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, Mock, MagicMock

from src.translator import OllamaTranslator, load_config


class TestLoadConfig:
    """Tests for the load_config function."""

    def test_load_config_returns_defaults_when_no_file(self):
        """Test that defaults are returned when config file doesn't exist."""
        with patch('src.translator.Path') as mock_path:
            mock_path_instance = MagicMock()
            mock_path_instance.exists.return_value = False
            mock_path.return_value.parent.parent.__truediv__.return_value = mock_path_instance

            # Re-import to use patched Path
            from src.translator import load_config as load_config_fresh

            with patch.object(Path, '__new__', return_value=mock_path_instance):
                config = load_config()

            assert 'ollama' in config
            assert config['ollama']['model'] == 'qwen2.5:7b'
            assert config['ollama']['base_url'] == 'http://localhost:11434'

    def test_load_config_merges_file_values(self):
        """Test that file values override defaults."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a temporary config file
            config_path = Path(tmpdir) / 'config.json'
            config_data = {
                "ollama": {
                    "model": "llama3:8b"
                }
            }
            config_path.write_text(json.dumps(config_data))

            with patch('src.translator.Path') as mock_path_class:
                mock_path_instance = MagicMock()
                mock_path_instance.exists.return_value = True

                # Mock __truediv__ to return our temp config path
                mock_path_class.return_value.parent.parent.__truediv__.return_value = config_path

                config = load_config()

            # Model should be from file, base_url should be default
            assert config['ollama']['model'] == 'llama3:8b'
            assert config['ollama']['base_url'] == 'http://localhost:11434'


class TestOllamaTranslator:
    """Tests for the OllamaTranslator class."""

    @pytest.fixture
    def translator(self):
        """Create a translator instance with explicit config."""
        return OllamaTranslator(model='test-model', base_url='http://localhost:11434')

    @pytest.fixture
    def sample_segments(self):
        """Sample subtitle segments for testing."""
        return [
            {'start': 0.0, 'end': 2.5, 'text': 'Hello, world!'},
            {'start': 2.5, 'end': 5.0, 'text': 'This is a test.'},
            {'start': 5.0, 'end': 8.3, 'text': 'Testing translation.'},
        ]

    def test_translator_initialization_with_explicit_values(self):
        """Test translator initializes with explicit model and base_url."""
        translator = OllamaTranslator(
            model='custom-model',
            base_url='http://custom:8080'
        )
        assert translator.model == 'custom-model'
        assert translator.base_url == 'http://custom:8080'

    def test_translator_initialization_uses_config_defaults(self):
        """Test translator uses config values when not provided."""
        with patch('src.translator.load_config') as mock_config:
            mock_config.return_value = {
                'ollama': {
                    'model': 'default-model',
                    'base_url': 'http://default:11434'
                }
            }
            translator = OllamaTranslator()
            assert translator.model == 'default-model'
            assert translator.base_url == 'http://default:11434'

    def test_translate_text_success(self, translator):
        """Test successful text translation."""
        mock_response = Mock()
        mock_response.json.return_value = {'response': '你好，世界！'}
        mock_response.raise_for_status = Mock()

        with patch('src.translator.requests.post', return_value=mock_response):
            result = translator.translate_text(
                'Hello, world!',
                'English',
                'Chinese'
            )

        assert result == '你好，世界！'

    def test_translate_text_strips_whitespace(self, translator):
        """Test that translated text is stripped of whitespace."""
        mock_response = Mock()
        mock_response.json.return_value = {'response': '  你好，世界！  \n'}
        mock_response.raise_for_status = Mock()

        with patch('src.translator.requests.post', return_value=mock_response):
            result = translator.translate_text(
                'Hello, world!',
                'English',
                'Chinese'
            )

        assert result == '你好，世界！'

    def test_translate_text_connection_error(self, translator):
        """Test handling of connection errors."""
        import requests as req

        with patch('src.translator.requests.post') as mock_post:
            mock_post.side_effect = req.exceptions.ConnectionError()

            with pytest.raises(ConnectionError) as exc_info:
                translator.translate_text('Hello', 'English', 'Chinese')

            assert 'Cannot connect to Ollama' in str(exc_info.value)

    def test_translate_text_timeout_error(self, translator):
        """Test handling of timeout errors."""
        import requests as req

        with patch('src.translator.requests.post') as mock_post:
            mock_post.side_effect = req.exceptions.Timeout()

            with pytest.raises(RuntimeError) as exc_info:
                translator.translate_text('Hello', 'English', 'Chinese')

            assert 'timed out' in str(exc_info.value)

    def test_translate_segments_preserves_timestamps(self, translator, sample_segments):
        """Test that translation preserves timestamps."""
        translations = ['你好，世界！', '这是一个测试。', '测试翻译。']

        with patch.object(translator, 'translate_text') as mock_translate:
            mock_translate.side_effect = translations
            result = translator.translate_segments(
                sample_segments,
                'English',
                'Chinese'
            )

        # Check timestamps are preserved
        assert result[0]['start'] == 0.0
        assert result[0]['end'] == 2.5
        assert result[1]['start'] == 2.5
        assert result[1]['end'] == 5.0
        assert result[2]['start'] == 5.0
        assert result[2]['end'] == 8.3

    def test_translate_segments_translates_all_texts(self, translator, sample_segments):
        """Test that all segments are translated."""
        translations = ['Translation 1', 'Translation 2', 'Translation 3']

        with patch.object(translator, 'translate_text') as mock_translate:
            mock_translate.side_effect = translations
            result = translator.translate_segments(
                sample_segments,
                'English',
                'Chinese'
            )

        assert result[0]['text'] == 'Translation 1'
        assert result[1]['text'] == 'Translation 2'
        assert result[2]['text'] == 'Translation 3'

    def test_translate_segments_calls_progress_callback(self, translator, sample_segments):
        """Test that progress callback is called correctly."""
        progress_calls = []

        def progress_callback(current, total):
            progress_calls.append((current, total))

        with patch.object(translator, 'translate_text', return_value='translated'):
            translator.translate_segments(
                sample_segments,
                'English',
                'Chinese',
                progress_callback=progress_callback
            )

        assert progress_calls == [(1, 3), (2, 3), (3, 3)]

    def test_translate_segments_empty_list(self, translator):
        """Test translating empty segment list."""
        result = translator.translate_segments([], 'English', 'Chinese')
        assert result == []

    def test_check_connection_success(self, translator):
        """Test successful connection check."""
        mock_response = Mock()
        mock_response.status_code = 200

        with patch('src.translator.requests.get', return_value=mock_response):
            result = translator.check_connection()

        assert result is True

    def test_check_connection_failure(self, translator):
        """Test failed connection check."""
        import requests as req

        with patch('src.translator.requests.get') as mock_get:
            mock_get.side_effect = req.exceptions.ConnectionError()
            result = translator.check_connection()

        assert result is False

    def test_check_connection_non_200_status(self, translator):
        """Test connection check with non-200 status."""
        mock_response = Mock()
        mock_response.status_code = 500

        with patch('src.translator.requests.get', return_value=mock_response):
            result = translator.check_connection()

        assert result is False

    def test_translate_text_sends_correct_prompt(self, translator):
        """Test that the correct prompt is sent to Ollama."""
        mock_response = Mock()
        mock_response.json.return_value = {'response': 'translated'}
        mock_response.raise_for_status = Mock()

        with patch('src.translator.requests.post', return_value=mock_response) as mock_post:
            translator.translate_text('Hello', 'English', 'Spanish')

            # Verify the call
            call_args = mock_post.call_args
            assert call_args[0][0] == 'http://localhost:11434/api/generate'

            json_data = call_args[1]['json']
            assert json_data['model'] == 'test-model'
            assert 'English' in json_data['prompt']
            assert 'Spanish' in json_data['prompt']
            assert 'Hello' in json_data['prompt']
            assert json_data['stream'] is False

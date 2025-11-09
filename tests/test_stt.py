import pytest
from unittest.mock import patch, MagicMock

# Adiciona o diretório raiz ao path para permitir a importação de stt
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from stt import STT
import speech_recognition as sr

@pytest.fixture
def mock_recognizer():
    """Fixture para mockar o Recognizer e o Microphone."""
    with patch('speech_recognition.Recognizer') as MockRecognizer,
         patch('speech_recognition.Microphone') as MockMicrophone:
        
        mock_recognizer_instance = MockRecognizer.return_value
        mock_microphone_instance = MockMicrophone.return_value.__enter__.return_value
        
        yield mock_recognizer_instance, mock_microphone_instance

def test_stt_listen_success(mock_recognizer):
    """Testa o reconhecimento de fala bem-sucedido."""
    mock_recognizer_instance, mock_microphone_instance = mock_recognizer
    mock_recognizer_instance.recognize_google.return_value = "Olá Jarvis"

    stt = STT()
    result = stt.listen()

    mock_recognizer_instance.listen.assert_called_once_with(mock_microphone_instance)
    mock_recognizer_instance.recognize_google.assert_called_once()
    assert result == "Olá Jarvis"

def test_stt_listen_unknown_value_error(mock_recognizer):
    """Testa o tratamento de UnknownValueError."""
    mock_recognizer_instance, _ = mock_recognizer
    mock_recognizer_instance.recognize_google.side_effect = sr.UnknownValueError

    stt = STT()
    result = stt.listen()

    assert result == "Não entendi o que você disse."

def test_stt_listen_request_error(mock_recognizer):
    """Testa o tratamento de RequestError."""
    mock_recognizer_instance, _ = mock_recognizer
    mock_recognizer_instance.recognize_google.side_effect = sr.RequestError("API indisponível")

    stt = STT()
    result = stt.listen()

    assert "Erro no serviço de reconhecimento de fala" in result
    assert "API indisponível" in result

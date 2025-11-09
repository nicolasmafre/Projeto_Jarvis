import pytest
import os
from unittest.mock import patch, MagicMock

# Adiciona o diretório raiz ao path para permitir a importação de tts
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tts import TTS

# --- Testes para o motor pyttsx3 ---

@patch.dict(os.environ, {"TTS_ENGINE": "pyttsx3"})
@patch('pyttsx3.init')
def test_tts_pyttsx3_engine(mock_pyttsx3_init):
    """Testa se o motor pyttsx3 é inicializado e usado corretamente."""
    mock_engine = MagicMock()
    mock_pyttsx3_init.return_value = mock_engine

    tts = TTS()
    tts.speak("Olá mundo")

    mock_pyttsx3_init.assert_called_once()
    mock_engine.say.assert_called_once_with("Olá mundo")
    mock_engine.runAndWait.assert_called_once()

# --- Testes para o motor eSpeak-ng ---

@patch.dict(os.environ, {"TTS_ENGINE": "espeak-ng"})
@patch('subprocess.run')
def test_tts_espeak_ng_engine(mock_subprocess_run):
    """Testa se o motor eSpeak-ng é chamado corretamente."""
    # Simula que o espeak-ng está instalado
    mock_subprocess_run.return_value = MagicMock(check=True)

    tts = TTS()
    tts.speak("Teste com eSpeak")

    # Verifica se o comando correto foi executado
    expected_command = ["espeak-ng", "-v", "pt-br", "-s", "150", "Teste com eSpeak"]
    
    # A primeira chamada é a verificação de instalação, a segunda é o speak
    assert mock_subprocess_run.call_count >= 2
    # Pega a última chamada feita ao subprocess.run
    last_call_args = mock_subprocess_run.call_args.args[0]
    assert last_call_args == expected_command

@patch.dict(os.environ, {"TTS_ENGINE": "espeak-ng"})
@patch('subprocess.run', side_effect=FileNotFoundError)
@patch('pyttsx3.init') # Mock pyttsx3 para o fallback
def test_tts_espeak_ng_not_found_fallback(mock_pyttsx3_init, mock_subprocess_run):
    """Testa o fallback para pyttsx3 quando eSpeak-ng não é encontrado."""
    mock_engine = MagicMock()
    mock_pyttsx3_init.return_value = mock_engine

    tts = TTS()
    assert tts.engine_type == "pyttsx3" # Verifica se o fallback ocorreu

    tts.speak("Testando fallback")
    mock_engine.say.assert_called_once_with("Testando fallback")
    mock_engine.runAndWait.assert_called_once()

@patch.dict(os.environ, {}, clear=True) # Garante que TTS_ENGINE não está definido
@patch('pyttsx3.init')
def test_tts_default_engine_is_pyttsx3(mock_pyttsx3_init):
    """Testa se o motor padrão é pyttsx3 quando a variável de ambiente não está definida."""
    tts = TTS()
    assert tts.engine_type == "pyttsx3"
    mock_pyttsx3_init.assert_called_once()

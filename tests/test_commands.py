import pytest
import os
from unittest.mock import patch

# Adiciona o diretório raiz ao path para permitir a importação de commands
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from commands import CommandHandler

@pytest.fixture
def command_handler_safe_mode():
    """Fixture para o CommandHandler com SAFE_MODE=True."""
    with patch.dict(os.environ, {"SAFE_MODE": "True"}):
        return CommandHandler()

@pytest.fixture
def command_handler_unsafe_mode():
    """Fixture para o CommandHandler com SAFE_MODE=False."""
    with patch.dict(os.environ, {"SAFE_MODE": "False"}):
        return CommandHandler()

# --- Testes em Modo Seguro ---

@patch('builtins.input', return_value='s') # Simula o usuário digitando 's'
@patch('os.listdir', return_value=['arquivo1.txt', 'arquivo2.log'])
def test_handle_list_files_safe_mode_confirm(mock_listdir, mock_input, command_handler_safe_mode):
    """Testa o comando 'liste os arquivos' em modo seguro com confirmação."""
    response = command_handler_safe_mode.handle("Jarvis, por favor, liste os arquivos em /tmp")
    mock_input.assert_called_once()
    assert response == "arquivo1.txt\narquivo2.log"

@patch('builtins.input', return_value='n') # Simula o usuário digitando 'n'
@patch('os.listdir')
def test_handle_list_files_safe_mode_cancel(mock_listdir, mock_input, command_handler_safe_mode):
    """Testa o comando 'liste os arquivos' em modo seguro com cancelamento."""
    response = command_handler_safe_mode.handle("Jarvis, liste os arquivos em /tmp")
    mock_input.assert_called_once()
    mock_listdir.assert_not_called() # Garante que os.listdir não foi chamado
    assert response == "Ação cancelada."

# --- Testes em Modo Inseguro ---

@patch('builtins.input')
@patch('os.listdir', return_value=['doc.pdf'])
def test_handle_list_files_unsafe_mode(mock_listdir, mock_input, command_handler_unsafe_mode):
    """Testa o comando 'liste os arquivos' em modo inseguro."""
    response = command_handler_unsafe_mode.handle("liste os arquivos em /docs")
    mock_input.assert_not_called() # Garante que o input não foi solicitado
    mock_listdir.assert_called_once_with("/docs")
    assert response == "doc.pdf"

# --- Testes Gerais ---

@patch('os.listdir', side_effect=FileNotFoundError)
def test_handle_list_files_directory_not_found(mock_listdir, command_handler_unsafe_mode):
    """Testa o comando para um diretório que não existe."""
    response = command_handler_unsafe_mode.handle("liste os arquivos em /diretorio_inexistente")
    assert "Diretório não encontrado" in response

def test_handle_no_command(command_handler_safe_mode):
    """Testa uma resposta que não contém um comando válido."""
    response = command_handler_safe_mode.handle("Olá, tudo bem? Esta é uma resposta normal.")
    assert response is None

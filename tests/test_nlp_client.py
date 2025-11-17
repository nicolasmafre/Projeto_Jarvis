import pytest
import os
from unittest.mock import patch, MagicMock

# Adiciona o diretório raiz ao path
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nlp_client import HuggingFaceHubClient, NlpClient

# --- Testes para HuggingFaceHubClient ---

@patch.dict(os.environ, {"HF_TOKEN": "fake_hf_token"})
@patch('nlp_client.InferenceClient')
def test_huggingface_generate_success(mock_inference_client):
    """Testa a geração de texto bem-sucedida do HuggingFaceHubClient."""
    # Configura o mock para simular a resposta da API
    mock_response_chunk = MagicMock()
    mock_response_chunk.choices = [MagicMock()]
    mock_response_chunk.choices[0].delta.content = "Olá"
    mock_inference_client.return_value.chat.completions.create.return_value = [mock_response_chunk]

    client = HuggingFaceHubClient()
    response = client.generate("Oi")
    
    assert response == "Olá"
    mock_inference_client.return_value.chat.completions.create.assert_called_once()

@patch.dict(os.environ, {"HF_TOKEN": "fake_hf_token"})
@patch('nlp_client.InferenceClient')
def test_huggingface_generate_error(mock_inference_client):
    """Testa o tratamento de erro do HuggingFaceHubClient."""
    # Configura o mock para simular um erro na API
    mock_inference_client.return_value.chat.completions.create.side_effect = Exception("API Error")

    client = HuggingFaceHubClient()
    response = client.generate("Oi")

    # Verifica se a mensagem de erro amigável é retornada
    assert "Desculpe, ocorreu um erro" in response
    assert "API Error" in response

def test_huggingface_init_no_token():
    """Testa a inicialização sem token do HuggingFaceHubClient."""
    with patch.dict(os.environ, {"HF_TOKEN": ""}):
        with pytest.raises(ValueError, match="A chave de API do Hugging Face não foi encontrada."):
            HuggingFaceHubClient()

# --- Testes para a fábrica NlpClient.create ---

@patch.dict(os.environ, {"NLP_PROVIDER": "huggingface", "HF_TOKEN": "fake_token"})
def test_create_huggingface_client():
    """Testa se a fábrica cria o cliente HuggingFace corretamente."""
    client = NlpClient.create()
    assert isinstance(client, HuggingFaceHubClient)

@patch.dict(os.environ, {"NLP_PROVIDER": "invalid_provider"})
def test_create_unknown_provider():
    """Testa se a fábrica levanta um erro para um provedor desconhecido."""
    with pytest.raises(ValueError, match="Provedor de NLP desconhecido: invalid_provider"):
        NlpClient.create()

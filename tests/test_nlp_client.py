import pytest
import os
from unittest.mock import patch, MagicMock

# Adiciona o diretório raiz ao path para permitir a importação do nlp_client
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nlp_client import HuggingFaceHubClient, ReplicateClient

# --- Testes para HuggingFaceHubClient ---

@patch.dict(os.environ, {"HF_TOKEN": "fake_hf_token"})
@patch('nlp_client.InferenceClient')
def test_huggingface_generate_success(mock_inference_client):
    """Testa a geração de texto bem-sucedida do HuggingFaceHubClient."""
    # Configura o mock para simular a resposta do stream
    mock_chunk1 = MagicMock()
    mock_chunk1.choices = [MagicMock(delta=MagicMock(content="Olá"))]
    mock_chunk2 = MagicMock()
    mock_chunk2.choices = [MagicMock(delta=MagicMock(content=" mundo!"))]
    mock_chunk_end = MagicMock()
    mock_chunk_end.choices = [] # Simula um chunk vazio ou de controle

    mock_inference_client.return_value.chat.completions.create.return_value = [
        mock_chunk1, mock_chunk2, mock_chunk_end
    ]

    client = HuggingFaceHubClient()
    response = client.generate("Oi")

    assert response == "Olá mundo!"
    mock_inference_client.return_value.chat.completions.create.assert_called_once()

@patch.dict(os.environ, {"HF_TOKEN": "fake_hf_token"})
@patch('nlp_client.InferenceClient')
def test_huggingface_generate_error(mock_inference_client):
    """Testa o tratamento de erro do HuggingFaceHubClient."""
    mock_inference_client.return_value.chat.completions.create.side_effect = Exception("API Error")

    client = HuggingFaceHubClient()
    response = client.generate("Oi")

    assert "ocorreu um erro" in response

@patch.dict(os.environ, {"HF_TOKEN": ""}) # Simula token ausente
def test_huggingface_init_no_token():
    """Testa a inicialização sem token do HuggingFaceHubClient."""
    with pytest.raises(ValueError, match="chave de API do Hugging Face não foi encontrada"):
        HuggingFaceHubClient()

# --- Testes para ReplicateClient ---

@patch.dict(os.environ, {"REPLICATE_API_KEY": "fake_replicate_token"})
@patch('requests.post')
@patch('requests.get')
def test_replicate_generate_success(mock_requests_get, mock_requests_post):
    """Testa a geração de texto bem-sucedida do ReplicateClient."""
    # Mock para a primeira chamada POST (criação da predição)
    mock_post_response = MagicMock()
    mock_post_response.status_code = 201
    mock_post_response.json.return_value = {"urls": {"get": "http://fake.replicate.com/prediction"}}
    mock_requests_post.return_value = mock_post_response

    # Mock para as chamadas GET (verificação do status da predição)
    mock_get_response_pending = MagicMock()
    mock_get_response_pending.json.return_value = {"status": "processing"}
    
    mock_get_response_succeeded = MagicMock()
    mock_get_response_succeeded.json.return_value = {"status": "succeeded", "output": ["Resposta do Replicate"]}

    mock_requests_get.side_effect = [mock_get_response_pending, mock_get_response_succeeded]

    client = ReplicateClient()
    response = client.generate("Oi")

    assert response == "Resposta do Replicate"
    mock_requests_post.assert_called_once()
    assert mock_requests_get.call_count == 2

@patch.dict(os.environ, {"REPLICATE_API_KEY": "fake_replicate_token"})
@patch('requests.post')
@patch('requests.get')
def test_replicate_generate_failure(mock_requests_get, mock_requests_post):
    """Testa o tratamento de falha da geração do ReplicateClient."""
    mock_post_response = MagicMock()
    mock_post_response.status_code = 201
    mock_post_response.json.return_value = {"urls": {"get": "http://fake.replicate.com/prediction"}}
    mock_requests_post.return_value = mock_post_response

    mock_get_response_failed = MagicMock()
    mock_get_response_failed.json.return_value = {"status": "failed"}

    mock_requests_get.return_value = mock_get_response_failed

    client = ReplicateClient()
    response = client.generate("Oi")

    assert "geração da resposta falhou" in response

@patch.dict(os.environ, {"REPLICATE_API_KEY": "fake_replicate_token"})
@patch('requests.post')
def test_replicate_rate_limit(mock_requests_post):
    """Testa o retry com rate limit do ReplicateClient."""
    mock_response_429 = MagicMock()
    mock_response_429.status_code = 429 # Rate Limit
    mock_response_201 = MagicMock()
    mock_response_201.status_code = 201
    mock_response_201.json.return_value = {"urls": {"get": "http://fake.replicate.com/prediction"}}

    mock_requests_post.side_effect = [mock_response_429, mock_response_201]

    # Mock para a chamada GET subsequente
    mock_requests_get = MagicMock()
    mock_requests_get.return_value.json.return_value = {"status": "succeeded", "output": ["Retry bem-sucedido"]}
    
    with patch('requests.get', mock_requests_get):
        client = ReplicateClient()
        response = client.generate("Oi")

    assert response == "Retry bem-sucedido"
    assert mock_requests_post.call_count == 2

@patch.dict(os.environ, {"REPLICATE_API_KEY": ""}) # Simula token ausente
def test_replicate_init_no_token():
    """Testa a inicialização sem token do ReplicateClient."""
    # ReplicateClient não levanta erro na inicialização se a chave estiver ausente,
    # mas falhará na chamada generate.
    client = ReplicateClient()
    assert client.api_key == ""

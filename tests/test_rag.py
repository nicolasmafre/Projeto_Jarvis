import pytest
from unittest.mock import patch, MagicMock
import torch

# Adiciona o diretório raiz ao path
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from rag import Rag

# Mock dos dados que seriam lidos dos arquivos
MOCK_DOCUMENTS = [
    "O escudo do Capitão América é feito de Vibranium.",
    "O telefone da Polícia Militar é 190.",
    "O Homem de Ferro usa um Reator Arc."
]

@pytest.fixture
def mock_sentence_transformer():
    """Fixture para mockar o SentenceTransformer."""
    with patch('rag.SentenceTransformer') as MockTransformer:
        mock_model = MockTransformer.return_value
        
        # Simula o comportamento do método encode
        def mock_encode(texts, convert_to_tensor=False):
            # Retorna tensores falsos com a forma correta
            if isinstance(texts, str): # Se for uma única string (a pergunta)
                return torch.randn(1, 384)
            # Se for uma lista de strings (os documentos)
            return torch.randn(len(texts), 384)
            
        mock_model.encode.side_effect = mock_encode
        yield mock_model

@pytest.fixture
def mock_rag_instance(mock_sentence_transformer):
    """Fixture que cria uma instância do RAG com mocks."""
    # Mock para os.listdir e open para simular a leitura dos documentos
    with patch('os.listdir', return_value=['doc1.md', 'doc2.md', 'doc3.md']):
        with patch('builtins.open', MagicMock()) as mock_open:
            # Simula a leitura sequencial dos documentos
            mock_open.side_effect = [
                MagicMock(__enter__=MagicMock(return_value=MagicMock(read=MagicMock(return_value=doc))))
                for doc in MOCK_DOCUMENTS
            ]
            rag_instance = Rag(knowledge_dir="fake_dir")
            # Força os documentos a serem os mocks para consistência
            rag_instance.documents = MOCK_DOCUMENTS
            # Força a re-indexação com os documentos mockados
            rag_instance.doc_embeddings = rag_instance.model.encode(rag_instance.documents, convert_to_tensor=True)
            yield rag_instance

def test_rag_index_documents(mock_rag_instance):
    """Verifica se os documentos são indexados corretamente."""
    assert len(mock_rag_instance.documents) == 3
    assert mock_rag_instance.doc_embeddings is not None
    assert mock_rag_instance.doc_embeddings.shape[0] == 3

def test_rag_answer_with_relevant_question(mock_rag_instance):
    """Verifica se o RAG responde a perguntas relevantes."""
    # Mock da similaridade de cosseno para forçar um resultado
    with patch('rag.util.cos_sim', return_value=torch.tensor([[0.9, 0.2, 0.1]])):
        question = "De que é feito o escudo do Capitão?"
        answer = mock_rag_instance.answer_with_rag(question, similarity_threshold=0.8)
        assert answer is not None
        assert "Vibranium" in answer

def test_rag_answer_with_another_relevant_question(mock_rag_instance):
    """Verifica se o RAG responde a outra pergunta relevante."""
    with patch('rag.util.cos_sim', return_value=torch.tensor([[0.1, 0.95, 0.3]])):
        question = "Qual o telefone da PM?"
        answer = mock_rag_instance.answer_with_rag(question, similarity_threshold=0.8)
        assert answer is not None
        assert "190" in answer

def test_rag_answer_with_irrelevant_question(mock_rag_instance):
    """Verifica se o RAG retorna None para perguntas irrelevantes."""
    with patch('rag.util.cos_sim', return_value=torch.tensor([[0.1, 0.2, 0.3]])):
        question = "Qual a cor do céu?"
        answer = mock_rag_instance.answer_with_rag(question, similarity_threshold=0.8)
        assert answer is None

def test_rag_empty_knowledge_base():
    """Verifica o comportamento com uma base de conhecimento vazia."""
    with patch('os.listdir', return_value=[]):
        with patch('rag.SentenceTransformer'): # Mock para não carregar o modelo
            rag = Rag(knowledge_dir="empty_dir")
            assert len(rag.documents) == 0
            assert rag.doc_embeddings is None
            answer = rag.answer_with_rag("Qualquer pergunta")
            assert answer is None

import pytest
import os
from unittest.mock import patch, mock_open

# Adiciona o diretório raiz ao path para permitir a importação do rag
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from rag import Rag

# Conteúdo simulado para os arquivos de conhecimento
MOCK_KNOWLEDGE_FILES = {
    "knowledge/doc1.md": "O Capitão América usa um escudo feito de Vibranium.",
    "knowledge/doc2.txt": "O número de emergência da Polícia Militar no Brasil é 190.",
    "knowledge/outro.txt": "Este é um documento irrelevante."
}

@pytest.fixture
def mock_rag_instance():
    """Fixture para uma instância de Rag com documentos mockados."""
    with patch('os.listdir', return_value=MOCK_KNOWLEDGE_FILES.keys()):
        with patch('builtins.open', new_callable=mock_open) as mock_file_open:
            # Configura mock_open para retornar o conteúdo correto para cada arquivo
            def mock_read_data(filename, mode='r'):
                if filename in MOCK_KNOWLEDGE_FILES:
                    mock_file_open.return_value.__enter__.return_value.read.return_value = MOCK_KNOWLEDGE_FILES[filename]
                return mock_file_open.return_value
            mock_file_open.side_effect = mock_read_data
            
            rag = Rag(knowledge_dir="knowledge")
            yield rag

def test_rag_index_documents(mock_rag_instance):
    """Verifica se os documentos são indexados corretamente."""
    assert len(mock_rag_instance.documents) == 3
    assert "Vibranium" in mock_rag_instance.documents[0]
    assert mock_rag_instance.tfidf_matrix is not None

def test_rag_answer_with_relevant_question(mock_rag_instance):
    """Verifica se o RAG responde a perguntas relevantes."""
    question = "De que é feito o escudo do Capitão?"
    answer = mock_rag_instance.answer_with_rag(question)
    assert "Vibranium" in answer

def test_rag_answer_with_another_relevant_question(mock_rag_instance):
    """Verifica se o RAG responde a outra pergunta relevante."""
    question = "Qual o telefone da PM?"
    answer = mock_rag_instance.answer_with_rag(question)
    assert "190" in answer

def test_rag_answer_with_irrelevant_question(mock_rag_instance):
    """Verifica se o RAG retorna None para perguntas irrelevantes."""
    question = "Qual a capital da França?"
    answer = mock_rag_instance.answer_with_rag(question)
    assert answer is None

def test_rag_empty_knowledge_base():
    """Verifica o comportamento com uma base de conhecimento vazia."""
    with patch('os.listdir', return_value=[]):
        rag = Rag(knowledge_dir="knowledge")
        assert len(rag.documents) == 0
        assert rag.tfidf_matrix is None
        assert rag.answer_with_rag("qualquer coisa") is None

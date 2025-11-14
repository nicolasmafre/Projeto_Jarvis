"""
Módulo de Retrieval-Augmented Generation (RAG).

Este módulo é responsável por indexar uma base de conhecimento local
(documentos de texto) e recuperar informações relevantes para responder
a perguntas dos usuários, usando busca por similaridade semântica.
"""

import os
import torch
from sentence_transformers import SentenceTransformer, util

class Rag:
    """
    Gerencia a indexação e a busca em uma base de conhecimento local.
    """
    def __init__(self, knowledge_dir="knowledge", model_name='all-MiniLM-L6-v2'):
        """
        Inicializa o sistema RAG.
        """
        self.knowledge_dir = knowledge_dir
        self.documents = []
        self.doc_embeddings = None
        
        print("[RAG] Carregando o modelo de embedding...")
        try:
            self.model = SentenceTransformer(model_name)
            self._index_documents()
        except Exception as e:
            print(f"ERRO [RAG]: Falha ao carregar o modelo SentenceTransformer: {e}")
            self.model = None

    def _index_documents(self):
        """Lê os documentos da pasta 'knowledge' e gera os embeddings."""
        if not self.model:
            print("[RAG] Modelo não carregado. A indexação foi pulada.")
            return

        doc_texts = []
        for filename in os.listdir(self.knowledge_dir):
            if filename.endswith(('.txt', '.md')):
                filepath = os.path.join(self.knowledge_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        doc_texts.append(f.read())
                except Exception as e:
                    print(f"ERRO [RAG]: Falha ao ler o arquivo {filepath}: {e}")

        if doc_texts:
            self.documents = doc_texts
            self.doc_embeddings = self.model.encode(self.documents, convert_to_tensor=True)
            print(f"[RAG] {len(self.documents)} documentos indexados com sucesso.")
        else:
            print("[RAG] Nenhum documento encontrado na pasta 'knowledge'.")

    def answer_with_rag(self, question, similarity_threshold=0.7):
        """
        Encontra o documento mais relevante para uma pergunta.

        Args:
            question (str): A pergunta do usuário.
            similarity_threshold (float): O limiar de similaridade de cosseno.
                                          Aumentado para 0.7 para evitar falsos positivos.

        Returns:
            str | None: O texto do documento mais relevante, ou None.
        """
        if self.doc_embeddings is None or not self.documents:
            return None

        question_embedding = self.model.encode(question, convert_to_tensor=True)
        cos_scores = util.cos_sim(question_embedding, self.doc_embeddings)[0]
        
        best_match_index = torch.argmax(cos_scores).item()
        best_match_score = cos_scores[best_match_index].item()

        if best_match_score > similarity_threshold:
            print(f"[RAG] Encontrado documento relevante com similaridade: {best_match_score:.2f}")
            return self.documents[best_match_index]
        else:
            print(f"[RAG] Nenhum documento relevante encontrado (maior similaridade: {best_match_score:.2f})")
            return None

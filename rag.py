import os
from sentence_transformers import SentenceTransformer, util
import torch

class Rag:
    def __init__(self, knowledge_dir="knowledge", model_name='all-MiniLM-L6-v2'):
        self.knowledge_dir = knowledge_dir
        self.documents = []
        self.doc_embeddings = None
        
        print("[RAG] Carregando o modelo de embedding... (Isso pode levar um momento na primeira vez)")
        try:
            self.model = SentenceTransformer(model_name)
            self._index_documents()
        except Exception as e:
            print(f"ERRO [RAG]: Falha ao carregar o modelo SentenceTransformer: {e}")
            print("Execute 'pip install -r requirements.txt' ou 'conda env update -f environment.yml --prune' para instalar as dependências.")
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
            # Gera os embeddings para todos os documentos
            # O modelo pode ser executado na GPU se disponível
            self.doc_embeddings = self.model.encode(self.documents, convert_to_tensor=True)
            print(f"[RAG] {len(self.documents)} documentos indexados com sucesso usando SentenceTransformer.")
        else:
            print("[RAG] Nenhum documento encontrado na pasta 'knowledge'.")

    def answer_with_rag(self, question, similarity_threshold=0.5):
        """
        Encontra o documento mais relevante usando busca por similaridade semântica.
        """
        if self.doc_embeddings is None or not self.documents:
            return None

        # Gera o embedding para a pergunta
        question_embedding = self.model.encode(question, convert_to_tensor=True)

        # Calcula a similaridade de cosseno entre a pergunta e todos os documentos
        # A função 'util.cos_sim' é otimizada para tensores do PyTorch
        cos_scores = util.cos_sim(question_embedding, self.doc_embeddings)[0]
        
        # Encontra o documento com a maior pontuação
        best_match_index = torch.argmax(cos_scores).item()
        best_match_score = cos_scores[best_match_index].item()

        # Retorna o documento apenas se a similaridade for acima do limiar
        if best_match_score > similarity_threshold:
            print(f"[RAG] Encontrado documento relevante com similaridade: {best_match_score:.2f}")
            return self.documents[best_match_index]
        else:
            print(f"[RAG] Nenhum documento relevante encontrado (maior similaridade: {best_match_score:.2f})")
            return None

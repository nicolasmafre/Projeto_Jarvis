import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class Rag:
    def __init__(self, knowledge_dir="knowledge"):
        self.knowledge_dir = knowledge_dir
        self.documents = []
        self.vectorizer = TfidfVectorizer()
        self.tfidf_matrix = None
        self._index_documents()

    def _index_documents(self):
        for filename in os.listdir(self.knowledge_dir):
            if filename.endswith(('.txt', '.md')):
                with open(os.path.join(self.knowledge_dir, filename), 'r') as f:
                    self.documents.append(f.read())
        if self.documents:
            self.tfidf_matrix = self.vectorizer.fit_transform(self.documents)

    def answer_with_rag(self, question):
        if not self.documents:
            return None

        question_vec = self.vectorizer.transform([question])
        similarities = cosine_similarity(question_vec, self.tfidf_matrix).flatten()
        most_similar_doc_index = similarities.argmax()

        if similarities[most_similar_doc_index] > 0.5:  # Limiar de similaridade
            return self.documents[most_similar_doc_index]
        else:
            return None

import json
import os

class LongTermMemory:
    def __init__(self, memory_file="memory.json", memory_dir="memory"):
        self.memory_dir = memory_dir
        os.makedirs(self.memory_dir, exist_ok=True)
        self.memory_file = os.path.join(self.memory_dir, memory_file)
        self.facts = self._load_memory()

    def _load_memory(self):
        if os.path.exists(self.memory_file):
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def _save_memory(self):
        with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.facts, f, indent=2, ensure_ascii=False)

    def add_fact(self, fact):
        if fact and fact not in self.facts:
            self.facts.append(fact)
            self._save_memory()
            return True
        return False

    def get_relevant_facts(self, query, top_n=3):
        """
        Recupera fatos relevantes da memória de longo prazo.
        Para uma implementação simples, faz uma busca por palavras-chave.
        Em uma versão mais avançada, usaria embeddings e busca vetorial.
        """
        relevant_snippets = []
        query_words = set(query.lower().split())

        for fact in self.facts:
            fact_lower = fact.lower()
            # Contagem de palavras-chave em comum
            common_words = len(query_words.intersection(set(fact_lower.split())))
            if common_words > 0: # Se houver alguma palavra em comum
                relevant_snippets.append((common_words, fact))
        
        # Ordena por número de palavras em comum e pega os top_n
        relevant_snippets.sort(key=lambda x: x[0], reverse=True)
        return [fact for count, fact in relevant_snippets[:top_n]]

    def clear_memory(self):
        self.facts = []
        self._save_memory()

    def get_all_facts(self):
        return self.facts

"""
Módulo para gerenciar a memória de longo prazo do assistente.
"""

import json
import os

class LongTermMemory:
    """
    Gerencia o armazenamento e a recuperação de fatos em um arquivo JSON.
    """
    def __init__(self, memory_file="memory.json", memory_dir="memory"):
        """
        Inicializa a memória, carregando fatos de um arquivo existente.
        """
        self.memory_dir = memory_dir
        os.makedirs(self.memory_dir, exist_ok=True)
        self.memory_file = os.path.join(self.memory_dir, memory_file)
        self.facts = self._load_memory()
        print(f"[Memória] Inicializada. {len(self.facts)} fatos carregados de '{self.memory_file}'.")

    def _load_memory(self):
        """Carrega os fatos do arquivo JSON para a memória."""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    facts = json.load(f)
                    print(f"[Memória] Arquivo '{self.memory_file}' encontrado e lido.")
                    return facts
            except (json.JSONDecodeError, IOError):
                print(f"Aviso: Arquivo de memória '{self.memory_file}' corrompido ou ilegível. Começando com memória vazia.")
                return []
        print(f"[Memória] Arquivo '{self.memory_file}' não encontrado. Começando com memória vazia.")
        return []

    def _save_memory(self):
        """Salva os fatos atuais da memória no arquivo JSON."""
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.facts, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"ERRO: Não foi possível salvar no arquivo de memória: {e}")

    def add_fact(self, fact):
        """
        Adiciona um novo fato à memória, se ele ainda não existir.
        """
        if fact and isinstance(fact, str) and fact not in self.facts:
            self.facts.append(fact)
            self._save_memory()
            return True
        return False

    def get_relevant_facts(self, query, top_n=3):
        """
        Recupera os fatos mais relevantes para uma dada consulta.
        """
        if not self.facts:
            return []
            
        query_words = set(query.lower().split())
        relevant_snippets = []

        for fact in self.facts:
            fact_lower = fact.lower()
            common_words = len(query_words.intersection(set(fact_lower.split())))
            if common_words > 0:
                relevant_snippets.append((common_words, fact))
        
        relevant_snippets.sort(key=lambda x: x[0], reverse=True)
        return [fact for count, fact in relevant_snippets[:top_n]]

    def clear_memory(self):
        """Apaga todos os fatos da memória."""
        self.facts = []
        self._save_memory()

    def get_all_facts(self):
        """Retorna uma lista de todos os fatos armazenados."""
        return self.facts

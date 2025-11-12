"""
Módulo central que define a classe principal do assistente Jarvis.
"""

import os
from dotenv import load_dotenv
from nlp_client import NlpClient
from rag import Rag
from commands import CommandHandler
from memory import LongTermMemory
from sentiment import SentimentAnalyzer
from web_search import search_web

load_dotenv()

class Jarvis:
    """
    A classe principal do assistente Jarvis.
    """
    def __init__(self):
        """Inicializa todos os componentes do assistente."""
        self.nlp_client = NlpClient.create()
        self.rag = Rag()
        self.command_handler = CommandHandler()
        self.conversation_history = []
        self.memory = LongTermMemory()
        self.sentiment_analyzer = SentimentAnalyzer()
        print("[Jarvis] Assistente inicializado e pronto.")

    def _learn_from_interaction(self, user_prompt):
        """
        Extrai e armazena fatos do prompt do usuário na memória de longo prazo.
        """
        fact = self.nlp_client.extract_facts(user_prompt)
        if fact:
            if self.memory.add_fact(fact):
                print(f"[Memória]: Novo fato aprendido e salvo: {fact}")

    def interact(self, prompt: str) -> str:
        """
        Processa um prompt do usuário e retorna a resposta do assistente.
        """
        self._learn_from_interaction(prompt)

        rag_answer = self.rag.answer_with_rag(prompt)
        if rag_answer:
            return f"(Com base no meu conhecimento local)\n{rag_answer}"

        tool_decision = self.nlp_client.decide_on_tool(prompt)
        search_query = tool_decision.get("query") if tool_decision and tool_decision.get("tool") == "web_search" else None

        if search_query:
            print(f"[Jarvis] Decidi pesquisar na web sobre: '{search_query}'")
            search_results = search_web(search_query)
            
            # --- PROMPT FINAL REFINADO PARA BUSCA ---
            final_prompt = (
                f"Com base **exclusivamente** nos seguintes resultados de pesquisa, responda à pergunta do usuário.\n\n"
                f"--- Resultados da Pesquisa na Web ---\n{search_results}\n--- Fim dos Resultados ---\n\n"
                f"Pergunta original do usuário: {prompt}"
            )
        else:
            # Se não houver busca, enriquece com memória e sentimento
            sentiment = self.sentiment_analyzer.analyze(prompt)
            sentiment_context = f"O sentimento do usuário parece ser {sentiment}."
            
            relevant_facts = self.memory.get_relevant_facts(prompt)
            memory_context = ""
            if relevant_facts:
                memory_context = "\n\n--- Fatos relevantes da memória ---\n" + "\n".join(f"- {fact}" for fact in relevant_facts)
                print(f"[Memória] Fatos relevantes encontrados e adicionados ao prompt: {relevant_facts}")

            final_prompt = f"Contexto: {sentiment_context}{memory_context}\n\nPergunta: {prompt}"

        self.conversation_history.append({"role": "user", "content": final_prompt})
        response = self.nlp_client.generate(
            prompt=final_prompt,
            conversation_history=self.conversation_history
        )
        self.conversation_history.append({"role": "assistant", "content": response})

        command_response = self.command_handler.handle(response)
        return command_response if command_response else response

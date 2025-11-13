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
        # Etapa 1: Aprende com a entrada do usuário
        self._learn_from_interaction(prompt)

        # Etapa 2: Tenta responder com a base de conhecimento local (RAG)
        rag_answer = self.rag.answer_with_rag(prompt)
        if rag_answer:
            self.conversation_history.append({"role": "user", "content": prompt})
            self.conversation_history.append({"role": "assistant", "content": rag_answer})
            return f"(Com base no meu conhecimento local)\n{rag_answer}"

        # --- NOVO FLUXO DE DECISÃO CONTEXTUAL ---
        # Etapa 3: Constrói o contexto completo ANTES de tomar qualquer decisão
        sentiment = self.sentiment_analyzer.analyze(prompt)
        relevant_facts = self.memory.get_relevant_facts(prompt)
        
        # Etapa 4: Decide se precisa de uma ferramenta, agora com o contexto completo
        # Combina o histórico da sessão com os fatos da memória de longo prazo
        full_context_history = self.conversation_history + [{"role": "system", "content": f"Fatos conhecidos sobre o usuário: {', '.join(relevant_facts)}."}]
        
        tool_decision = self.nlp_client.decide_on_tool(prompt, full_context_history)
        search_query = tool_decision.get("query") if tool_decision and tool_decision.get("tool") == "web_search" else None

        # Etapa 5: Prepara o prompt final para a geração da resposta
        if search_query:
            print(f"[Jarvis] Decidi pesquisar na web sobre: '{search_query}'")
            search_results = search_web(search_query)
            final_prompt = (
                f"Com base **exclusivamente** nos seguintes resultados de pesquisa, responda à pergunta do usuário.\n\n"
                f"--- Resultados da Pesquisa na Web ---\n{search_results}\n--- Fim dos Resultados ---\n\n"
                f"Pergunta original do usuário: {prompt}"
            )
        else:
            # Se não houver busca, enriquece com memória e sentimento para uma resposta conversacional
            sentiment_context = f"O sentimento do usuário parece ser {sentiment}."
            memory_context = ""
            if relevant_facts:
                memory_context = "\n\n--- Fatos relevantes da memória ---\n" + "\n".join(f"- {fact}" for fact in relevant_facts)
            final_prompt = f"Contexto: {sentiment_context}{memory_context}\n\nPergunta: {prompt}"

        # Etapa 6: Gera a resposta final com o LLM
        self.conversation_history.append({"role": "user", "content": prompt}) # Adiciona o prompt original ao histórico
        response = self.nlp_client.generate(
            prompt=final_prompt,
            conversation_history=self.conversation_history
        )
        self.conversation_history.append({"role": "assistant", "content": response})

        # Etapa 7: Verifica se a resposta é um comando
        command_response = self.command_handler.handle(response)
        return command_response if command_response else response

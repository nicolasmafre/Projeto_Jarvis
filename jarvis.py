"""
Módulo central que define a classe principal do assistente Jarvis.

Este módulo integra todos os outros componentes, como o cliente de NLP,
o sistema de RAG, a memória de longo prazo e o manipulador de comandos,
para orquestrar a lógica de interação do assistente.
"""

import os
from dotenv import load_dotenv
from nlp_client import NlpClient
from rag import Rag
from commands import CommandHandler
from memory import LongTermMemory

load_dotenv()

class Jarvis:
    """
    A classe principal do assistente Jarvis.

    Orquestra a interação entre o usuário e os diferentes subsistemas
    (NLP, RAG, Memória, Comandos) para gerar respostas.
    """
    def __init__(self):
        """Inicializa todos os componentes do assistente."""
        self.nlp_client = NlpClient.create()
        self.rag = Rag()
        self.command_handler = CommandHandler()
        self.conversation_history = []
        self.memory = LongTermMemory()
        print("[Jarvis] Assistente inicializado e pronto.")

    def _enrich_prompt_with_memory(self, prompt):
        """
        Enriquece o prompt do usuário com fatos relevantes da memória de longo prazo.

        Args:
            prompt (str): O prompt original do usuário.

        Returns:
            str: O prompt enriquecido com contexto da memória, ou o prompt original.
        """
        relevant_facts = self.memory.get_relevant_facts(prompt)
        if not relevant_facts:
            return prompt

        memory_context = "\n\n--- Fatos relevantes da memória ---\n"
        for fact in relevant_facts:
            memory_context += f"- {fact}\n"
        memory_context += "--- Fim dos fatos ---\n"
        
        return f"{memory_context}\nPergunta original: {prompt}"

    def _learn_from_interaction(self, user_prompt, assistant_response):
        """
        Extrai e armazena fatos da interação atual na memória de longo prazo.

        Args:
            user_prompt (str): O prompt enviado pelo usuário.
            assistant_response (str): A resposta gerada pelo assistente.
        """
        if assistant_response.startswith("Desculpe, ocorreu um erro"):
            return

        interaction_text = f"Usuário: \"{user_prompt}\"\nAssistente: \"{assistant_response}\""
        
        fact = self.nlp_client.extract_facts(interaction_text)
        if fact:
            if self.memory.add_fact(fact):
                print(f"[Memória]: Novo fato aprendido: {fact}")

    def interact(self, prompt):
        """
        Processa um prompt do usuário e retorna a resposta do assistente.

        O fluxo de processamento é:
        1. Tenta responder usando a base de conhecimento estática (RAG).
        2. Se não houver resposta do RAG, enriquece o prompt com a memória de longo prazo.
        3. Gera uma resposta usando o cliente de NLP (LLM).
        4. Tenta aprender fatos da interação para a memória de longo prazo.
        5. Verifica se a resposta é um comando a ser executado.

        Args:
            prompt (str): O prompt do usuário.

        Returns:
            str: A resposta final do assistente.
        """
        rag_answer = self.rag.answer_with_rag(prompt)
        if rag_answer:
            self._learn_from_interaction(prompt, rag_answer)
            return rag_answer

        enriched_prompt = self._enrich_prompt_with_memory(prompt)
        
        self.conversation_history.append({"role": "user", "content": enriched_prompt})
        response = self.nlp_client.generate(
            prompt=enriched_prompt,
            conversation_history=self.conversation_history
        )
        self.conversation_history.append({"role": "assistant", "content": response})

        self._learn_from_interaction(prompt, response)

        command_response = self.command_handler.handle(response)
        if command_response:
            return command_response

        return response

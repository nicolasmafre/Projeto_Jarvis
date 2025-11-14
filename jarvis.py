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
from task_manager import TaskManager # Importa o Gerenciador de Tarefas

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
        self.memory = LongTermMemory()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.task_manager = TaskManager() # Inicializa o Gerenciador de Tarefas
        print("[Jarvis] Assistente inicializado e pronto.")

    def _learn_from_interaction(self, user_prompt):
        """Extrai e armazena fatos do prompt do usuário."""
        fact = self.nlp_client.extract_facts(user_prompt)
        if fact and self.memory.add_fact(fact):
            print(f"[Memória]: Novo fato aprendido e salvo: {fact}")

    def interact(self, prompt: str) -> str:
        """
        Processa um prompt do usuário e retorna a resposta do assistente.
        """
        self._learn_from_interaction(prompt)

        # Etapa 1: Decide a ferramenta/ação a ser tomada
        full_context_history = self.task_manager.get_active_task_state() or self.conversation_history
        tool_decision = self.nlp_client.decide_on_tool(prompt, full_context_history)
        chosen_tool = tool_decision.get("tool", "none")

        # Etapa 2: Executa meta-comandos de gerenciamento de tarefas
        if chosen_tool == "start_task":
            task_name = tool_decision.get("task_name", "Tarefa sem nome")
            self.task_manager.start_task(task_name, prompt)
            response = f"Ok, vamos começar a tarefa: '{task_name}'. Qual é o primeiro passo ou a primeira pergunta?"
            self.task_manager.update_task_history(prompt, response)
            return response
        
        if chosen_tool == "pause_task":
            self.task_manager.pause_task()
            return "Ok, tarefa pausada. Podemos continuar quando você quiser."

        if chosen_tool == "resume_task":
            # Tenta retomar a última tarefa ativa (ou a mais recente)
            if self.task_manager.tasks:
                latest_task = max(self.task_manager.tasks, key=lambda t: self.task_manager.tasks[t]['ultimo_update'])
                self.task_manager.start_task(latest_task, "")
                return f"Ok, retomando a tarefa '{latest_task}'. Onde paramos?"
            return "Não há nenhuma tarefa para retomar."

        # Se uma tarefa estiver ativa, todo o contexto vem dela
        active_task = self.task_manager.get_active_task_state()
        if active_task:
            print(f"[Jarvis] Continuando a tarefa ativa: '{self.task_manager.active_task}'")
            # O prompt para o LLM agora inclui o histórico da tarefa
            task_history = active_task.get("historico", [])
            response = self.nlp_client.generate(prompt, conversation_history=task_history)
            self.task_manager.update_task_history(prompt, response)
            return response

        # --- Fluxo Padrão (se nenhuma tarefa estiver ativa) ---
        rag_answer = self.rag.answer_with_rag(prompt)
        if rag_answer:
            # ... (lógica do RAG)
            pass
        
        # ... (lógica de busca na web e conversação geral) ...
        
        # Este é um stub, o fluxo completo precisaria ser reimplementado aqui
        response = self.nlp_client.generate(prompt, conversation_history=self.conversation_history)
        self.conversation_history.append({"role": "user", "content": prompt})
        self.conversation_history.append({"role": "assistant", "content": response})
        return response

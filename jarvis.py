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
from task_manager import TaskManager

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
        self.task_manager = TaskManager()
        self.conversation_history = []
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

        context_for_decision = self.task_manager.get_active_task_state() or self.conversation_history
        tool_decision = self.nlp_client.decide_on_tool(prompt, context_for_decision)
        
        if not isinstance(tool_decision, dict):
            tool_decision = {"tool": "none"}
            
        chosen_tool = tool_decision.get("tool", "none")

        response = ""

        if chosen_tool == "start_task":
            task_name = tool_decision.get("task_name", prompt)
            self.task_manager.start_task(task_name, prompt)
            response = f"Ok, vamos começar a tarefa: '{task_name}'. Qual é o primeiro passo ou a primeira pergunta?"
            self.task_manager.update_task_history(prompt, response)
        
        elif chosen_tool == "pause_task":
            self.task_manager.pause_task()
            response = "Ok, tarefa pausada. Podemos continuar quando você quiser."

        elif chosen_tool == "resume_task":
            if self.task_manager.tasks:
                latest_task = max(self.task_manager.tasks, key=lambda t: self.task_manager.tasks[t]['ultimo_update'])
                self.task_manager.start_task(latest_task, "")
                response = f"Ok, retomando a tarefa '{latest_task}'. Onde paramos?"
            else:
                response = "Não há nenhuma tarefa para retomar."
        
        else:
            active_task = self.task_manager.get_active_task_state()
            if active_task:
                print(f"[Jarvis] Continuando a tarefa ativa: '{self.task_manager.active_task}'")
                task_history = active_task.get("historico", [])
                response = self.nlp_client.generate(prompt, conversation_history=task_history)
                self.task_manager.update_task_history(prompt, response)
            else:
                rag_answer = self.rag.answer_with_rag(prompt)
                if rag_answer:
                    response = f"(Com base no meu conhecimento local)\n{rag_answer}"
                else:
                    search_query = tool_decision.get("query") if chosen_tool == "web_search" else None
                    if search_query:
                        print(f"[Jarvis] Decidi pesquisar na web sobre: '{search_query}'")
                        search_results = search_web(search_query)
                        final_prompt = (
                            f"Com base nos resultados da pesquisa, responda à pergunta: {prompt}\n\n"
                            f"--- Resultados da Pesquisa ---\n{search_results}"
                        )
                        response = self.nlp_client.generate(prompt=final_prompt, conversation_history=self.conversation_history)
                    else:
                        sentiment = self.sentiment_analyzer.analyze(prompt)
                        relevant_facts = self.memory.get_relevant_facts(prompt)
                        sentiment_context = f"O sentimento do usuário parece ser {sentiment}."
                        memory_context = ""
                        if relevant_facts:
                            memory_context = "\n\nFatos relevantes da memória: " + ", ".join(relevant_facts)
                        
                        final_prompt = f"Contexto: {sentiment_context}{memory_context}\n\nPergunta: {prompt}"
                        response = self.nlp_client.generate(prompt=final_prompt, conversation_history=self.conversation_history)

        if not self.task_manager.get_active_task_state():
            self.conversation_history.append({"role": "user", "content": prompt})
            self.conversation_history.append({"role": "assistant", "content": response})
        
        command_response = self.command_handler.handle(response)
        return command_response if command_response else response

"""
Módulo cliente para interagir com APIs de Modelos de Linguagem (LLMs).
"""

import os
import traceback
import json
from abc import ABC, abstractmethod
from huggingface_hub import InferenceClient

class NlpClient(ABC):
    # ... (assinaturas dos métodos) ...
    @abstractmethod
    def decide_on_tool(self, prompt, conversation_history): pass

class HuggingFaceHubClient(NlpClient):
    # ... (__init__ e _call_llm) ...

    def decide_on_tool(self, prompt, conversation_history):
        """Decide qual ferramenta ou meta-comando usar."""
        system_prompt = (
            "Sua tarefa é analisar a pergunta do usuário e o contexto para decidir a melhor ação. Responda apenas com um JSON.\n"
            "1. Para explicações de conceitos (ex: 'o que é', 'me explique'), use 'educational_query'.\n"
            "2. Para notícias ou fatos em tempo real, use 'web_search'.\n"
            "3. Se o usuário pedir para iniciar uma tarefa longa (ex: 'crie um plano de estudos', 'me ensine'), use 'start_task' com o nome da tarefa.\n"
            "4. Se o usuário pedir para parar, pausar ou interromper a tarefa atual, use 'pause_task'.\n"
            "5. Se o usuário pedir para continuar ou retomar a última tarefa, use 'resume_task'.\n"
            "6. Para conversas gerais, use 'none'.\n"
            "Exemplos:\n"
            'Pergunta: "Me ensine Cálculo I" -> {"tool": "start_task", "task_name": "Plano de Estudos de Cálculo I"}\n'
            'Pergunta: "Vamos parar por aqui." -> {"tool": "pause_task"}\n'
            'Pergunta: "Podemos continuar a aula?" -> {"tool": "resume_task"}\n'
            'Pergunta: "Quais as últimas notícias?" -> {"tool": "web_search", "query": "últimas notícias"}\n'
            'Pergunta: "Olá, tudo bem?" -> {"tool": "none"}\n'
            'Responda APENAS com o JSON.'
        )
        messages = [{"role": "system", "content": system_prompt}]
        if conversation_history: messages.extend(conversation_history[-2:])
        messages.append({"role": "user", "content": f"Pergunta: \"{prompt}\""})

        try:
            response = self._call_llm(self.general_model_name, messages, max_tokens=150, temperature=0.0)
            return json.loads(response[response.find('{'):response.rfind('}')+1])
        except Exception:
            return {"tool": "none"}

    # ... (resto dos métodos: generate, generate_educational_answer, extract_facts) ...

class ReplicateClient(NlpClient):
    # ... (stubs) ...
    def decide_on_tool(self, prompt, conversation_history): return {"tool": "none"}

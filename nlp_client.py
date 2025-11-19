"""
Módulo cliente para interagir com APIs de Modelos de Linguagem (LLMs).
"""

import os
import traceback
import json
from abc import ABC, abstractmethod
from huggingface_hub import InferenceClient

class NlpClient(ABC):
    @abstractmethod
    def generate(self, prompt, max_tokens=1024, temperature=0.7, conversation_history=None): pass
    @abstractmethod
    def generate_educational_answer(self, prompt): pass
    @abstractmethod
    def extract_facts(self, text): pass
    @abstractmethod
    def decide_on_tool(self, prompt, conversation_history): pass

    @staticmethod
    def create():
        provider = os.getenv("NLP_PROVIDER", "huggingface").lower()
        if provider == "huggingface":
            return HuggingFaceHubClient()
        elif provider == "replicate":
            return ReplicateClient()
        else:
            raise ValueError(f"Provedor de NLP desconhecido: {provider}")

class HuggingFaceHubClient(NlpClient):
    """Cliente de NLP para a API de Inferência do Hugging Face."""
    def __init__(self):
        token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_API_KEY")
        if not token: raise ValueError("A chave de API do Hugging Face não foi encontrada.")
        
        self.general_model_name = "meta-llama/Meta-Llama-3-8B-Instruct"
        self.educational_model_name = "microsoft/Phi-3-mini-4k-instruct"
        self.client = InferenceClient(token=token)

    def _call_llm(self, model_name, messages, max_tokens, temperature):
        try:
            response_stream = self.client.chat.completions.create(
                model=model_name, messages=messages, max_tokens=max_tokens, temperature=temperature, stream=True
            )
            full_response = ""
            for chunk in response_stream:
                if chunk.choices and len(chunk.choices) > 0 and chunk.choices[0].delta and chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
            return full_response
        except Exception as e:
            print(f"Ocorreu um erro ao contatar a API do Hugging Face: {e}")
            raise e

    def decide_on_tool(self, prompt, conversation_history):
        """Decide qual ferramenta ou meta-comando usar."""
        # --- PROMPT DE DECISÃO REFORÇADO ---
        system_prompt = (
            "Sua tarefa é analisar a pergunta do usuário e classificar a intenção em uma categoria. Responda apenas com um JSON.\n"
            "Categorias:\n"
            "- 'start_task': Para iniciar tarefas longas (ex: 'me ensine', 'crie um plano').\n"
            "- 'pause_task': Para parar ou pausar a tarefa atual.\n"
            "- 'resume_task': Para continuar uma tarefa anterior.\n"
            "- 'educational_query': Para perguntas sobre conceitos (ex: 'o que é', 'explique').\n"
            "- 'web_search': Para QUALQUER pergunta que precise de informações do mundo real ou em tempo real. Use para previsão do tempo, notícias, resultados esportivos, fatos sobre pessoas, lugares, empresas, etc.\n"
            "- 'none': Para conversas gerais, saudações e opiniões.\n"
            "Exemplos:\n"
            'Pergunta: "Qual a previsão do tempo para hoje?" -> {"tool": "web_search", "query": "previsão do tempo para hoje"}\n'
            'Pergunta: "Quem é o presidente da França?" -> {"tool": "web_search", "query": "presidente da França"}\n'
            'Pergunta: "Me explique a teoria da relatividade" -> {"tool": "educational_query"}\n'
            'Pergunta: "Olá, tudo bem?" -> {"tool": "none"}\n'
            'Responda APENAS com o JSON.'
        )
        messages = [{"role": "system", "content": system_prompt}]
        if conversation_history: messages.extend(conversation_history[-2:])
        messages.append({"role": "user", "content": f"Pergunta: \"{prompt}\""})

        try:
            response = self._call_llm(self.general_model_name, messages, max_tokens=150, temperature=0.0)
            json_str = response[response.find('{'):response.rfind('}')+1]
            if not json_str: return {"tool": "none"}
            return json.loads(json_str)
        except Exception as e:
            print(f"ERRO [decide_on_tool]: Falha ao decidir a ferramenta: {e}")
            return {"tool": "none"}

    def generate(self, prompt, max_tokens=1024, temperature=0.7, conversation_history=None):
        system_prompt = "Você é Jarvis, um assistente de IA prestativo e cortês..."
        messages = [{"role": "system", "content": system_prompt}]
        if conversation_history: messages.extend(conversation_history)
        messages.append({"role": "user", "content": prompt})
        try:
            return self._call_llm(self.general_model_name, messages, max_tokens, temperature)
        except Exception as e:
            return f"Desculpe, ocorreu um erro ao processar sua solicitação. Detalhes: {e}"

    def generate_educational_answer(self, prompt):
        print(f"[NLP Client] Usando o modelo educacional ({self.educational_model_name}) para a pergunta.")
        system_prompt = "Você é um tutor especialista..."
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}]
        try:
            return self._call_llm(self.educational_model_name, messages, max_tokens=1024, temperature=0.5)
        except Exception as e:
            return f"Desculpe, ocorreu um erro ao processar sua solicitação. Detalhes: {e}"

    def extract_facts(self, text):
        system_prompt = "Você é um especialista em extrair informações importantes sobre um usuário..."
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"Texto: '{text}'"}]
        try:
            fact = self._call_llm(self.general_model_name, messages, max_tokens=50, temperature=0.0)
            if "N/A" in fact or len(fact.strip()) < 8: return None
            return fact.strip()
        except Exception:
            return None

class ReplicateClient(NlpClient):
    def generate(self, prompt, max_tokens=1024, temperature=0.7, conversation_history=None): pass
    def generate_educational_answer(self, prompt): pass
    def extract_facts(self, text): pass
    def decide_on_tool(self, prompt, conversation_history): return {"tool": "none"}

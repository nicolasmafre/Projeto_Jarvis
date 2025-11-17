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

    # --- O MÉTODO FALTANTE ESTÁ AQUI ---
    @staticmethod
    def create():
        """
        Cria e retorna uma instância do cliente de NLP apropriado.
        """
        provider = os.getenv("NLP_PROVIDER", "huggingface").lower()
        if provider == "huggingface":
            return HuggingFaceHubClient()
        elif provider == "replicate":
            return ReplicateClient()
        else:
            raise ValueError(f"Provedor de NLP desconhecido: {provider}")
    # ------------------------------------

class HuggingFaceHubClient(NlpClient):
    """Cliente de NLP para a API de Inferência do Hugging Face."""
    def __init__(self):
        """Inicializa o cliente, carregando o token e os nomes dos modelos."""
        token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_API_KEY")
        if not token: raise ValueError("A chave de API do Hugging Face não foi encontrada.")
        
        self.general_model_name = "meta-llama/Meta-Llama-3-8B-Instruct"
        self.educational_model_name = "microsoft/Phi-3-mini-4k-instruct"
        
        self.client = InferenceClient(token=token)

    def _call_llm(self, model_name, messages, max_tokens, temperature):
        """Faz a chamada para a API, especificando o modelo a ser usado, e trata erros."""
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
        # ... (código do decide_on_tool) ...
        pass
        
    def generate(self, prompt, max_tokens=1024, temperature=0.7, conversation_history=None):
        """Gera uma resposta de conversação geral."""
        system_prompt = "Você é Jarvis, um assistente de IA prestativo e cortês..."
        messages = [{"role": "system", "content": system_prompt}]
        if conversation_history: messages.extend(conversation_history)
        messages.append({"role": "user", "content": prompt})
        
        try:
            return self._call_llm(self.general_model_name, messages, max_tokens, temperature)
        except Exception as e:
            return f"Desculpe, ocorreu um erro ao processar sua solicitação. Detalhes: {e}"

    def generate_educational_answer(self, prompt):
        """Gera uma resposta educacional usando o modelo Phi-3."""
        print(f"[NLP Client] Usando o modelo educacional ({self.educational_model_name}) para a pergunta.")
        system_prompt = "Você é um tutor especialista..."
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}]
        
        try:
            return self._call_llm(self.educational_model_name, messages, max_tokens=1024, temperature=0.5)
        except Exception as e:
            return f"Desculpe, ocorreu um erro ao processar sua solicitação. Detalhes: {e}"

    def extract_facts(self, text):
        """Extrai fatos importantes de um texto."""
        system_prompt = "Você é um especialista em extrair informações..."
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"Texto: '{text}'"}]
        
        try:
            fact = self._call_llm(self.general_model_name, messages, max_tokens=50, temperature=0.0)
            if "N/A" in fact or len(fact.strip()) < 8:
                return None
            return fact.strip()
        except Exception:
            return None

class ReplicateClient(NlpClient):
    def generate(self, prompt, max_tokens=1024, temperature=0.7, conversation_history=None): pass
    def generate_educational_answer(self, prompt): pass
    def extract_facts(self, text): pass
    def decide_on_tool(self, prompt, conversation_history): return {"tool": "none"}

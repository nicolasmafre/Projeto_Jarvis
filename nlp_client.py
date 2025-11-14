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
        """Faz a chamada para a API, especificando o modelo a ser usado."""
        response_stream = self.client.chat.completions.create(
            model=model_name, messages=messages, max_tokens=max_tokens, temperature=temperature, stream=True
        )
        full_response = ""
        for chunk in response_stream:
            if chunk.choices and len(chunk.choices) > 0 and chunk.choices[0].delta and chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
        return full_response

    def decide_on_tool(self, prompt, conversation_history):
        """Decide qual ferramenta ou meta-comando usar."""
        system_prompt = (
            "Sua tarefa é analisar a pergunta do usuário e o contexto para classificar a intenção em uma de seis categorias. Responda apenas com um JSON.\n"
            "1. 'start_task': Se o usuário pedir para iniciar uma tarefa longa e contínua. Ex: 'me ensine', 'crie um plano de estudos', 'vamos começar um projeto'.\n"
            "2. 'pause_task': Se o usuário pedir para parar, pausar, interromper ou fazer uma pausa. Ex: 'vamos parar por aqui', 'pausa', 'continuamos depois'.\n"
            "3. 'resume_task': Se o usuário pedir para continuar, retomar ou voltar a uma tarefa anterior. Ex: 'vamos continuar a aula', 'retomando', 'onde paramos?'.\n"
            "4. 'educational_query': Para perguntas diretas sobre conceitos, definições, explicações. Ex: 'o que é a mitose?', 'como funciona um motor?'.\n"
            "5. 'web_search': Para notícias, eventos atuais, ou fatos em tempo real.\n"
            "6. 'none': Para conversas gerais, saudações, opiniões.\n"
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
        """Gera uma resposta de conversação geral."""
        system_prompt = "Você é Jarvis, um assistente de IA prestativo e cortês..."
        messages = [{"role": "system", "content": system_prompt}]
        if conversation_history: messages.extend(conversation_history)
        messages.append({"role": "user", "content": prompt})
        return self._call_llm(self.general_model_name, messages, max_tokens, temperature)

    def generate_educational_answer(self, prompt):
        """Gera uma resposta educacional usando o modelo Phi-3."""
        print(f"[NLP Client] Usando o modelo educacional ({self.educational_model_name}) para a pergunta.")
        system_prompt = (
            "Você é um tutor especialista. Sua tarefa é explicar conceitos complexos de forma clara, concisa e didática."
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        return self._call_llm(self.educational_model_name, messages, max_tokens=1024, temperature=0.5)

    def extract_facts(self, text):
        """Extrai fatos importantes de um texto usando o modelo do Hugging Face."""
        try:
            system_prompt = (
                "Você é um especialista em extrair informações importantes sobre um usuário a partir de um texto..."
            )
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Texto: '{text}'"}
            ]
            fact = self._call_llm(self.general_model_name, messages, max_tokens=50, temperature=0.0)
            
            if "N/A" in fact or len(fact.strip()) < 8:
                return None
            return fact.strip()
        except Exception as e:
            print(f"Erro ao extrair fatos: {e}")
            return None

class ReplicateClient(NlpClient):
    def generate(self, prompt, max_tokens=1024, temperature=0.7, conversation_history=None): pass
    def generate_educational_answer(self, prompt): pass
    def extract_facts(self, text): pass
    def decide_on_tool(self, prompt, conversation_history): return {"tool": "none"}

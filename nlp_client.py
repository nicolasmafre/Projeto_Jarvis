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
    def extract_facts(self, text): pass
    @abstractmethod
    def decide_on_tool(self, prompt, conversation_history): pass

    @staticmethod
    def create():
        provider = os.getenv("NLP_PROVIDER", "huggingface").lower()
        if provider == "huggingface": return HuggingFaceHubClient()
        elif provider == "replicate": return ReplicateClient()
        else: raise ValueError(f"Provedor de NLP desconhecido: {provider}")

class HuggingFaceHubClient(NlpClient):
    """Cliente de NLP para a API de Inferência do Hugging Face."""
    def __init__(self):
        """Inicializa o cliente, carregando o token e o modelo."""
        token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_API_KEY")
        if not token: raise ValueError("A chave de API do Hugging Face não foi encontrada.")
        
        self.model = "meta-llama/Meta-Llama-3-8B-Instruct"
        self.client = InferenceClient(model=self.model, token=token)

    def _call_llm(self, messages, max_tokens, temperature):
        response_stream = self.client.chat.completions.create(messages=messages, max_tokens=max_tokens, temperature=temperature, stream=True)
        full_response = ""
        for chunk in response_stream:
            if chunk.choices and len(chunk.choices) > 0 and chunk.choices[0].delta and chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
        return full_response

    def decide_on_tool(self, prompt, conversation_history):
        """Decide se uma pesquisa na web é necessária, usando o contexto da conversa."""
        system_prompt = (
            "Sua tarefa é analisar a pergunta MAIS RECENTE do usuário e o histórico da conversa para decidir se uma pesquisa na web é necessária. "
            "Use o histórico para entender referências como 'ele', 'esse lugar', 'isso'. Responda apenas com um JSON.\n"
            "Use 'web_search' para perguntas sobre fatos, eventos, pessoas, ou lugares específicos.\n"
            "Use 'none' para conversas gerais, opiniões ou perguntas sobre o próprio usuário.\n"
            'Responda APENAS com o JSON.'
        )
        
        messages = [{"role": "system", "content": system_prompt}]
        if conversation_history:
            messages.extend(conversation_history[-4:])
        messages.append({"role": "user", "content": f"Pergunta: \"{prompt}\""})

        try:
            response = self._call_llm(messages, max_tokens=100, temperature=0.0)
            return json.loads(response[response.find('{'):response.rfind('}')+1])
        except Exception:
            return {"tool": "none"}

    def generate(self, prompt, max_tokens=1024, temperature=0.7, conversation_history=None):
        """Gera uma resposta de texto usando o modelo do Hugging Face."""
        try:
            system_prompt = (
                "Você é Jarvis, um assistente de IA prestativo, cortês e técnico. "
                "Suas respostas devem ser sempre completas, detalhadas e longas."
            )
            messages = [{"role": "system", "content": system_prompt}]
            if conversation_history: messages.extend(conversation_history)
            messages.append({"role": "user", "content": prompt})
            return self._call_llm(messages, max_tokens, temperature)
        except Exception as e:
            print(f"Ocorreu um erro ao contatar a API do Hugging Face: {e}")
            # --- A CORREÇÃO ESTÁ AQUI ---
            # Garante que uma string de erro seja sempre retornada.
            return f"Desculpe, ocorreu um erro ao processar sua solicitação. Detalhes: {e}"

    def extract_facts(self, text):
        """Extrai fatos importantes de um texto usando o modelo do Hugging Face."""
        try:
            system_prompt = (
                "Você é um especialista em extrair informações importantes sobre um usuário a partir de um texto. "
                "Seu objetivo é criar uma frase curta e afirmativa sobre o usuário. "
                "Extraia nomes, locais, gostos, preferências ou qualquer fato pessoal.\n"
                "Responda APENAS com o fato extraído ou com 'N/A'."
            )
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Texto: '{text}'"}
            ]
            fact = self._call_llm(messages, max_tokens=50, temperature=0.0)
            
            if "N/A" in fact or len(fact.strip()) < 8:
                return None
            return fact.strip()
        except Exception as e:
            print(f"Erro ao extrair fatos: {e}")
            return None

class ReplicateClient(NlpClient):
    def generate(self, prompt, max_tokens=1024, temperature=0.7, conversation_history=None): pass
    def extract_facts(self, text): pass
    def decide_on_tool(self, prompt, conversation_history): return {"tool": "none"}

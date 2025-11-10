import os
import requests
import time
import traceback
from abc import ABC, abstractmethod
from huggingface_hub import InferenceClient

class NlpClient(ABC):
    @abstractmethod
    def generate(self, prompt, max_tokens=1024, temperature=0.7, conversation_history=None):
        pass

    @abstractmethod
    def extract_facts(self, text):
        pass

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
    def __init__(self):
        token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_API_KEY")
        if not token:
            raise ValueError("A chave de API do Hugging Face não foi encontrada. Defina a variável de ambiente HF_TOKEN ou HUGGINGFACE_API_KEY.")
        
        # --- REVERTENDO PARA O LLAMA 3 ---
        self.model = "meta-llama/Meta-Llama-3-8B-Instruct"
        # ---------------------------------
        
        self.client = InferenceClient(model=self.model, token=token)

    def _call_llm(self, messages, max_tokens, temperature):
        response_stream = self.client.chat.completions.create(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True,
        )
        full_response = ""
        for chunk in response_stream:
            if chunk.choices and len(chunk.choices) > 0 and chunk.choices[0].delta and chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
        return full_response

    def generate(self, prompt, max_tokens=1024, temperature=0.7, conversation_history=None):
        if temperature <= 0:
            temperature = 0.1

        try:
            system_prompt = (
                "Você é Jarvis, um assistente de IA prestativo, cortês e técnico. "
                "Suas respostas devem ser sempre completas, detalhadas e longas, explicando o contexto e "
                "fornecendo informações adicionais sempre que possível. Não economize nas palavras."
            )
            
            messages = [
                {"role": "system", "content": system_prompt},
            ]
            if conversation_history:
                messages.extend(conversation_history)
            messages.append({"role": "user", "content": prompt})

            return self._call_llm(messages, max_tokens, temperature)

        except Exception as e:
            print("\n--- ERRO CRÍTICO NA API HUGGING FACE ---")
            print(f"Tipo de Exceção: {type(e).__name__}")
            print(f"Mensagem da Exceção: {e}")
            print("--- Traceback Completo ---")
            traceback.print_exc()
            print("--------------------------\n")
            
            error_message = str(e)
            if "Model is currently loading" in error_message or "timeout" in error_message.lower():
                user_friendly_error = f"O modelo ({self.model}) ainda está carregando ou a API está sobrecarregada. Por favor, tente novamente em alguns minutos."
            elif "authorization" in error_message.lower() or "token" in error_message.lower():
                user_friendly_error = "ERRO DE AUTORIZAÇÃO: Verifique se o seu HF_TOKEN no arquivo .env é válido, tem a permissão de 'write' e se você aceitou os termos do modelo."
            else:
                user_friendly_error = f"Ocorreu um erro inesperado. Verifique o traceback acima para detalhes técnicos."

            return f"Desculpe, ocorreu um erro ao processar sua solicitação. {user_friendly_error}"

    def extract_facts(self, text):
        try:
            system_prompt = (
                "Você é um extrator de fatos..." # (prompt omitido por brevidade)
            )
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Extraia um fato do seguinte texto: \n\n{text}"}
            ]
            fact = self._call_llm(messages, max_tokens=50, temperature=0.2)
            if "N/A" in fact or len(fact.strip()) < 5:
                return None
            return fact.strip()
        except Exception as e:
            print(f"Erro ao extrair fatos: {e}")
            return None


class ReplicateClient(NlpClient):
    # ... (código do ReplicateClient permanece o mesmo)
    def generate(self, prompt, max_tokens=1024, temperature=0.7, conversation_history=None): pass
    def extract_facts(self, text): pass

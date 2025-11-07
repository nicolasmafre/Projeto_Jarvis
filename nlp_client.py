import os
import requests
import time
from abc import ABC, abstractmethod
from huggingface_hub import InferenceClient

class NlpClient(ABC):
    @abstractmethod
    def generate(self, prompt, max_tokens=150, temperature=0.7, conversation_history=None):
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
        
        self.model = "meta-llama/Meta-Llama-3-8B-Instruct"
        self.client = InferenceClient(model=self.model, token=token)

    def generate(self, prompt, max_tokens=150, temperature=0.7, conversation_history=None):
        if temperature <= 0:
            temperature = 0.1

        try:
            messages = [
                {"role": "system", "content": "Você é Jarvis, um assistente de IA prestativo, cortês e técnico."},
                {"role": "user", "content": prompt}
            ]

            response_stream = self.client.chat.completions.create(
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
            )

            full_response = ""
            for chunk in response_stream:
                # Lógica de verificação robusta para o stream
                if chunk.choices and len(chunk.choices) > 0 and chunk.choices[0].delta and chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
            
            return full_response

        except Exception as e:
            print(f"Ocorreu um erro ao contatar a API do Hugging Face: {e}")
            if "authorization" in str(e).lower() or "token" in str(e).lower():
                print("ERRO DE AUTORIZAÇÃO: Verifique se o seu HF_TOKEN no arquivo .env é válido, tem a permissão de 'write' e não expirou.")
                print("Lembre-se também de aceitar os termos do modelo em https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct")
            return "Desculpe, ocorreu um erro ao processar sua solicitação."

class ReplicateClient(NlpClient):
    def __init__(self):
        self.api_key = os.getenv("REPLICATE_API_KEY")
        self.api_url = "https://api.replicate.com/v1/predictions"

    def generate(self, prompt, max_tokens=150, temperature=0.7, conversation_history=None):
        headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "version": "f8221218c84b31a4ebb51311b06b62728834015f69c13c00a839a3b6ed33a43d", # Llama 3 8B Instruct
            "input": {
                "prompt": prompt,
                "max_new_tokens": max_tokens,
                "temperature": temperature
            }
        }

        for i in range(3):
            response = requests.post(self.api_url, headers=headers, json=payload)
            if response.status_code == 201:
                prediction_url = response.json()["urls"]["get"]
                while True:
                    prediction_response = requests.get(prediction_url, headers=headers)
                    prediction_data = prediction_response.json()
                    if prediction_data["status"] == "succeeded":
                        return "".join(prediction_data["output"])
                    elif prediction_data["status"] in ["failed", "canceled"]:
                        return "Desculpe, a geração da resposta falhou."
                    time.sleep(1)
            elif response.status_code == 429:  # Rate limit
                time.sleep(2 ** i)
            else:
                response.raise_for_status()
        return "Desculpe, o serviço está sobrecarregado. Tente novamente mais tarde."

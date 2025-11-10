"""
Módulo cliente para interagir com APIs de Modelos de Linguagem (LLMs).

Define uma classe abstrata `NlpClient` e fornece implementações concretas
para diferentes provedores de API, como Hugging Face e Replicate.
A seleção do cliente é feita via variáveis de ambiente.
"""

import os
import traceback
from abc import ABC, abstractmethod
from huggingface_hub import InferenceClient

class NlpClient(ABC):
    """
    Classe base abstrata para todos os clientes de NLP.
    Define a interface que os clientes concretos devem implementar.
    """
    @abstractmethod
    def generate(self, prompt, max_tokens=1024, temperature=0.7, conversation_history=None):
        """
        Gera uma resposta de texto a partir de um prompt.

        Args:
            prompt (str): O texto de entrada para o modelo.
            max_tokens (int): O número máximo de tokens a serem gerados.
            temperature (float): O valor de "criatividade" da resposta.
            conversation_history (list, optional): O histórico da conversa.

        Returns:
            str: A resposta de texto gerada pelo modelo.
        """
        pass

    @abstractmethod
    def extract_facts(self, text):
        """
        Extrai fatos importantes de um trecho de texto.

        Args:
            text (str): O texto a ser analisado.

        Returns:
            str | None: O fato extraído como uma string, ou None se nenhum fato for encontrado.
        """
        pass

    @staticmethod
    def create():
        """
        Cria e retorna uma instância do cliente de NLP apropriado.

        A seleção é baseada na variável de ambiente `NLP_PROVIDER`.

        Returns:
            NlpClient: Uma instância de um cliente de NLP concreto.
        
        Raises:
            ValueError: Se o provedor de NLP especificado for desconhecido.
        """
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
        """Inicializa o cliente, carregando o token e o modelo."""
        token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_API_KEY")
        if not token:
            raise ValueError("A chave de API do Hugging Face não foi encontrada.")
        
        self.model = "meta-llama/Meta-Llama-3-8B-Instruct"
        self.client = InferenceClient(model=self.model, token=token)

    def _call_llm(self, messages, max_tokens, temperature):
        """
        Faz a chamada real para a API de chat do Hugging Face.

        Args:
            messages (list): A lista de mensagens (prompt do sistema, histórico, prompt do usuário).
            max_tokens (int): O número máximo de tokens a serem gerados.
            temperature (float): A temperatura da geração.

        Returns:
            str: A resposta completa do modelo.
        """
        response_stream = self.client.chat.completions.create(
            messages=messages, max_tokens=max_tokens, temperature=temperature, stream=True
        )
        full_response = ""
        for chunk in response_stream:
            if chunk.choices and len(chunk.choices) > 0 and chunk.choices[0].delta and chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
        return full_response

    def generate(self, prompt, max_tokens=1024, temperature=0.7, conversation_history=None):
        """Gera uma resposta de texto usando o modelo do Hugging Face."""
        if temperature <= 0:
            temperature = 0.1

        try:
            system_prompt = (
                "Você é Jarvis, um assistente de IA prestativo, cortês e técnico. "
                "Suas respostas devem ser sempre completas, detalhadas e longas, explicando o contexto e "
                "fornecendo informações adicionais sempre que possível. Não economize nas palavras."
            )
            
            messages = [{"role": "system", "content": system_prompt}]
            if conversation_history:
                messages.extend(conversation_history)
            messages.append({"role": "user", "content": prompt})

            return self._call_llm(messages, max_tokens, temperature)

        except Exception as e:
            print("\n--- ERRO CRÍTICO NA API HUGGING FACE ---")
            traceback.print_exc()
            print("--------------------------\n")
            
            error_message = str(e)
            if "Model is currently loading" in error_message or "timeout" in error_message.lower():
                user_friendly_error = f"O modelo ({self.model}) ainda está carregando ou a API está sobrecarregada."
            elif "authorization" in error_message.lower() or "token" in error_message.lower():
                user_friendly_error = "ERRO DE AUTORIZAÇÃO: Verifique seu HF_TOKEN e se você aceitou os termos do modelo."
            else:
                user_friendly_error = "Ocorreu um erro inesperado na API."

            return f"Desculpe, ocorreu um erro ao processar sua solicitação. {user_friendly_error}"

    def extract_facts(self, text):
        """Extrai fatos importantes de um texto usando o modelo do Hugging Face."""
        try:
            system_prompt = (
                "Você é um extrator de fatos. Sua tarefa é ler o texto e extrair "
                "uma única e concisa informação ou preferência do usuário. "
                "Se não houver nenhum fato claro, responda apenas com 'N/A'."
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
    """Cliente de NLP para a API do Replicate (Implementação de exemplo)."""
    def generate(self, prompt, max_tokens=1024, temperature=0.7, conversation_history=None):
        """Gera texto usando Replicate (não implementado)."""
        print("Aviso: ReplicateClient.generate() não está implementado.")
        return "Resposta de exemplo do Replicate."
    
    def extract_facts(self, text):
        """Extrai fatos usando Replicate (não implementado)."""
        print("Aviso: ReplicateClient.extract_facts() não está implementado.")
        return None

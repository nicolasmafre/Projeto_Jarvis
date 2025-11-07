import os
from dotenv import load_dotenv
from nlp_client import NlpClient
from rag import Rag
from commands import CommandHandler

load_dotenv()

class Jarvis:
    def __init__(self):
        self.nlp_client = NlpClient.create()
        self.rag = Rag()
        self.command_handler = CommandHandler()
        self.conversation_history = []

    def interact(self, prompt):
        # Etapa 1: Tenta responder com RAG
        rag_answer = self.rag.answer_with_rag(prompt)
        if rag_answer:
            return rag_answer

        # Etapa 2: Se não houver resposta do RAG, usa o LLM
        # Adiciona o prompt ao histórico da conversa
        self.conversation_history.append({"role": "user", "content": prompt})

        # Gera a resposta com o LLM
        response = self.nlp_client.generate(
            prompt=prompt,
            conversation_history=self.conversation_history
        )

        # Adiciona a resposta do LLM ao histórico
        self.conversation_history.append({"role": "assistant", "content": response})

        # Etapa 3: Verifica se a resposta é um comando
        command_response = self.command_handler.handle(response)
        if command_response:
            return command_response

        return response

import os
from dotenv import load_dotenv
from nlp_client import NlpClient
from rag import Rag
from commands import CommandHandler
from memory import LongTermMemory

load_dotenv()

class Jarvis:
    def __init__(self):
        self.nlp_client = NlpClient.create()
        self.rag = Rag()
        self.command_handler = CommandHandler()
        self.conversation_history = []
        self.memory = LongTermMemory()

    def _enrich_prompt_with_memory(self, prompt):
        relevant_facts = self.memory.get_relevant_facts(prompt)
        if not relevant_facts:
            return prompt

        memory_context = "\n\n--- Fatos relevantes da memória ---\n"
        for fact in relevant_facts:
            memory_context += f"- {fact}\n"
        memory_context += "--- Fim dos fatos ---\n"
        
        return f"{memory_context}\nPergunta original: {prompt}"

    def _learn_from_interaction(self, user_prompt, assistant_response):
        # --- A MUDANÇA ESTÁ AQUI ---
        # Não tenta aprender se a resposta do assistente for uma mensagem de erro.
        if assistant_response.startswith("Desculpe, ocorreu um erro"):
            return
        # --------------------------

        interaction_text = f"Usuário: \"{user_prompt}\"\nAssistente: \"{assistant_response}\""
        
        fact = self.nlp_client.extract_facts(interaction_text)
        if fact:
            if self.memory.add_fact(fact):
                print(f"[Memória]: Novo fato aprendido: {fact}")

    def interact(self, prompt):
        rag_answer = self.rag.answer_with_rag(prompt)
        if rag_answer:
            self._learn_from_interaction(prompt, rag_answer)
            return rag_answer

        enriched_prompt = self._enrich_prompt_with_memory(prompt)
        
        self.conversation_history.append({"role": "user", "content": enriched_prompt})
        response = self.nlp_client.generate(
            prompt=enriched_prompt,
            conversation_history=self.conversation_history
        )
        self.conversation_history.append({"role": "assistant", "content": response})

        self._learn_from_interaction(prompt, response)

        command_response = self.command_handler.handle(response)
        if command_response:
            return command_response

        return response

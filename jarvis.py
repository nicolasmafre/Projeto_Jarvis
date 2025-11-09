import os
from dotenv import load_dotenv
from nlp_client import NlpClient
from rag import Rag
from commands import CommandHandler
from memory import LongTermMemory # Importa a memória de longo prazo

load_dotenv()

class Jarvis:
    def __init__(self):
        self.nlp_client = NlpClient.create()
        self.rag = Rag()
        self.command_handler = CommandHandler()
        self.conversation_history = []
        self.memory = LongTermMemory() # Inicializa a memória de longo prazo

    def _enrich_prompt_with_memory(self, prompt):
        """Enriquece o prompt do usuário com fatos relevantes da memória."""
        relevant_facts = self.memory.get_relevant_facts(prompt)
        if not relevant_facts:
            return prompt

        # Constrói o contexto para adicionar ao prompt
        memory_context = "\n\n--- Fatos relevantes da memória ---\n"
        for fact in relevant_facts:
            memory_context += f"- {fact}\n"
        memory_context += "--- Fim dos fatos ---\n"

        # Retorna o prompt original com o contexto da memória no início
        return f"{memory_context}\nPergunta original: {prompt}"

    def _learn_from_interaction(self, user_prompt, assistant_response):
        """Extrai e armazena fatos da interação atual."""
        # Cria um texto combinado da interação para extrair fatos
        interaction_text = f"Usuário: \"{user_prompt}\"\nAssistente: \"{assistant_response}\""
        
        fact = self.nlp_client.extract_facts(interaction_text)
        if fact:
            if self.memory.add_fact(fact):
                print(f"[Memória]: Novo fato aprendido: {fact}")

    def interact(self, prompt):
        # Etapa 1: Tenta responder com RAG (conhecimento estático)
        rag_answer = self.rag.answer_with_rag(prompt)
        if rag_answer:
            # Mesmo com RAG, vamos aprender com a interação
            self._learn_from_interaction(prompt, rag_answer)
            return rag_answer

        # Etapa 2: Enriquece o prompt com a memória de longo prazo
        enriched_prompt = self._enrich_prompt_with_memory(prompt)

        # Etapa 3: Gera a resposta com o LLM usando o prompt enriquecido
        self.conversation_history.append({"role": "user", "content": enriched_prompt})
        response = self.nlp_client.generate(
            prompt=enriched_prompt, # Usa o prompt enriquecido
            conversation_history=self.conversation_history
        )
        self.conversation_history.append({"role": "assistant", "content": response})

        # Etapa 4: Aprende com a interação atual
        self._learn_from_interaction(prompt, response)

        # Etapa 5: Verifica se a resposta é um comando
        command_response = self.command_handler.handle(response)
        if command_response:
            return command_response

        return response

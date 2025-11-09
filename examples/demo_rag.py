# examples/demo_rag.py

"""
Este script demonstra a funcionalidade de Retrieval-Augmented Generation (RAG).

Ele importa a classe Jarvis, faz perguntas específicas cujas respostas estão nos
arquivos da pasta /knowledge e imprime o resultado. Isso prova que o Jarvis
está usando a base de conhecimento local para responder.
"""

# Adiciona o diretório raiz ao path para permitir a importação do Jarvis
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jarvis import Jarvis

def run_rag_demo():
    print("--- Iniciando Demonstração do RAG ---")
    jarvis_instance = Jarvis()

    # Pergunta 1: Sobre a Marvel (deve usar marvel_data.md)
    question1 = "Do que é feito o escudo do Capitão América?"
    print(f"\n[Pergunta]: {question1}")
    answer1 = jarvis_instance.interact(question1)
    print(f"[Jarvis RAG]: {answer1}")

    print("-" * 20)

    # Pergunta 2: Sobre serviços públicos (deve usar servicos_publicos_br.md)
    question2 = "Qual o número para denunciar violência contra a mulher?"
    print(f"\n[Pergunta]: {question2}")
    answer2 = jarvis_instance.interact(question2)
    print(f"[Jarvis RAG]: {answer2}")

    print("\n--- Fim da Demonstração ---")

if __name__ == "__main__":
    run_rag_demo()

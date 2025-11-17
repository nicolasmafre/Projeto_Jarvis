# examples/demo_cli_programmatic.py

"""
Este script demonstra como importar e usar a classe Jarvis diretamente
em outro projeto ou script Python, sem depender da interface do app.py.

Isso é útil para integrar a lógica do Jarvis em outras automações.
"""

# Adiciona o diretório raiz ao path para permitir a importação do Jarvis
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jarvis import Jarvis

def run_programmatic_demo():
    print("--- Iniciando Demonstração de Uso Programático ---")

    # Você pode criar uma instância do Jarvis em qualquer lugar
    my_jarvis = Jarvis()

    # Agora você pode usar a instância para interagir
    prompt1 = "Escreva uma função em Python que some dois números."
    print(f"\n[Script]: Enviando prompt: '{prompt1}'")
    response1 = my_jarvis.interact(prompt1)
    print(f"[Jarvis]:\n{response1}")

    print("-" * 20)

    prompt2 = "Qual o número do Corpo de Bombeiros?"
    print(f"\n[Script]: Enviando prompt: '{prompt2}'")
    response2 = my_jarvis.interact(prompt2)
    print(f"[Jarvis]: {response2}")

    print("\n--- Fim da Demonstração ---")

if __name__ == "__main__":
    run_programmatic_demo()

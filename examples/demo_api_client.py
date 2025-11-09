# examples/demo_api_client.py

"""
Este script demonstra como um cliente externo pode interagir com a API web do Jarvis.

Para que este script funcione, o servidor Flask do Jarvis deve estar rodando
(execute 'python app.py --web' em outro terminal).
"""

import requests
import json

def run_api_client_demo():
    print("--- Iniciando Demonstração do Cliente de API ---")
    api_url = "http://127.0.0.1:5000/chat"

    # Mensagem para enviar ao Jarvis
    prompt = "Olá Jarvis, qual a sua função principal?"

    headers = {"Content-Type": "application/json"}
    payload = {"prompt": prompt}

    try:
        print(f"\n[Cliente]: Enviando prompt para {api_url}: '{prompt}'")
        response = requests.post(api_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Levanta um HTTPError para códigos de status ruins (4xx ou 5xx)

        response_data = response.json()
        print(f"[Jarvis API]: {response_data.get('response', 'Nenhuma resposta.')}")

    except requests.exceptions.ConnectionError:
        print("ERRO: Não foi possível conectar ao servidor Flask do Jarvis.")
        print("Certifique-se de que o servidor está rodando (execute 'python app.py --web' em outro terminal).")
    except requests.exceptions.HTTPError as e:
        print(f"ERRO HTTP: {e}")
        print(f"Resposta do servidor: {response.text}")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

    print("\n--- Fim da Demonstração ---")

if __name__ == "__main__":
    run_api_client_demo()

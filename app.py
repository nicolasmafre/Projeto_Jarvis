import argparse
import os
import sys
import contextlib
import subprocess
import platform
import io
from ctypes import CFUNCTYPE, c_char_p, c_int, cdll
from flask import Flask, request, jsonify, render_template, Response
from jarvis import Jarvis
from stt import STT
from tts import TTS

# --- Força a codificação UTF-8 para stdin/stdout para evitar UnicodeDecodeError ---
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
except (TypeError, ValueError):
    # Ocorre em alguns ambientes onde o buffer não está disponível (ex: IDEs)
    print("Aviso: Não foi possível reconfigurar a codificação de stdin/stdout.")
# --------------------------------------------------------------------------------

# --- Context Manager Avançado para suprimir erros do ALSA ---
ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)

def py_error_handler(filename, line, function, err, fmt):
    """Função vazia para atuar como nosso manipulador de erro C."""
    pass

c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

@contextlib.contextmanager
def no_alsa_err():
    """Suprime as mensagens de erro do ALSA redirecionando-as para uma função vazia."""
    if platform.system() != "Linux":
        yield
        return
    try:
        asound = cdll.LoadLibrary('libasound.so.2')
        asound.snd_lib_error_set_handler(c_error_handler)
        yield
        asound.snd_lib_error_set_handler(None)
    except (OSError, AttributeError):
        yield


app = Flask(__name__)
jarvis = Jarvis()

@app.route("/", methods=["GET"])
def index():
    """Renderiza a página principal do chat web."""
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    """Processa as mensagens de chat da interface web ou API."""
    is_htmx = "HX-Request" in request.headers
    prompt = request.form.get("prompt") if is_htmx else request.get_json().get("prompt")

    if not prompt:
        return "<div class='jarvis-message'>Erro: Prompt não fornecido.</div>" if is_htmx else (jsonify({"error": "Prompt não fornecido"}), 400)

    response_text = jarvis.interact(prompt)

    if is_htmx:
        user_html = f"<div class='user-message'><b>Você:</b> {prompt}</div>"
        jarvis_html = f"<div class='jarvis-message'><b>Jarvis:</b> {response_text}</div>"
        return Response(user_html + jarvis_html, mimetype='text/html')
    else:
        return jsonify({"response": response_text})

@app.route("/voice", methods=["POST"])
def voice():
    """Endpoint futuro para processamento de áudio de voz."""
    return jsonify({"error": "Endpoint de voz ainda não implementado"}), 501

def cli_interface():
    """Inicia a interface de linha de comando com um menu de seleção de modo."""
    print("=================================")
    print("      INICIAR PROJETO JARVIS     ")
    print("=================================")
    mode = input("Escolha o modo de interação: [1] Voz ou [2] Texto: ")

    if mode == '1':
        run_voice_cli()
    else:
        run_text_cli()

def run_text_cli():
    """Executa o loop da CLI para interação baseada em texto."""
    print("\n--- Modo Texto Ativado ---")
    print("Jarvis: Olá! Como posso ajudar?")
    while True:
        try:
            prompt = input("Você: ")
            if prompt.lower().strip() in ["sair", "exit"]:
                print("Jarvis: Até logo!")
                break
            response = jarvis.interact(prompt)
            print(f"Jarvis: {response}")
        except (KeyboardInterrupt, EOFError):
            print("\nJarvis: Até logo!")
            break

def run_voice_cli():
    """Executa o loop da CLI para interação por voz, gerenciando o pavucontrol."""
    print("\n--- Modo Voz Ativado ---")
    pavucontrol_process = None
    
    try:
        if platform.system() == "Linux":
            print("Tentando iniciar o PulseAudio Volume Control (pavucontrol)...")
            try:
                pavucontrol_process = subprocess.Popen(["pavucontrol"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print("pavucontrol iniciado em segundo plano. Use-o para ajustar seu microfone.")
            except FileNotFoundError:
                print("Aviso: 'pavucontrol' não encontrado. Continuando sem ele.")
        
        with no_alsa_err():
            tts_instance = TTS()

        initial_greeting = "Olá! Como posso ajudar?"
        print(f"Jarvis: {initial_greeting}")
        tts_instance.speak(initial_greeting)

        while True:
            print("Você: (Pressione Enter para ativar o microfone ou digite 'sair' para encerrar)")
            if input().lower().strip() in ["sair", "exit"]:
                 break

            print("Você: (Ouvindo...)")
            with no_alsa_err():
                stt_instance = STT()
                prompt = stt_instance.listen()
            
            print(f"(Você disse: {prompt})\n")

            if prompt.lower().strip().replace('.', '') in ["sair", "exit", "encerrar", "parar"]:
                break
            
            if prompt.startswith("Não entendi") or prompt.startswith("Erro no serviço") or prompt.startswith("Tempo de escuta esgotado"):
                response = "Desculpe, não consegui entender. Pode repetir?"
            else:
                response = jarvis.interact(prompt)
            
            print(f"Jarvis: {response}")
            tts_instance.speak(response)

    except (KeyboardInterrupt, EOFError):
        print("\nSaindo...")
    finally:
        if pavucontrol_process:
            print("\nEncerrando o pavucontrol...")
            pavucontrol_process.terminate()
            try:
                pavucontrol_process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                pavucontrol_process.kill()
            print("pavucontrol encerrado.")
        
        exit_message = "Até logo!"
        print(f"Jarvis: {exit_message}")
        if 'tts_instance' in locals():
            tts_instance.speak(exit_message)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Jarvis - Assistente de Linguagem Natural")
    parser.add_argument("--web", action="store_true", help="Iniciar a interface web com Flask")
    args = parser.parse_args()

    if args.web:
        app.run(debug=True, port=5000)
    else:
        cli_interface()

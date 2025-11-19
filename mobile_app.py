import flet as ft
import threading
import requests
import os

# --- Configuração do Servidor ---
# Use 'http://127.0.0.1:5000' para testar no mesmo PC.
# Para testar no celular, substitua pelo IP do seu computador na rede Wi-Fi.
# Ex: 'http://192.168.1.10:5000'
# Você pode pegar o IP do seu PC com 'ip a' ou 'ifconfig' no Linux.
SERVER_URL = os.getenv("JARVIS_SERVER_URL", "http://127.0.0.1:5000")
CHAT_ENDPOINT = f"{SERVER_URL}/chat"

def main(page: ft.Page):
    page.title = "Jarvis Mobile"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 400
    page.window_height = 700

    def on_message(msg: dict):
        """Callback que é chamado quando uma nova mensagem é recebida."""
        author = msg["author"]
        text = msg["message"]
        
        if author == "Jarvis":
            send_button.disabled = False
            new_message.disabled = False
        
        show_message(author, text)
        page.update()

    page.pubsub.subscribe(on_message)

    def show_message(author: str, message: str):
        """Adiciona uma nova mensagem à lista de chat."""
        is_user = author == "Você"
        chat_list.controls.append(
            ft.Row(
                controls=[
                    ft.CircleAvatar(content=ft.Text(author[0]), bgcolor=ft.Colors.BLUE_GREY_700 if is_user else ft.Colors.GREEN_800),
                    ft.Column(controls=[ft.Text(author, weight=ft.FontWeight.BOLD), ft.Text(message, selectable=True)]),
                ],
            )
        )

    def handle_server_response(prompt: str):
        """Função executada na thread para obter a resposta do servidor."""
        try:
            # --- A MUDANÇA ESTÁ AQUI: Faz uma requisição HTTP ---
            response = requests.post(CHAT_ENDPOINT, json={"prompt": prompt}, timeout=120)
            response.raise_for_status() # Levanta um erro para status 4xx/5xx
            response_text = response.json().get("response", "Erro: Resposta sem conteúdo.")
            # ----------------------------------------------------
        except requests.exceptions.RequestException as e:
            response_text = f"Erro de conexão: {e}"

        page.pubsub.send_all({"author": "Jarvis", "message": response_text})

    def send_message_click(e):
        """Callback para quando o botão de envio é clicado."""
        prompt = new_message.value
        if not prompt:
            return

        show_message("Você", prompt)
        page.update()
        
        new_message.value = ""
        send_button.disabled = True
        new_message.disabled = True
        page.update()

        thread = threading.Thread(target=handle_server_response, args=(prompt,))
        thread.start()

    chat_list = ft.ListView(expand=True, spacing=10, auto_scroll=True)
    new_message = ft.TextField(hint_text="Digite sua mensagem...", autofocus=True, expand=True, on_submit=send_message_click)
    send_button = ft.IconButton(icon=ft.Icons.SEND_ROUNDED, on_click=send_message_click)

    page.add(ft.Container(content=chat_list, expand=True), ft.Row(controls=[new_message, send_button]))

if __name__ == "__main__":
    ft.app(target=main)

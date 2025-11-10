import flet as ft
from jarvis import Jarvis
import threading
import time

def main(page: ft.Page):
    # --- Configuração da Página ---
    page.title = "Jarvis GUI"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 800
    page.window_height = 900

    # Instância do Jarvis
    jarvis = Jarvis()

    def show_message(author: str, message: str, is_user: bool):
        """Adiciona uma nova mensagem à lista de chat."""
        chat_list.controls.append(
            ft.Row(
                controls=[
                    ft.CircleAvatar(content=ft.Text(author[0]), bgcolor=ft.Colors.BLUE_GREY_700 if is_user else ft.Colors.GREEN_800),
                    ft.Column(
                        controls=[
                            ft.Text(author, weight=ft.FontWeight.BOLD),
                            ft.Text(message, selectable=True, width=page.window_width - 150),
                        ]
                    ),
                ],
                alignment=ft.MainAxisAlignment.START if not is_user else ft.MainAxisAlignment.END,
            )
        )
        page.update()

    def handle_jarvis_response(prompt: str):
        """Função executada na thread para obter a resposta do Jarvis."""
        response = jarvis.interact(prompt)
        
        # --- A CORREÇÃO FINAL E CORRETA ESTÁ AQUI ---
        # A sintaxe correta é passar uma função (lambda) para o 'handler'.
        page.run_thread(handler=lambda: show_message("Jarvis", response, False))
        
        page.run_thread(handler=lambda: setattr(send_button, 'disabled', False))
        page.run_thread(handler=lambda: setattr(new_message, 'disabled', False))
        page.run_thread(handler=page.update)
        # -------------------------------------------


    def send_message_click(e):
        """Callback para quando o botão de envio é clicado."""
        prompt = new_message.value
        if not prompt:
            return

        show_message("Você", prompt, True)
        
        new_message.value = ""
        send_button.disabled = True
        new_message.disabled = True
        page.update()

        thread = threading.Thread(target=handle_jarvis_response, args=(prompt,))
        thread.start()

    # --- Componentes da UI ---
    chat_list = ft.ListView(
        expand=True,
        spacing=10,
        auto_scroll=True,
    )

    new_message = ft.TextField(
        hint_text="Digite sua mensagem...",
        autofocus=True,
        expand=True,
        on_submit=send_message_click,
    )

    send_button = ft.IconButton(
        icon=ft.Icons.SEND_ROUNDED,
        tooltip="Enviar Mensagem",
        on_click=send_message_click,
    )

    # --- Layout da Página ---
    page.add(
        ft.Container(
            content=chat_list,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=5,
            padding=10,
            expand=True,
        ),
        ft.Row(
            controls=[
                new_message,
                send_button,
            ]
        ),
    )

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.FLET_APP_HIDDEN)

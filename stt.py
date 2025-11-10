"""
Módulo de Speech-to-Text (STT).

Responsável por capturar áudio do microfone do usuário e convertê-lo
em texto usando um serviço de reconhecimento de fala.
"""

import speech_recognition as sr
import os

class STT:
    """
    Gerencia a captura de áudio e o reconhecimento de fala.
    """
    def __init__(self):
        """
        Inicializa o reconhecedor de fala e configura seus parâmetros.
        """
        self.recognizer = sr.Recognizer()
        
        # Ativa o ajuste dinâmico de energia para melhor reconhecimento
        self.recognizer.dynamic_energy_threshold = True
        
        # Aumenta o limiar de pausa para permitir pausas mais longas na fala
        self.recognizer.pause_threshold = 2.0

        try:
            self.device_index = int(os.getenv("MIC_INDEX"))
        except (ValueError, TypeError):
            self.device_index = None

    def listen(self):
        """
        Captura áudio do microfone e o transcreve para texto.

        Abre o microfone, ouve a fala do usuário até detectar uma pausa,
        e envia o áudio para a API de reconhecimento do Google.

        Returns:
            str: O texto transcrito da fala, ou uma mensagem de erro.
        """
        try:
            with sr.Microphone(device_index=self.device_index) as source:
                # Não usa mais adjust_for_ambient_noise devido ao dynamic_energy_threshold
                print("Diga algo...")
                try:
                    audio = self.recognizer.listen(source, timeout=10)
                except sr.WaitTimeoutError:
                    return "Tempo de escuta esgotado. Nenhum som detectado."
        except Exception as e:
            error_message = f"Erro ao acessar o microfone: {e}. "
            if self.device_index is not None:
                error_message += f"Verifique se o dispositivo com índice {self.device_index} está disponível."
            else:
                error_message += "Verifique se há um microfone padrão disponível."
            return error_message

        try:
            return self.recognizer.recognize_google(audio, language='pt-BR')
        except sr.UnknownValueError:
            return "Não entendi o que você disse."
        except sr.RequestError as e:
            return f"Erro no serviço de reconhecimento de fala; {e}"

"""
Módulo de Text-to-Speech (TTS).

Responsável por converter strings de texto em fala audível, usando
diferentes motores de síntese de voz.
"""

import os
import pyttsx3
import subprocess
import platform

class TTS:
    """
    Gerencia a síntese de fala.

    Suporta múltiplos motores de TTS, como 'pyttsx3' (padrão, usa vozes do sistema)
    e 'espeak-ng' (voz robótica offline). A seleção é feita pela variável
    de ambiente `TTS_ENGINE`.
    """
    def __init__(self):
        """
        Inicializa o motor de TTS com base na configuração do ambiente.
        """
        self.engine_type = os.getenv("TTS_ENGINE", "pyttsx3").lower()
        self.engine = None
        self.espeak_command = []

        if self.engine_type == "espeak-ng":
            self._init_espeak_ng()
        else:
            self._init_pyttsx3()

    def _init_pyttsx3(self):
        """Inicializa o motor pyttsx3 e tenta configurar uma voz em português."""
        try:
            self.engine = pyttsx3.init()
            voices = self.engine.getProperty('voices')
            for voice in voices:
                if 'pt' in voice.lang.lower():
                    self.engine.setProperty('voice', voice.id)
                    break
            print("TTS Engine: pyttsx3 (usando vozes do sistema)")
        except Exception as e:
            print(f"Erro ao inicializar pyttsx3: {e}. Tentando eSpeak-ng como fallback.")
            self.engine_type = "espeak-ng"
            self._init_espeak_ng()

    def _init_espeak_ng(self):
        """Inicializa e verifica a disponibilidade do motor eSpeak-ng."""
        try:
            cmd = "where" if platform.system() == "Windows" else "which"
            subprocess.run([cmd, "espeak-ng"], check=True, capture_output=True)
            self.espeak_command = ["espeak-ng", "-v", "pt-br", "-s", "150"]
            print("TTS Engine: eSpeak-ng")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("ERRO: eSpeak-ng não encontrado. Usando pyttsx3 como fallback (se disponível).")
            self.engine_type = "pyttsx3"
            if not self.engine: self._init_pyttsx3()

    def speak(self, text):
        """
        Converte e fala o texto fornecido usando o motor de TTS configurado.

        Args:
            text (str): O texto a ser falado.
        """
        if self.engine_type == "espeak-ng" and self.espeak_command:
            try:
                command = self.espeak_command + [text]
                subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception as e:
                print(f"Erro ao usar eSpeak-ng: {e}.")
        elif self.engine:
            self.engine.say(text)
            self.engine.runAndWait()
        else:
            print(f"AVISO: Nenhum motor de TTS funcional para falar: {text}")

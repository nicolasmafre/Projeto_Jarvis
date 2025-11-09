import os
import pyttsx3
import subprocess
import platform

class TTS:
    def __init__(self):
        self.engine_type = os.getenv("TTS_ENGINE", "pyttsx3").lower()
        self.espeak_command = [] # Inicializa para evitar erro se não for usado

        if self.engine_type == "espeak-ng":
            self._init_espeak_ng()
        else: # Padrão para pyttsx3
            self._init_pyttsx3()

    def _init_pyttsx3(self):
        try:
            self.engine = pyttsx3.init()
            # Tenta definir uma voz em português se disponível
            voices = self.engine.getProperty('voices')
            pt_voice_found = False
            for voice in voices:
                if 'pt' in voice.lang.lower():
                    self.engine.setProperty('voice', voice.id)
                    pt_voice_found = True
                    break
            if not pt_voice_found:
                print("Aviso: Nenhuma voz em português encontrada para pyttsx3. Usando a voz padrão.")
            print("TTS Engine: pyttsx3 (usando vozes do sistema)")
        except Exception as e:
            print(f"Erro ao inicializar pyttsx3: {e}. Tentando eSpeak-ng como fallback.")
            self.engine_type = "espeak-ng"
            self._init_espeak_ng()

    def _init_espeak_ng(self):
        # Verifica se espeak-ng está instalado e no PATH
        try:
            if platform.system() == "Windows":
                subprocess.run(["where", "espeak-ng"], check=True, capture_output=True)
            else:
                subprocess.run(["which", "espeak-ng"], check=True, capture_output=True)
            
            # Define o comando espeak-ng. -v pt-br para voz em português, -s 150 para velocidade
            self.espeak_command = ["espeak-ng", "-v", "pt-br", "-s", "150"]
            print("TTS Engine: eSpeak-ng")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("ERRO: eSpeak-ng não encontrado ou não está no PATH. Por favor, instale-o.")
            print("Instruções: https://espeak-ng.sourceforge.io/download.html")
            print("Voltando para pyttsx3 (se disponível).")
            self.engine_type = "pyttsx3"
            self._init_pyttsx3() # Fallback para pyttsx3

    def speak(self, text):
        if self.engine_type == "espeak-ng":
            try:
                # Usa subprocess para chamar espeak-ng
                command = self.espeak_command + [text]
                subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception as e:
                print(f"Erro ao usar eSpeak-ng: {e}. Verifique a instalação e o PATH.")
        else: # pyttsx3
            self.engine.say(text)
            self.engine.runAndWait()

# Alternativas comerciais:
# - Google Cloud Text-to-Speech: https://cloud.google.com/text-to-speech
# - Amazon Polly: https://aws.amazon.com/polly/

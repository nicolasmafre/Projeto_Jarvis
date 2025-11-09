import speech_recognition as sr
import os

class STT:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        
        # Ativa o ajuste dinâmico de energia. Isso é muito mais robusto
        # do que o 'adjust_for_ambient_noise' para lidar com variações de volume.
        self.recognizer.dynamic_energy_threshold = True
        
        # Mantemos um limiar de pausa generoso para evitar cortes em pausas naturais.
        self.recognizer.pause_threshold = 2.0
        # -----------------------------------------

        try:
            self.device_index = int(os.getenv("MIC_INDEX"))
        except (ValueError, TypeError):
            self.device_index = None

    def listen(self):
        try:
            with sr.Microphone(device_index=self.device_index) as source:
                # NÃO usamos mais o adjust_for_ambient_noise.
                # O dynamic_energy_threshold faz um trabalho melhor.
                print("Diga algo...")
                try:
                    # O phrase_time_limit foi removido para permitir falas de qualquer duração.
                    audio = self.recognizer.listen(source, timeout=10)
                except sr.WaitTimeoutError:
                    return "Tempo de escuta esgotado. Nenhum som detectado."
        except Exception as e:
            error_message = f"Erro ao acessar o microfone: {e}. "
            if self.device_index is not None:
                error_message += f"Verifique se o dispositivo com índice {self.device_index} está disponível e não está em uso."
            else:
                error_message += "Verifique se há um microfone padrão disponível e se as permissões estão corretas."
            return error_message

        try:
            # Tenta reconhecer a fala
            return self.recognizer.recognize_google(audio, language='pt-BR')
        except sr.UnknownValueError:
            return "Não entendi o que você disse."
        except sr.RequestError as e:
            return f"Erro no serviço de reconhecimento de fala; {e}"

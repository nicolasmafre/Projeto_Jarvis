import speech_recognition as sr

class STT:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def listen(self):
        with sr.Microphone() as source:
            audio = self.recognizer.listen(source)
        try:
            return self.recognizer.recognize_google(audio, language='pt-BR')
        except sr.UnknownValueError:
            return "Não entendi o que você disse."
        except sr.RequestError as e:
            return f"Erro no serviço de reconhecimento de fala; {e}"

# Alternativas:
# - Whisper (OpenAI): https://github.com/openai/whisper
# - Google Cloud Speech-to-Text: https://cloud.google.com/speech-to-text
# - Amazon Transcribe: https://aws.amazon.com/transcribe/

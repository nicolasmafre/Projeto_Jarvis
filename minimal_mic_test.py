import speech_recognition as sr
import os
from dotenv import load_dotenv

def run_minimal_test():
    """
    Um teste mínimo e isolado para verificar a funcionalidade do microfone.
    """
    print("--- INICIANDO TESTE MÍNIMO DO MICROFONE ---")
    
    # Carrega as variáveis de ambiente do arquivo .env
    load_dotenv()
    
    try:
        mic_index_str = os.getenv("MIC_INDEX")
        if mic_index_str:
            mic_index = int(mic_index_str)
            print(f"Tentando usar o microfone com índice: {mic_index}")
        else:
            mic_index = None
            print("Nenhum MIC_INDEX definido. Tentando usar o microfone padrão.")
    except (ValueError, TypeError):
        print("ERRO: MIC_INDEX no arquivo .env não é um número válido.")
        return

    recognizer = sr.Recognizer()
    
    try:
        with sr.Microphone(device_index=mic_index) as source:
            print("\nPASSO 1: Microfone aberto com sucesso.")
            
            print("PASSO 2: Ajustando para ruído ambiente (1 segundo)...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Ajuste de ruído concluído.")
            
            print("\nPASSO 3: Ouvindo... Por favor, diga 'teste'. (Você tem 5 segundos)")
            audio = recognizer.listen(source, timeout=5)
            print("Escuta concluída. Processando...")
            
            text = recognizer.recognize_google(audio, language='pt-BR')
            print(f"\nSUCESSO! Texto reconhecido: '{text}'")
            
    except sr.WaitTimeoutError:
        print("\nFALHA: Tempo de escuta esgotado. Nenhum som foi detectado.")
    except sr.UnknownValueError:
        print("\nFALHA: O Google Speech Recognition não conseguiu entender o áudio.")
    except sr.RequestError as e:
        print(f"\nFALHA: Não foi possível solicitar resultados do Google Speech Recognition; {e}")
    except Exception as e:
        print(f"\n--- ERRO CRÍTICO CAPTURADO ---")
        print(f"Ocorreu um erro inesperado: {e}")
        print("Este é provavelmente o erro raiz que impede o microfone de funcionar no Jarvis.")
        print("Verifique se o índice do microfone está correto e se o dispositivo não está sendo usado por outro programa.")

    print("\n--- TESTE MÍNIMO CONCLUÍDO ---")

if __name__ == "__main__":
    run_minimal_test()

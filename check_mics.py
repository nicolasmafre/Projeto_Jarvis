import speech_recognition as sr

def list_microphones():
    """
    Lista todos os microfones disponíveis e seus índices.
    """
    print("\n--- Listando Microfones Disponíveis ---")
    try:
        mic_list = sr.Microphone.list_microphone_names()
        if not mic_list:
            print("Nenhum microfone encontrado.")
            return

        print("Índice | Nome do Microfone")
        print("-------|--------------------")
        for index, name in enumerate(mic_list):
            print(f"{index:<7}| {name}")
        
        print("\nInstruções:")
        print("1. Identifique o microfone que você deseja usar na lista acima.")
        print("2. Anote o número do 'Índice' correspondente.")
        print("3. Crie ou atualize a variável 'MIC_INDEX' no seu arquivo .env com este número.")
        print("   Exemplo: MIC_INDEX=2")

    except Exception as e:
        print(f"Ocorreu um erro ao tentar listar os microfones: {e}")
        print("Isso pode indicar um problema com a instalação do PyAudio ou com os drivers de áudio do seu sistema.")

if __name__ == "__main__":
    list_microphones()

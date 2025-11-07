import os

class CommandHandler:
    def __init__(self):
        self.safe_mode = os.getenv("SAFE_MODE", "True").lower() == "true"

    def handle(self, response):
        # Exemplo de um comando simples: "liste os arquivos em ..."
        if "liste os arquivos em" in response.lower():
            dir_path = response.lower().split("liste os arquivos em")[-1].strip()
            if self.safe_mode:
                confirm = input(f"Tem certeza que deseja listar os arquivos em '{dir_path}'? (s/n) ")
                if confirm.lower() != 's':
                    return "Ação cancelada."
            try:
                files = os.listdir(dir_path)
                return "\n".join(files)
            except FileNotFoundError:
                return f"Diretório não encontrado: {dir_path}"
            except Exception as e:
                return f"Erro ao listar arquivos: {e}"
        return None

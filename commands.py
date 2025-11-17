"""
Módulo para manipulação de comandos específicos.

Este módulo é responsável por analisar as respostas do LLM e identificar
se elas contêm um comando que o assistente deve executar, como
operações no sistema de arquivos.
"""

import os

class CommandHandler:
    """
    Processa texto para identificar e executar comandos predefinidos.
    """
    def __init__(self):
        """
        Inicializa o manipulador de comandos, verificando o modo de segurança.
        """
        self.safe_mode = os.getenv("SAFE_MODE", "True").lower() == "true"

    def handle(self, response):
        """
        Analisa uma resposta e executa um comando, se encontrado.

        Args:
            response (str): O texto da resposta gerada pelo LLM.

        Returns:
            str | None: O resultado da execução do comando, ou None se nenhum
                        comando for encontrado.
        """
        # --- A CORREÇÃO ESTÁ AQUI ---
        # Adiciona uma verificação para garantir que a resposta não é nula.
        if not response:
            return None
        # --------------------------

        response_lower = response.lower()
        
        if "liste os arquivos em" in response_lower:
            try:
                dir_path = response_lower.split("liste os arquivos em")[-1].strip().replace("'", "").replace("\"", "")
                if not dir_path:
                    return "Erro: O caminho do diretório não foi especificado."

                if self.safe_mode:
                    confirm = input(f"Tem certeza que deseja listar os arquivos em '{dir_path}'? (s/n) ")
                    if confirm.lower() != 's':
                        return "Ação cancelada."
                
                files = os.listdir(dir_path)
                if not files:
                    return f"O diretório '{dir_path}' está vazio."
                return "\n".join(files)

            except FileNotFoundError:
                return f"Diretório não encontrado: {dir_path}"
            except Exception as e:
                return f"Erro ao listar arquivos: {e}"
        
        return None

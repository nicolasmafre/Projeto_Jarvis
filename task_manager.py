"""
Módulo para gerenciar o estado de tarefas de longo prazo.
"""

import json
import os
from datetime import datetime

class TaskManager:
    """Gerencia o ciclo de vida de tarefas complexas."""
    def __init__(self, tasks_dir="tasks"):
        """Inicializa o gerenciador, criando o diretório de tarefas se necessário."""
        self.tasks_dir = tasks_dir
        os.makedirs(self.tasks_dir, exist_ok=True)
        self.active_task = None
        self.task_file = os.path.join(self.tasks_dir, "tasks.json")
        self.tasks = self._load_tasks()
        print(f"[TaskManager] Inicializado. {len(self.tasks)} tarefas salvas encontradas.")

    def _load_tasks(self):
        """Carrega as tarefas salvas do arquivo JSON."""
        if os.path.exists(self.task_file):
            try:
                with open(self.task_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def _save_tasks(self):
        """Salva o dicionário de tarefas no arquivo JSON."""
        try:
            with open(self.task_file, 'w', encoding='utf-8') as f:
                json.dump(self.tasks, f, indent=2, ensure_ascii=False)
            # --- DEBUGGING ADICIONADO ---
            print(f"[TaskManager] Estado das tarefas salvo com sucesso em '{self.task_file}'")
        except Exception as e:
            print(f"ERRO [TaskManager]: Falha ao salvar o arquivo de tarefas: {e}")

    def start_task(self, task_name: str, initial_prompt: str):
        """Inicia uma nova tarefa ou retoma uma existente."""
        if task_name in self.tasks:
            print(f"[TaskManager] Retomando tarefa existente: '{task_name}'")
            self.active_task = task_name
            return self.tasks[task_name]
        
        print(f"[TaskManager] Iniciando nova tarefa: '{task_name}'")
        self.active_task = task_name
        new_task_state = {
            "prompt_inicial": initial_prompt,
            "historico": [],
            "feedback_usuario": [],
            "ultimo_update": datetime.now().isoformat()
        }
        self.tasks[task_name] = new_task_state
        self._save_tasks() # Garante que a nova tarefa seja salva imediatamente
        return new_task_state

    def update_task_history(self, user_input: str, assistant_output: str):
        """Adiciona uma interação ao histórico da tarefa ativa e salva."""
        if not self.active_task:
            return
        
        task = self.tasks.get(self.active_task)
        if task:
            task["historico"].append({"role": "user", "content": user_input})
            task["historico"].append({"role": "assistant", "content": assistant_output})
            task["ultimo_update"] = datetime.now().isoformat()
            self._save_tasks() # Salva a cada atualização

    def add_feedback(self, feedback: str):
        """Adiciona um feedback do usuário à tarefa ativa e salva."""
        if not self.active_task: return
        task = self.tasks.get(self.active_task)
        if task:
            task["feedback_usuario"].append(feedback)
            self._save_tasks()
            print(f"[TaskManager] Feedback adicionado à tarefa '{self.active_task}': {feedback}")

    def pause_task(self):
        """Pausa a tarefa ativa, garantindo que o estado seja salvo."""
        if self.active_task:
            print(f"[TaskManager] Tarefa '{self.active_task}' pausada.")
            self._save_tasks() # Garante um último salvamento
            self.active_task = None
            
    def get_active_task_state(self):
        """Retorna o estado completo da tarefa ativa."""
        if self.active_task:
            return self.tasks.get(self.active_task)
        return None

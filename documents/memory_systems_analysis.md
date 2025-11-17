# Análise Técnica: Sistemas de Memória (`memory.py`, `task_manager.py`)

O Projeto Jarvis utiliza uma arquitetura de memória dupla para alcançar tanto a personalização quanto a continuidade nas conversas. Cada tipo de memória tem uma função distinta e é gerenciado por um módulo especializado.

## 1. `memory.py`: Memória de Fatos (Memória Semântica)

### a) Visão Geral

Este módulo implementa a **memória de longo prazo** do Jarvis. Sua função é armazenar fatos atômicos e imutáveis sobre o usuário para personalizar as interações futuras. Ele funciona como um "banco de dados de fatos" simples.

-   **O que armazena:** Fatos sobre o usuário (ex: "O nome do usuário é Nícolas", "O usuário gosta de pizza").
-   **Persistência:** Os dados são salvos no arquivo `memory/memory.json`.

### b) Lógica Principal

-   **`_load_memory()` e `_save_memory()`**: Métodos privados que lidam com a serialização e desserialização dos fatos de/para o arquivo JSON. O salvamento ocorre automaticamente sempre que um novo fato é adicionado.
-   **`add_fact(fact)`**: Recebe um fato (uma string), verifica se ele já não existe na memória e, se for novo, o adiciona à lista e aciona o salvamento.
-   **`get_relevant_facts(query)`**: Esta é uma função de recuperação simples. Ela compara as palavras da `query` do usuário com as palavras de cada fato armazenado e retorna os fatos que têm mais palavras em comum. É uma forma básica de busca por relevância que não requer um modelo de IA.

### c) Conexão e Propósito

-   **Conexão:** O `jarvis.py` usa a `LongTermMemory` para duas coisas:
    1.  **Aprender:** Chama `add_fact()` após o `nlp_client` extrair um fato do prompt do usuário.
    2.  **Lembrar:** Chama `get_relevant_facts()` para buscar fatos relevantes que são então inseridos no prompt enviado ao LLM, dando-lhe contexto sobre com quem ele está falando.
-   **Propósito:** O objetivo desta memória é a **personalização**. Ela permite que o Jarvis se lembre de detalhes de uma sessão para outra, criando uma experiência mais contínua e pessoal.

---

## 2. `task_manager.py`: Memória de Estado de Tarefa (Memória Episódica)

### a) Visão Geral

Este módulo é a solução para a "amnésia de curto prazo" e representa a **memória de trabalho** do Jarvis. Ele foi projetado para rastrear o progresso de tarefas complexas e de múltiplos passos, como uma aula ou um projeto.

-   **O que armazena:** O estado completo de tarefas, incluindo o prompt inicial, o histórico de conversa *dentro* da tarefa, e feedbacks do usuário.
-   **Persistência:** Os estados das tarefas são salvos no arquivo `tasks/tasks.json`.

### b) Lógica Principal

-   **`start_task(task_name, ...)`**: Cria uma nova entrada no dicionário `self.tasks` com uma estrutura definida (histórico, feedback, etc.) e a salva no disco. Também define a tarefa como `self.active_task`.
-   **`update_task_history(...)`**: Adiciona a última troca de mensagens (usuário e assistente) ao histórico da tarefa *ativa* e salva o estado atualizado no disco. Este salvamento a cada passo é crucial para a persistência.
-   **`pause_task()`**: Simplesmente define `self.active_task` como `None`. Como o estado já é salvo a cada `update`, não há perda de dados.
-   **`get_active_task_state()`**: Um método getter que permite ao `jarvis.py` verificar se há uma tarefa ativa e obter seu estado (principalmente seu histórico de conversa).

### c) Conexão e Propósito

-   **Conexão:** O `jarvis.py` usa o `TaskManager` como um "controlador de estado".
    1.  **Decisão:** O `nlp_client` primeiro decide se a intenção do usuário é um meta-comando (`start_task`, `pause_task`, `resume_task`).
    2.  **Execução:** O `jarvis.py` chama os métodos correspondentes no `TaskManager` para alterar o estado (iniciar, pausar, etc.).
    3.  **Contextualização:** Se uma tarefa está ativa, o `jarvis.py` ignora o histórico de chat geral e usa **apenas** o histórico da tarefa (obtido via `get_active_task_state`) para contextualizar a próxima chamada ao LLM.
-   **Propósito:** O objetivo desta memória é a **continuidade de processos**. Ela permite que o Jarvis mantenha o foco em uma tarefa de longo prazo, lembrando o que já foi dito e feito dentro daquele contexto específico, mesmo que a aplicação seja reiniciada.

### Sinergia das Duas Memórias

Os dois sistemas trabalham em conjunto. A **Memória de Fatos** fornece o contexto geral sobre *quem é o usuário*, enquanto a **Memória de Estado de Tarefa** fornece o contexto específico sobre *o que estamos fazendo agora*. Essa arquitetura dupla é o que permite ao Jarvis ser, ao mesmo tempo, um assistente pessoal e um especialista focado em uma tarefa.

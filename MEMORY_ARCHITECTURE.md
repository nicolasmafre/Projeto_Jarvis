# A Arquitetura de Memória Dupla do Projeto Jarvis

Para se tornar um assistente verdadeiramente inteligente, o Jarvis evoluiu de uma simples memória de fatos para um sistema complexo que gerencia tanto fatos sobre o usuário quanto o estado de tarefas contínuas. Entender a diferença entre esses dois tipos de memória é crucial para compreender a capacidade atual do projeto.

## 1. Memória de Fatos (Memória Semântica)

Este é o tipo de memória mais básico, mas fundamental. Ela funciona como um conjunto de "cartões de índice" ou uma pequena base de dados sobre o usuário.

*   **O que ela armazena:** Fatos atômicos e imutáveis sobre o usuário.
    *   *Exemplo:* O nome do usuário é Nícolas.
    *   *Exemplo:* O usuário gosta de pizza e lasanha.
    *   *Exemplo:* O usuário trabalha no CEETEPS.

*   **Como funciona no Jarvis:**
    1.  **Módulo Responsável:** `memory.py` (classe `LongTermMemory`).
    2.  **Armazenamento:** Os fatos são persistidos no arquivo `memory/memory.json`.
    3.  **Extração:** A cada interação, o método `_learn_from_interaction` em `jarvis.py` chama o `nlp_client.extract_facts`. Este usa o LLM para analisar o *prompt* do usuário e extrair um fato pessoal, se houver.
    4.  **Uso:** Antes de gerar uma resposta, o método `_enrich_prompt_with_context` busca no `memory.json` por fatos que sejam semanticamente relevantes para a pergunta atual. Esses fatos são adicionados ao "contexto" enviado ao LLM, permitindo que ele personalize a resposta (ex: "Olá, Nícolas!").

*   **Analogia:** É como um amigo que se lembra do seu aniversário, do seu time de futebol e da sua comida favorita. Ele conhece você, mas não necessariamente se lembra do que vocês estavam conversando cinco minutos atrás.

*   **Limitação:** Esta memória é excelente para personalização, mas terrível para continuidade. Ela não tem noção de "processo" ou "sequência". Se você disser "vamos continuar", ela não sabe o que é para ser continuado.

## 2. Memória de Estado de Tarefa (Memória Episódica)

Este é o sistema avançado que foi implementado para superar a "amnésia de curto prazo" do Jarvis. Ele funciona como um "marcador de página" inteligente para conversas complexas e de múltiplos passos.

*   **O que ela armazena:** O estado completo de uma tarefa em andamento.
    *   *Exemplo:*
      ```json
      "Plano de Estudos de Cálculo I": {
        "prompt_inicial": "Me ensine Cálculo I",
        "historico": [
          {"role": "user", "content": "O que são limites?"},
          {"role": "assistant", "content": "Limites são o valor para o qual uma função se aproxima..."},
          {"role": "user", "content": "Não entendi a parte sobre o infinito."}
        ],
        "feedback_usuario": ["O usuário teve dificuldade com o conceito de limites"],
        "ultimo_update": "2024-07-26T12:00:00Z"
      }
      ```

*   **Como funciona no Jarvis:**
    1.  **Módulo Responsável:** `task_manager.py` (classe `TaskManager`).
    2.  **Armazenamento:** Os estados das tarefas são persistidos no arquivo `tasks/tasks.json`.
    3.  **Gerenciamento do Ciclo de Vida:**
        *   **Início:** Quando o usuário faz um pedido como "me ensine a programar em Python", o `nlp_client.decide_on_tool` identifica isso como um `start_task`. O `jarvis.py` então chama o `task_manager.start_task`, que cria uma nova entrada no `tasks.json`.
        *   **Continuidade:** Enquanto uma tarefa está ativa (`self.task_manager.active_task`), o `jarvis.py` prioriza o histórico daquela tarefa para contextualizar a conversa, ignorando o histórico de chat geral. Cada nova interação é salva dentro do `historico` da tarefa.
        *   **Pausa:** Um comando como "vamos parar por hoje" é identificado pelo `decide_on_tool` como `pause_task`. O `jarvis.py` então chama o `task_manager.pause_task`, que simplesmente desativa a tarefa na memória RAM (os dados já estão salvos no JSON).
        *   **Retomada:** Um comando como "vamos continuar nossa aula" é identificado como `resume_task`. O `jarvis.py` instrui o `TaskManager` a encontrar a tarefa mais recente e reativá-la, carregando seu estado e histórico para dar continuidade à conversa.

*   **Analogia:** É como um gerente de projetos que mantém um documento detalhado para cada projeto. Ele sabe exatamente qual era o último passo, quais foram as dificuldades e qual é o próximo item da agenda.

## A Sinergia das Duas Memórias

No Jarvis, esses dois sistemas de memória agora trabalham juntos:

1.  Ao decidir qual ferramenta usar, o Jarvis considera tanto o histórico da conversa (memória de curto prazo) quanto os fatos da memória de longo prazo (memória de fatos).
2.  Se uma tarefa está ativa (memória de estado), o contexto dessa tarefa tem prioridade máxima.
3.  Se nenhuma tarefa está ativa, a memória de fatos é usada para personalizar a conversa geral.

Essa arquitetura de memória dupla permite que o Jarvis seja, ao mesmo tempo, um amigo que te conhece (`memory.py`) e um tutor/gerente de projetos que se lembra do que vocês estão fazendo juntos (`task_manager.py`).

# Análise Técnica: `jarvis.py`

## 1. Visão Geral

O arquivo `jarvis.py` é o **cérebro e o coração** do Projeto Jarvis. Ele define a classe `Jarvis`, que atua como um **orquestrador central (agente)**. Sua responsabilidade não é executar tarefas específicas (como converter fala ou buscar na web), mas sim gerenciar e delegar essas tarefas para os módulos especializados.

Ele recebe um prompt de texto bruto do usuário e, através de um fluxo de decisão lógico, retorna uma resposta de texto final.

## 2. Bibliotecas e Importações Chave

As importações deste arquivo revelam sua função de orquestrador:

-   **`nlp_client.py`**: Para acessar os modelos de linguagem (LLMs) que fazem o "pensamento" real.
-   **`rag.py`**: Para consultar a base de conhecimento local.
-   **`web_search.py`**: Para buscar informações em tempo real na internet.
-   **`memory.py`**: Para acessar a memória de longo prazo (fatos sobre o usuário).
-   **`task_manager.py`**: Para gerenciar o estado de tarefas contínuas.
-   **`sentiment.py`**: Para analisar o tom emocional do prompt do usuário.
-   **`commands.py`**: Para interpretar se a resposta final é um comando a ser executado.

## 3. Análise das Partes Principais

### a) O Método `__init__`

O construtor da classe `Jarvis` inicializa uma instância de cada um dos módulos de serviço. Isso significa que, quando o Jarvis "nasce", ele já tem acesso a todas as suas capacidades (memória, RAG, etc.) e está pronto para usá-las.

### b) O Método `interact(prompt: str)`

Este é o método mais importante do projeto. Ele define a "cadeia de pensamento" (Chain of Thought) do Jarvis. O fluxo atual é projetado para ser eficiente e preciso:

1.  **Aprender (`_learn_from_interaction`)**: A primeira ação é sempre analisar o prompt do usuário para extrair e salvar fatos pessoais na memória de longo prazo.
2.  **Decidir a Ferramenta (`decide_on_tool`)**: O Jarvis usa o LLM (Llama 3) para analisar o prompt e o contexto da conversa para tomar uma decisão estratégica. Ele classifica a intenção do usuário em uma de várias categorias: `start_task`, `pause_task`, `resume_task`, `educational_query`, `web_search`, ou `none`.
3.  **Executar Meta-Comandos**: Se a decisão for gerenciar uma tarefa (`start`, `pause`, `resume`), ele executa a ação correspondente no `TaskManager` e gera uma resposta simples, encerrando o fluxo.
4.  **Continuar Tarefa Ativa**: Se uma tarefa já estiver ativa, o Jarvis prioriza o histórico dessa tarefa para contextualizar a conversa, garantindo a continuidade.
5.  **Fluxo Padrão (se nenhuma tarefa estiver ativa)**:
    -   **RAG Primeiro**: Ele primeiro tenta encontrar uma resposta na sua base de conhecimento local (`knowledge/`). Se encontrar um documento com alta relevância, ele o retorna imediatamente. Isso é rápido e garante o uso de informações curadas.
    -   **Busca na Web**: Se o RAG falhar e a decisão for `web_search`, ele executa a busca, constrói um prompt focado nos resultados e gera a resposta.
    -   **Resposta Educacional**: Se a decisão for `educational_query`, ele chama o modelo especialista (Phi-3) para uma explicação didática.
    -   **Conversa Geral**: Se nenhuma das opções acima for acionada, ele trata como uma conversa normal, enriquecendo o prompt com a memória de fatos e a análise de sentimentos.
6.  **Verificar Comandos na Saída**: Antes de retornar a resposta final, ele a analisa com o `CommandHandler` para ver se a resposta do LLM contém uma instrução para o sistema (como "liste os arquivos...").

## 4. Conexões e Motivos

-   **`jarvis.py` é o Hub Central**: Ele se conecta a quase todos os outros módulos `.py`. Ele não *implementa* a lógica, mas *usa* a lógica implementada nos outros módulos.
-   **`jarvis.py` -> `nlp_client.py`**: Esta é a conexão mais crítica. O Jarvis delega todo o "pensamento" pesado (decidir, gerar, extrair fatos) para o `nlp_client`, que por sua vez chama a API do Hugging Face. Isso abstrai a complexidade da interação com a IA.
-   **`jarvis.py` -> `task_manager.py` e `memory.py`**: O Jarvis usa esses dois módulos para construir seu "contexto". O `TaskManager` fornece a memória episódica (o que estamos fazendo agora), e o `LongTermMemory` fornece a memória semântica (quem é o usuário). Juntos, eles permitem que o Jarvis tenha conversas contínuas e personalizadas.
-   **`jarvis.py` -> `rag.py` e `web_search.py`**: Estes são seus "módulos de pesquisa". O Jarvis os usa para buscar informações antes de formular uma resposta, tornando-o mais preciso e atualizado do que um LLM que depende apenas de seu conhecimento pré-treinado.

# Análise Técnica: Módulos de IA (`nlp_client`, `rag`, `sentiment`)

Estes três arquivos formam o núcleo de Inteligência Artificial do Projeto Jarvis. Cada um é especializado em uma tarefa diferente, mas todos seguem o mesmo padrão: encapsular a complexidade da interação com um modelo de IA pré-treinado.

## 1. `nlp_client.py`: O Cérebro Multi-Modelo

### a) Visão Geral

Este é o módulo mais crítico. Ele atua como um cliente universal para interagir com as APIs de Modelos de Linguagem (LLMs). Sua arquitetura é projetada para ser extensível, usando uma **Classe Base Abstrata (`NlpClient`)** que define uma interface comum (`generate`, `extract_facts`, etc.). A implementação concreta (`HuggingFaceHubClient`) lida com os detalhes da API do Hugging Face.

### b) Arquitetura Multi-Modelo

O `HuggingFaceHubClient` gerencia dois modelos diferentes para tarefas distintas, uma abordagem que otimiza a qualidade e a eficiência:

1.  **Modelo Geral (`meta-llama/Meta-Llama-3-8B-Instruct`)**: Usado para a maioria das tarefas de "pensamento":
    -   **Decisão de Ferramenta (`decide_on_tool`)**: Analisa a intenção do usuário e decide a próxima ação (buscar na web, usar o modo educacional, etc.). O Llama 3 é excelente em seguir as instruções complexas deste prompt.
    -   **Conversa Geral (`generate`)**: Mantém o fluxo da conversa, responde a perguntas gerais e sintetiza informações.
    -   **Extração de Fatos (`extract_facts`)**: Analisa o prompt do usuário para extrair fatos para a memória de longo prazo.

2.  **Modelo Educacional (`microsoft/Phi-3-mini-4k-instruct`)**: Usado como um "especialista" chamado sob demanda.
    -   **Geração Educacional (`generate_educational_answer`)**: Quando o Jarvis decide que a pergunta é educacional, ele chama este método. O Phi-3, treinado com dados de alta qualidade ("qualidade de livro didático"), é superior ao Llama 3 para fornecer explicações claras, concisas e didáticas sobre conceitos complexos.

**Motivo da Conexão:** O `jarvis.py` depende inteiramente do `nlp_client.py` para qualquer tarefa que exija raciocínio ou geração de linguagem. Esta abstração é poderosa: se quiséssemos trocar a API do Hugging Face pela do Google ou da OpenAI, precisaríamos apenas criar uma nova classe (ex: `GoogleAIClient`) que implemente a mesma interface, sem alterar nada no `jarvis.py`.

---

## 2. `rag.py`: A Memória Estática (Busca Semântica)

### a) Visão Geral

Este módulo implementa a técnica de **Retrieval-Augmented Generation (RAG)**. Ele transforma uma pasta de documentos de texto (`knowledge/`) em uma base de conhecimento pesquisável, permitindo que o Jarvis responda a perguntas com informações curadas e específicas, reduzindo as "alucinações" do LLM.

### b) Pipeline de Engenharia de Dados (ETL)

O `rag.py` executa um pipeline clássico de Extração, Transformação e Carga:

1.  **Extract**: Lê todos os arquivos `.md` e `.txt` da pasta `knowledge/`.
2.  **Transform**: Usa o modelo `sentence-transformers/all-MiniLM-L6-v2` para converter o conteúdo de cada documento em um **embedding vetorial**. Este vetor é uma representação numérica do *significado* do texto.
3.  **Load (Indexação)**: Armazena todos os embeddings em um tensor do PyTorch (`self.doc_embeddings`), pronto para a busca.

### c) Busca por Similaridade

-   **`answer_with_rag(question)`**: Quando este método é chamado, ele primeiro converte a `question` em um embedding usando o mesmo modelo. Em seguida, ele usa a **similaridade de cosseno** (`util.cos_sim`) para calcular a "distância" semântica entre o vetor da pergunta e os vetores de todos os documentos. Se o documento mais próximo estiver acima de um limiar de similaridade, seu conteúdo é retornado.

**Motivo da Conexão:** O `jarvis.py` chama o `rag.py` no **início** do seu fluxo de interação. Esta é uma decisão de design importante: se a resposta já existe na base de conhecimento local e confiável, o Jarvis a usa imediatamente, evitando chamadas desnecessárias (e mais lentas) para a API do LLM ou para a busca na web.

---

## 3. `sentiment.py`: O Termômetro Emocional

### a) Visão Geral

Este é um módulo especializado que executa uma única tarefa: **análise de sentimentos**. Ele fornece um contexto emocional sobre a entrada do usuário, permitindo que o Jarvis module suas respostas.

### b) Modelo e Processo

-   **Modelo**: Utiliza o `cardiffnlp/twitter-roberta-base-sentiment-latest`, um modelo treinado especificamente para classificar texto como `positivo`, `negativo` ou `neutro`.
-   **Biblioteca**: Usa a função `pipeline` da biblioteca `transformers` do Hugging Face, que é uma abstração de alto nível que simplifica o processo de carregar um modelo e executar inferência com ele.
-   **`analyze(text)`**: Este método recebe o prompt do usuário e retorna uma string simples ("positivo", "negativo" ou "neutro").

**Motivo da Conexão:** O `jarvis.py` usa o `sentiment.py` para enriquecer o prompt que é enviado ao LLM em conversas gerais. Ao informar explicitamente ao LLM "O sentimento do usuário parece ser negativo", ele pode escolher um tom mais empático e cuidadoso em sua resposta, tornando a interação mais humana.

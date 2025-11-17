# Análise Técnica: Módulos de Áudio e Utilitários

Estes arquivos fornecem funcionalidades de suporte essenciais para o Projeto Jarvis, lidando com a conversão de áudio, execução de comandos e busca na web.

## 1. `stt.py`: Speech-to-Text (Voz para Texto)

### a) Visão Geral

Este módulo é o "ouvido" do Jarvis no modo de voz. Sua única responsabilidade é capturar áudio do microfone do usuário e usar um serviço online para transcrevê-lo em texto.

### b) Bibliotecas e Lógica

-   **Biblioteca Principal:** `SpeechRecognition`. Esta é uma biblioteca popular que atua como um wrapper para várias APIs de reconhecimento de fala (Google Web Speech API, Sphinx, etc.).
-   **Configuração do Reconhecedor (`__init__`)**:
    -   `sr.Recognizer()`: Cria uma instância do reconhecedor.
    -   `dynamic_energy_threshold = True`: Esta é uma configuração crucial. Em vez de ter um limiar fixo de "silêncio", o reconhecedor se adapta dinamicamente ao ruído ambiente, tornando-o muito mais robusto para distinguir entre pausas na fala e o fim de uma frase.
    -   `pause_threshold = 2.0`: Define que o sistema deve esperar por 2 segundos de silêncio antes de considerar que o usuário terminou de falar. Isso evita que a gravação seja cortada prematuramente.
-   **Ouvindo (`listen`)**:
    -   `sr.Microphone()`: Abre o microfone padrão do sistema (ou um específico, se `MIC_INDEX` estiver definido) como uma fonte de áudio.
    -   `recognizer.listen(source, ...)`: Grava o áudio da fonte até que uma pausa (definida pelo `pause_threshold`) seja detectada.
    -   `recognizer.recognize_google(...)`: Envia o áudio gravado para a API de reconhecimento de fala da Google e retorna o texto transcrito.
    -   **Tratamento de Erros:** O método lida com exceções comuns, como `WaitTimeoutError` (se nenhum som for detectado) e `UnknownValueError` (se a API não conseguir entender o áudio).

### c) Conexão

-   **`app.py` -> `stt.py`**: A função `run_voice_cli` em `app.py` chama `stt.listen()` para obter o prompt do usuário quando está no modo de voz.

---

## 2. `tts.py`: Text-to-Speech (Texto para Fala)

### a) Visão Geral

Este módulo é a "voz" do Jarvis. Ele recebe uma string de texto e usa um motor de síntese de voz para convertê-la em áudio audível.

### b) Bibliotecas e Lógica

-   **Motores Suportados:** O módulo é projetado para suportar múltiplos motores, selecionáveis através da variável de ambiente `TTS_ENGINE`.
    1.  **`pyttsx3` (Padrão)**: Uma biblioteca que usa as vozes nativas instaladas no sistema operacional (Windows, macOS, Linux). É offline e rápido. O código tenta encontrar e configurar uma voz em português, se disponível.
    2.  **`eSpeak-ng`**: Um motor de síntese de voz de código aberto, conhecido por sua voz robótica e alta inteligibilidade. Ele é chamado como um processo de linha de comando usando a biblioteca `subprocess`.
-   **Lógica de Fallback:** O construtor é robusto. Se o motor `eSpeak-ng` for selecionado mas não for encontrado no sistema, ele automaticamente reverte para o `pyttsx3` para garantir que o Jarvis sempre tenha uma voz.

### c) Conexão

-   **`app.py` -> `tts.py`**: A função `run_voice_cli` em `app.py` chama `tts.speak(response)` para verbalizar a resposta final do Jarvis para o usuário.

---

## 3. `web_search.py`: A Janela para a Internet

### a) Visão Geral

Um módulo simples e focado que fornece a funcionalidade de pesquisa na web em tempo real.

### b) Bibliotecas e Lógica

-   **Biblioteca Principal:** `ddgs` (anteriormente `duckduckgo-search`). Esta biblioteca permite fazer buscas no motor de busca DuckDuckGo sem a necessidade de uma chave de API, tornando-a ideal para projetos de código aberto.
-   **`search_web(query, ...)`**:
    1.  Recebe um `query` de busca.
    2.  Usa `DDGS().text(...)` para executar a busca e obter os resultados.
    3.  **Formatação para o LLM:** Em vez de apenas retornar os links, a função formata os resultados em uma única string de texto legível, incluindo o título, um trecho do conteúdo e a URL de cada fonte. Este passo de pré-processamento é crucial, pois entrega ao LLM um contexto limpo e fácil de sintetizar.

### c) Conexão

-   **`jarvis.py` -> `web_search.py`**: Quando o `jarvis.py` determina (usando o `nlp_client`) que uma busca na web é necessária, ele chama a função `search_web()` com a query de busca apropriada. Os resultados formatados são então inseridos no prompt final enviado ao LLM.

---

## 4. `commands.py`: Executor de Ações

### a) Visão Geral

Este módulo permite que o Jarvis execute ações no sistema do usuário. Ele analisa a resposta final do LLM para ver se ela corresponde a um padrão de comando predefinido.

### b) Lógica Atual

-   **Comando Implementado:** Atualmente, ele implementa um único comando de exemplo: "liste os arquivos em [caminho]".
-   **Análise Simples:** Ele usa uma verificação de string simples (`if "liste os arquivos em" in response_lower:`).
-   **Modo de Segurança (`SAFE_MODE`)**: Antes de executar um comando que interage com o sistema de arquivos, ele verifica a variável de ambiente `SAFE_MODE`. Se estiver ativa, ele pede confirmação ao usuário no terminal, como uma medida de segurança para evitar ações inesperadas.

### c) Conexão

-   **`jarvis.py` -> `commands.py`**: Esta é a **última etapa** no fluxo de `interact`. Após o LLM gerar uma resposta, o `jarvis.py` a passa para o `command_handler.handle()`. Se a função retornar um resultado (ou seja, um comando foi executado), esse resultado é retornado ao usuário. Caso contrário, a resposta original do LLM é retornada. Isso permite que o Jarvis responda "Aqui estão os arquivos..." em vez de apenas gerar a frase "Ok, vou listar os arquivos...".

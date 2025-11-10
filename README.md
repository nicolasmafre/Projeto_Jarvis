# Projeto Jarvis - Assistente de Linguagem Natural

Este projeto implementa um assistente de linguagem natural multifacetado, inspirado no Jarvis. Ele combina um poderoso modelo de linguagem (LLM) com uma base de conhecimento local, memória de longo prazo e múltiplas interfaces de usuário, incluindo CLI, Web e uma GUI de desktop.

![Jarvis GUI Screenshot](https://i.imgur.com/your-screenshot-url.png) <!-- Adicione um screenshot da sua GUI aqui! -->

## Estrutura do Projeto

```
Projeto_Jarvis/
├── .env.example              # Exemplo de arquivo de configuração de ambiente
├── .gitignore                # Arquivos e pastas a serem ignorados pelo Git
├── README.md                 # Este arquivo
├── app.py                    # Ponto de entrada para as interfaces CLI e Web (Flask)
├── check_mics.py             # Script para listar microfones disponíveis (Linux)
├── commands.py               # Módulo para lidar com comandos específicos
├── environment.yml           # Arquivo de ambiente para Conda
├── examples/                 # Scripts de exemplo para demonstrar funcionalidades
│   ├── demo_api_client.py
│   ├── demo_cli_programmatic.py
│   └── demo_rag.py
├── gui_app.py                # Ponto de entrada para a Interface Gráfica (Flet)
├── iniciar_jarvis.bat        # Script de inicialização para Windows
├── jarvis.py                 # Lógica central do assistente
├── knowledge/                # Pasta para a base de conhecimento estático (RAG)
│   ├── ... (seus arquivos .md ou .txt)
├── memory/                   # Pasta para a memória de longo prazo
│   └── memory.json
├── minimal_mic_test.py       # Script para testes isolados do microfone
├── nlp_client.py             # Cliente para interagir com a API do LLM
├── rag.py                    # Lógica do Retrieval-Augmented Generation
├── requirements.txt          # Lista de dependências para pip
├── stt.py                    # Módulo de Speech-to-Text
├── templates/                # Templates HTML para a interface web
│   └── index.html
├── tests/                    # Testes unitários
│   ├── test_commands.py
│   ├── test_nlp_client.py
│   └── ...
└── tts.py                    # Módulo de Text-to-Speech
```

## Funcionalidades Principais

- **Integração com LLM Moderno:** Utiliza a biblioteca `huggingface-hub` para uma integração robusta com modelos de ponta.
- **RAG com Busca Semântica:** Usa `sentence-transformers` para uma busca por significado nos seus documentos locais, garantindo respostas precisas.
- **Memória de Longo Prazo:** O Jarvis aprende com suas conversas, armazenando fatos em `memory/memory.json` para personalizar interações futuras.
- **Múltiplas Interfaces:**
  - **GUI de Desktop:** Uma interface gráfica moderna e bonita construída com **Flet**.
  - **CLI (Voz e Texto):** Um assistente de voz completo no terminal, com ativação de microfone sob demanda e uma opção de modo texto.
  - **Web:** Uma interface de chat simples e reativa, construída com Flask e HTMX.
- **Configuração Automática de Microfone (Linux):** Tenta desmutar e ajustar o volume do microfone padrão ao iniciar o modo de voz.
- **Opções de Voz (TTS):** Suporte para as vozes nativas do sistema (`pyttsx3`) e para o motor offline `eSpeak-ng`.

---

## Guia de Instalação e Configuração

Siga estes passos **cuidadosamente** para garantir que o assistente funcione corretamente.

### Passo 1: Clonar o Repositório

```bash
git clone https://github.com/nicolasmafre/Projeto_Jarvis.git
cd Projeto_Jarvis
```

### Passo 2: Criar Ambiente e Instalar Dependências

**Opção A: Usando Conda (Recomendado)**

```bash
# Cria o ambiente a partir do arquivo de configuração
conda env create -f environment.yml

# Ativa o ambiente
conda activate Projeto_Jarvis
```

**Opção B: Usando venv e pip**

```bash
# Crie um ambiente virtual
python -m venv venv

# Ative o ambiente
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instale as bibliotecas necessárias
pip install -r requirements.txt
```

**Nota Importante para Usuários Linux (Ubuntu/Debian):**
Para garantir que o reconhecimento de voz e a interface gráfica funcionem corretamente, instale os seguintes pacotes de sistema:
```bash
sudo apt-get update && sudo apt-get install -y libasound2-plugins libasound2-dev pulseaudio-utils libmpv-dev
```

### Passo 3: Configurar a Chave de API do Hugging Face

1.  **Acesse:** [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens).
2.  **Crie um Novo Token:** Dê um nome, selecione a permissão **`write`**, e garanta que não tenha data de expiração.
3.  **Copie o Token** (começa com `hf_...`).
4.  **Crie e Edite o Arquivo `.env`:**
    - Copie o arquivo de exemplo: `cp .env.example .env`
    - Abra o `.env` e cole sua chave na variável `HF_TOKEN`.

### Passo 4: Aceitar os Termos de Uso do Modelo

Para usar o Llama 3 (ou outros modelos restritos), você precisa aceitar seus termos de uso na página do modelo no Hugging Face.

---

## Como Executar

Certifique-se de que seu ambiente (`conda` ou `venv`) esteja ativado.

### 1. Interface Gráfica (GUI) - Recomendado

Para a melhor experiência visual, execute a aplicação Flet:

```bash
python gui_app.py
```

### 2. CLI Interativo (Voz ou Texto)

Para usar o Jarvis no terminal:

```bash
python app.py
```

O programa irá perguntar se você deseja usar o modo de **Voz** ou **Texto**.

- **Modo Voz:** Pressione **Enter** para ativar o microfone e falar.
- **Modo Texto:** Interaja digitando normalmente.

### 3. Interface Web (Texto)

Para iniciar a interface de chat web:

```bash
python app.py --web
```

Acesse `http://127.0.0.1:5000` no seu navegador.

---

## Solução de Problemas (Troubleshooting)

### Erro `libmpv.so.1: cannot open shared object file` ao iniciar a GUI no Linux

Este erro ocorre porque a biblioteca Flet precisa da biblioteca de mídia `libmpv`, mas não a encontra.

**Solução:** Instale o pacote de desenvolvimento `libmpv-dev`, que geralmente resolve o problema para múltiplas versões.

```bash
sudo apt-get install -y libmpv-dev
```

Se o erro persistir, pode ser necessário criar um link simbólico. Primeiro, instale a `libmpv2` e depois crie um link para a `libmpv.so.1`:

```bash
# 1. Instale a libmpv2
sudo apt-get install -y libmpv2

# 2. Encontre o caminho da biblioteca instalada
find /usr/lib -name "libmpv.so.2"
# Exemplo de saída: /usr/lib/x86_64-linux-gnu/libmpv.so.2

# 3. Crie o link simbólico (substitua pelo caminho que você encontrou)
sudo ln -s /usr/lib/x86_64-linux-gnu/libmpv.so.2 /usr/lib/x86_64-linux-gnu/libmpv.so.1
```

### Microfone não funciona no Linux (Ubuntu)

Se o modo de voz não capturar seu áudio:

**Passo 1: Verifique o Índice do Dispositivo**
1.  Execute `python check_mics.py`.
2.  Anote o índice do seu microfone principal.
3.  Abra seu arquivo `.env` e defina a variável `MIC_INDEX` com o número. Ex: `MIC_INDEX=2`.

**Passo 2: Use o `pavucontrol` para Ajustes Manuais**
1.  Execute `pavucontrol` no terminal.
2.  Vá para a aba **"Dispositivos de entrada"** e verifique se o microfone correto não está mudo e se o volume está adequado.

---

## Executando os Testes

O projeto inclui uma suíte de testes unitários para garantir a funcionalidade e a estabilidade de cada módulo. Os testes são escritos usando a biblioteca `pytest`.

Para executá-los:

1.  Certifique-se de que seu ambiente (`conda` ou `venv`) esteja ativado.
2.  Na pasta raiz do projeto, execute o comando `pytest`:

    ```bash
    pytest
    ```

    Para uma saída mais detalhada, que lista cada teste individualmente, use o modo "verbose":

    ```bash
    pytest -v
    ```

O `pytest` irá automaticamente descobrir e executar todos os arquivos na pasta `tests/` que começam com `test_`, e então exibirá um relatório de quais testes passaram e quais falharam.

---

## 🚨 Segurança e Git: Não Envie Seus Segredos! 🚨

O arquivo **`.gitignore`** está configurado para ignorar o arquivo `.env`. Isso é uma proteção vital para impedir que sua chave de API seja enviada para o GitHub. **Nunca** remova o `.env` do `.gitignore`.

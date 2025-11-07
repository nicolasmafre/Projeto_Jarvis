# Projeto Jarvis - Assistente de Linguagem Natural

Este projeto implementa um assistente de linguagem natural inspirado no Jarvis, utilizando a API de Inferência do Hugging Face para acesso a modelos de linguagem de ponta como o Llama 3 da Meta.

## Funcionalidades Principais

- **Integração com LLM Moderno:** Utiliza a biblioteca `huggingface-hub` para uma integração robusta e em tempo real com os modelos de inferência.
- **Modelo de Chat:** Pré-configurado para usar o `meta-llama/Meta-Llama-3-8B-Instruct`.
- **Cliente de API Genérico:** Suporte a múltiplos provedores (Hugging Face, Replicate) com seleção via variável de ambiente.
- **RAG (Retrieval-Augmented Generation):** Indexa documentos locais para responder perguntas com base em conhecimento específico.
- **Interação por Voz:** A interface CLI utiliza reconhecimento de fala (STT) e síntese de voz (TTS) para uma experiência de assistente de voz completa.
- **Opções de Voz (TTS):** Suporte para as vozes nativas do sistema operacional (via `pyttsx3`) e para o motor de voz offline `eSpeak-ng`.
- **Interfaces Duplas:** Funciona como um assistente de voz no terminal (CLI) ou como uma aplicação de chat web via Flask e HTMX.
- **Segurança:** Inclui um modo "safe" que exige confirmação do usuário para ações sensíveis.

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

O Conda facilita a instalação de dependências complexas como a `PyAudio`.

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

### Passo 3: Configurar a Chave de API do Hugging Face

Este é o passo mais crítico.

1.  **Acesse as Configurações de Token:** Vá para [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens).
2.  **Crie um Novo Token:**
    - Dê um nome ao token (ex: `jarvis-project`).
    - No campo **"Role"**, selecione a permissão **`write`**. A permissão `read` não é suficiente.
    - Garanta que o token não tenha data de expiração.
3.  **Copie o Token** (começa com `hf_...`).
4.  **Crie e Edite o Arquivo `.env`:**
    - No seu terminal, copie o arquivo de exemplo: `cp .env.example .env`
    - Abra o novo arquivo `.env` e cole a sua chave na variável `HF_TOKEN`.

### Passo 4: Aceitar os Termos de Uso do Modelo

Para usar o Llama 3, você precisa aceitar seus termos de uso.

1.  Vá para a página do modelo: [meta-llama/Meta-Llama-3-8B-Instruct](https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct).
2.  Faça login com a mesma conta da sua chave de API.
3.  Clique nos botões para aceitar os termos.

### Passo 5 (Opcional): Configurar a Voz do Jarvis (TTS)

Por padrão, o Jarvis usa as vozes nativas do seu sistema operacional (`pyttsx3`). Você pode optar por usar a voz robótica e offline do `eSpeak-ng`.

1.  **Instale o eSpeak-ng no seu sistema:**
    - **Linux (Debian/Ubuntu):** `sudo apt-get update && sudo apt-get install espeak-ng`
    - **macOS (com Homebrew):** `brew install espeak-ng`
    - **Windows:** Baixe e execute o instalador a partir do [site oficial do eSpeak-ng](https://espeak-ng.sourceforge.io/download.html). Certifique-se de que ele seja adicionado ao PATH do sistema.

2.  **Configure o `.env`:**
    - Abra seu arquivo `.env` e altere a variável `TTS_ENGINE`:
      ```env
      TTS_ENGINE=espeak-ng
      ```

---

## Como Executar

Certifique-se de que seu ambiente (`conda` ou `venv`) esteja ativado.

### CLI Interativo (com Voz)

Para conversar com o Jarvis usando seu microfone e alto-falantes:

```bash
python app.py
```

### Interface Web (com Texto)

Para iniciar a interface de chat web:

```bash
python app.py --web
```

Acesse `http://127.0.0.1:5000` no seu navegador.

---

## 🚨 Segurança e Git: Não Envie Seus Segredos! 🚨

O arquivo **`.gitignore`** está configurado para ignorar o arquivo `.env`. Isso é uma proteção vital para impedir que sua chave de API seja enviada para o GitHub. **Nunca** remova o `.env` do `.gitignore`.

# Projeto Jarvis - Assistente de Linguagem Natural

Este projeto implementa um assistente de linguagem natural multifacetado, inspirado no Jarvis. Ele combina um poderoso modelo de linguagem (Meta Llama 3) com uma base de conhecimento local, memória de longo prazo e interação por voz.

## Funcionalidades Principais

- **Integração com LLM Moderno:** Utiliza a biblioteca `huggingface-hub` para uma integração robusta e em tempo real com o modelo `meta-llama/Meta-Llama-3-8B-Instruct`.
- **Memória de Longo Prazo:** O Jarvis aprende com suas conversas! Ele extrai fatos e preferências importantes, armazenando-os em `memory/memory.json` para personalizar interações futuras.
- **RAG (Retrieval-Augmented Generation):** Possui uma "memória estática" que indexa documentos locais (na pasta `knowledge/`) para responder a perguntas com conhecimento especializado que você fornece.
- **Interação por Voz Sob Demanda:** A interface CLI ativa o microfone apenas quando o usuário pressiona Enter, garantindo privacidade e controle total.
- **Opções de Voz (TTS):** Suporte para as vozes nativas do sistema operacional (via `pyttsx3`) e para o motor de voz offline `eSpeak-ng`, selecionável via variável de ambiente.
- **Interfaces Duplas:**
  - **CLI:** Um assistente de voz completo no terminal, com opção de modo texto.
  - **Web:** Uma interface de chat web simples e reativa, construída com Flask e HTMX.
- **Segurança:** Inclui um "modo seguro" que exige confirmação do usuário para ações sensíveis e um `.gitignore` robusto para prevenir o vazamento de segredos.
- **Suíte de Testes:** Acompanha uma suíte de testes unitários (`pytest`) para garantir a estabilidade e a funcionalidade de cada módulo.

---

## Guia de Instalação e Configuração

Siga estes passos **cuidadosamente** para garantir que o assistente funcione corretamente.

### Passo 1: Clonar o Repositório

```bash
git clone https://github.com/nicolasmafre/Projeto_Jarvis.git
cd Projeto_Jarvis
```

### Passo 2: Criar Ambiente e Instalar Dependências

**Opção A: Usando Conda (Recomendado para Linux e Windows)**

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

**Nota Importante para Usuários Linux (Ubuntu/Debian):**
Para garantir que o reconhecimento de voz funcione, é altamente recomendável instalar pacotes de desenvolvimento e plugins de áudio no seu sistema:
```bash
sudo apt-get update && sudo apt-get install -y libasound2-plugins libasound2-dev pavucontrol
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

---

## Como Executar

Certifique-se de que seu ambiente (`conda` ou `venv`) esteja ativado.

### CLI Interativo (com Voz ou Texto)

Execute o comando principal para iniciar o assistente:

```bash
python app.py
```

O programa irá perguntar se você deseja usar o modo de **Voz** ou **Texto**.

- **Modo Voz:** Pressione **Enter** para ativar o microfone e falar. A luz do seu microfone só acenderá quando o Jarvis estiver ouvindo.
- **Modo Texto:** Interaja digitando normalmente no terminal.

### Interface Web (com Texto)

Para iniciar a interface de chat web:

```bash
python app.py --web
```

Acesse `http://127.0.0.1:5000` no seu navegador.

---

## Configurações Avançadas (Arquivo `.env`)

Você pode personalizar o comportamento do Jarvis editando seu arquivo `.env`:

- `TTS_ENGINE`: Mude de `pyttsx3` (padrão) para `espeak-ng` para usar uma voz robótica offline. Requer a instalação do `eSpeak-ng` no seu sistema.
- `MIC_INDEX`: (Principalmente para Linux) Se o microfone padrão não funcionar, use o script `python check_mics.py` para encontrar o índice do seu dispositivo e defina-o aqui.

---

## Solução de Problemas (Troubleshooting)

### Microfone não funciona no Linux (Ubuntu)

Se o modo de voz não capturar seu áudio, siga estes passos:

**Passo 1: Use o PulseAudio Volume Control (`pavucontrol`)**

Esta ferramenta, que você instalou no Passo 2, oferece um controle mais detalhado.

```bash
# Execute a ferramenta
pavucontrol
```

**Passo 2: Verifique as Configurações do Microfone**

1.  Na janela do `pavucontrol`, vá para a aba **"Dispositivos de entrada"**.
2.  Encontre o seu microfone na lista.
3.  **Verifique 3 coisas:**
    - **Mudo:** O ícone de mudo (alto-falante com um X) **não** deve estar selecionado.
    - **Volume:** A barra de volume **não** deve estar em 0%. Aumente para 70-100%.
    - **Seleção de Porta:** Se houver um menu "Porta", certifique-se de que "Microfone" está selecionado.

**Passo 3: Verifique o Índice do Dispositivo**

Se o problema persistir, você pode estar usando o índice de dispositivo errado.

1.  Execute o script de verificação: `python check_mics.py`.
2.  Identifique o índice do seu microfone principal na lista.
3.  Abra seu arquivo `.env` e defina a variável `MIC_INDEX` com o número correto. Ex: `MIC_INDEX=2`.

---

## Executando os Testes

O projeto inclui uma suíte de testes unitários para garantir a funcionalidade e a estabilidade.

1.  Certifique-se de que seu ambiente (`conda` ou `venv`) esteja ativado.
2.  Na pasta raiz do projeto, execute o `pytest`:

    ```bash
    pytest
    ```

    Para uma saída mais detalhada, use: `pytest -v`

---

## 🚨 Segurança e Git: Não Envie Seus Segredos! 🚨

O arquivo **`.gitignore`** está configurado para ignorar o arquivo `.env`. Isso é uma proteção vital para impedir que sua chave de API seja enviada para o GitHub. **Nunca** remova o `.env` do `.gitignore`.

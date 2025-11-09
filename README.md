# Projeto Jarvis - Assistente de Linguagem Natural

Este projeto implementa um assistente de linguagem natural multifacetado, inspirado no Jarvis. Ele combina um poderoso modelo de linguagem (Meta Llama 3) com uma base de conhecimento local, memória de longo prazo e interação por voz.

## Funcionalidades Principais

- **Integração com LLM Moderno:** Utiliza a biblioteca `huggingface-hub` para uma integração robusta e em tempo real com o modelo `meta-llama/Meta-Llama-3-8B-Instruct`.
- **RAG com Busca Semântica:** A funcionalidade de Retrieval-Augmented Generation foi aprimorada para usar o modelo `all-MiniLM-L6-v2` da `Sentence-Transformers`. Isso substitui a busca por palavras-chave (TF-IDF) por uma **busca por significado**, resultando em respostas muito mais precisas e contextuais com base nos seus documentos.
- **Memória de Longo Prazo:** O Jarvis aprende com suas conversas! Ele extrai fatos e preferências importantes, armazenando-os em `memory/memory.json` para personalizar interações futuras.
- **Interação por Voz Sob Demanda:** A interface CLI ativa o microfone apenas quando o usuário pressiona Enter, garantindo privacidade e controle total.
- **Gerenciador de Áudio (Linux):** Ao iniciar o modo de voz no Linux, o Jarvis abre automaticamente o `pavucontrol` (PulseAudio Volume Control) para facilitar o ajuste do microfone. A janela é fechada ao sair.
- **Opções de Voz (TTS):** Suporte para as vozes nativas do sistema operacional (via `pyttsx3`) e para o motor de voz offline `eSpeak-ng`.
- **Interfaces Duplas:**
  - **CLI:** Um assistente de voz completo no terminal, com opção de modo texto.
  - **Web:** Uma interface de chat web simples e reativa, construída com Flask e HTMX.
- **Segurança:** Inclui um "modo seguro" que exige confirmação do usuário para ações sensíveis.
- **Suíte de Testes:** Acompanha uma suíte de testes unitários (`pytest`) para garantir a estabilidade e a funcionalidade de cada módulo.

---

## Guia de Instalação e Configuração

Siga estes passos **cuidadosamente** para garantir que o assistente funcione corretamente.

### Passo 1: Clonar o Repositório
...

### Passo 2: Criar Ambiente e Instalar Dependências

**Opção A: Usando Conda (Recomendado)**

O Conda facilita a instalação de dependências complexas como `PyAudio` e `PyTorch`.

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
...
---

## Alimentando a Base de Conhecimento (RAG)

O Jarvis possui uma funcionalidade de **RAG (Retrieval-Augmented Generation)** que agora utiliza busca semântica para responder perguntas com base em seus próprios documentos.

**Como funciona:**
1.  Você coloca arquivos de texto (`.txt`, `.md`) dentro da pasta `knowledge/`.
2.  Ao iniciar, o Jarvis usa o modelo `all-MiniLM-L6-v2` para converter seus documentos em vetores numéricos (embeddings) que representam seu significado.
3.  Quando você faz uma pergunta, o Jarvis converte sua pergunta em um vetor e busca o documento com o significado mais próximo em sua base de conhecimento.
4.  Se a similaridade for alta, ele usa esse documento para formular a resposta.

Esta funcionalidade é extremamente poderosa para personalizar o conhecimento do Jarvis, permitindo que ele entenda o contexto e a intenção, em vez de apenas combinar palavras-chave.

...

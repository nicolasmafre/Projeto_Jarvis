# Guia de Estudo e Recursos do Projeto Jarvis

Este guia foi criado para ajudar desenvolvedores e entusiastas a aprofundar seus conhecimentos nas tecnologias e conceitos utilizados no Projeto Jarvis.

## 1. Conceitos Fundamentais de IA e Python

Para entender a base do projeto, é essencial ter um bom domínio de Python e dos conceitos de IA.

- **Livro: "Python Fluente" por Luciano Ramalho**
    - **Link:** [Amazon](https://www.amazon.com.br/Python-Fluente-Luciano-Ramalho/dp/8575224622)
    - **Por que é útil:** Não é um livro para iniciantes, mas é o melhor guia para escrever código Python idiomático e eficiente. Essencial para entender as estruturas de dados e as classes usadas no projeto.

- **Livro: "Inteligência Artificial: Uma Abordagem Moderna" por Stuart Russell e Peter Norvig**
    - **Link:** [Amazon](https://www.amazon.com.br/Intelig%C3%AAncia-Artificial-Abordagem-Moderna-Russell/dp/8543008233)
    - **Por que é útil:** É a "bíblia" da Inteligência Artificial. Embora denso, ele cobre todos os fundamentos teóricos, desde agentes inteligentes até aprendizado de máquina e processamento de linguagem natural.

## 2. Processamento de Linguagem Natural (PLN) e LLMs

Esta é a área central do Jarvis.

- **Curso: "Natural Language Processing Specialization" por DeepLearning.AI (Coursera)**
    - **Link:** [Coursera](https://www.coursera.org/specializations/natural-language-processing)
    - **Por que é útil:** Uma das melhores especializações online, cobre desde o básico (modelos probabilísticos) até redes neurais, RNNs, LSTMs e Transformers. Perfeito para entender o que acontece dentro dos modelos.

- **Artigo/Blog: "The Illustrated Transformer" por Jay Alammar**
    - **Link:** [The Illustrated Transformer](https://jalammar.github.io/illustrated-transformer/)
    - **Por que é útil:** Uma explicação visual e intuitiva da arquitetura "Transformer", que é a base de todos os LLMs modernos como Llama, GPT e Mixtral. Leitura obrigatória.

- **Documentação: Hugging Face - The Hub for Machine Learning**
    - **Link:** [Hugging Face Docs](https://huggingface.co/docs)
    - **Por que é útil:** O projeto depende inteiramente do ecossistema Hugging Face. Navegar pela documentação das bibliotecas `transformers`, `huggingface_hub` e `sentence-transformers` é a melhor forma de entender como os modelos são carregados e utilizados.

## 3. Retrieval-Augmented Generation (RAG) e Busca Semântica

Para entender como o Jarvis usa a pasta `knowledge/`.

- **Artigo: "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" (Paper Original)**
    - **Link:** [arXiv](https://arxiv.org/abs/2005.11401)
    - **Por que é útil:** Para os mais acadêmicos, este é o paper que popularizou a técnica de RAG. Ele explica a motivação e a arquitetura por trás da ideia de combinar busca de informações com geração de texto.

- **Blog: "What is Retrieval-Augmented Generation?" pela NVIDIA**
    - **Link:** [NVIDIA Blog](https://blogs.nvidia.com/blog/what-is-retrieval-augmented-generation/)
    - **Por que é útil:** Uma explicação mais acessível e focada na indústria sobre o que é RAG e por que é tão importante para reduzir "alucinações" e usar dados privados.

- **Documentação: `sentence-transformers`**
    - **Link:** [sbert.net](https://www.sbert.net/)
    - **Por que é útil:** Explica em detalhes como usar a biblioteca para criar embeddings e, mais importante, como calcular a **similaridade de cosseno** (`util.cos_sim`), que é a operação matemática no coração do nosso `rag.py`.

## 4. Desenvolvimento de Interfaces (GUI e Web)

Para entender os arquivos `gui_app.py` e `app.py`.

- **Documentação: Flet - Build Flutter apps in Python**
    - **Link:** [Flet Docs](https://flet.dev/docs/)
    - **Por que é útil:** A documentação oficial do Flet é excelente, cheia de exemplos. É o melhor lugar para entender os componentes (`ft.Row`, `ft.TextField`, etc.) e, crucialmente, o conceito de **atualização da UI a partir de threads secundárias**, que é a parte mais complexa do `gui_app.py`.

- **Tutorial: "Flask Official Tutorial"**
    - **Link:** [Flask Docs](https://flask.palletsprojects.com/en/3.0.x/tutorial/)
    - **Por que é útil:** O tutorial oficial do Flask ensina os conceitos de rotas (`@app.route`), requisições e templates, que são a base da nossa interface web em `app.py`.

- **Documentação: HTMX - High Power Tools for HTML**
    - **Link:** [HTMX Docs](https://htmx.org/docs/)
    - **Por que é útil:** Para entender como a interface web em `templates/index.html` consegue ser dinâmica sem escrever JavaScript. A documentação explica os atributos `hx-post`, `hx-target`, etc.

## 5. Áudio em Python (STT e TTS)

Para entender os arquivos `stt.py` e `tts.py`.

- **Documentação: `SpeechRecognition`**
    - **Link:** [PyPI - SpeechRecognition](https://pypi.org/project/SpeechRecognition/)
    - **Por que é útil:** A página da biblioteca no PyPI tem uma documentação completa e com exemplos de como usar o `Recognizer`, o `Microphone`, e como tratar as exceções (`UnknownValueError`, `RequestError`), exatamente como fazemos no `stt.py`.

- **Documentação: `pyttsx3`**
    - **Link:** [pyttsx3 Docs](https://pyttsx3.readthedocs.io/en/latest/)
    - **Por que é útil:** Explica como inicializar o motor (`pyttsx3.init()`), mudar propriedades como a voz e a velocidade, e usar os métodos `say()` e `runAndWait()`.

- **Artigo/Fórum: "Why is PyAudio so painful to install?"**
    - **Link:** Uma busca por este termo no Google ou Stack Overflow.
    - **Por que é útil:** Não é um link específico, mas pesquisar sobre os problemas de instalação do `PyAudio` ajuda a entender por que ele depende de bibliotecas de sistema (`portaudio`, `libasound2-dev`) e por que o Conda ou a instalação manual dessas dependências é frequentemente necessária, especialmente no Linux e Windows.

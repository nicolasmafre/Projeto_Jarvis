"""
Módulo de Análise de Sentimentos.

Este módulo é responsável por analisar o sentimento de um texto,
classificando-o como positivo, negativo ou neutro.
"""

from transformers import pipeline

class SentimentAnalyzer:
    """
    Analisa o sentimento de um texto usando um modelo pré-treinado.
    """
    def __init__(self, model_name="cardiffnlp/twitter-roberta-base-sentiment-latest"):
        """
        Inicializa o analisador de sentimentos, carregando o modelo.

        Args:
            model_name (str): O nome do modelo a ser usado do Hugging Face Hub.
        """
        print("[Sentimento] Carregando o modelo de análise de sentimentos...")
        try:
            # Usamos a biblioteca 'transformers' diretamente para este tipo de modelo
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model=model_name,
                device=-1 # -1 para CPU, 0 para GPU (se disponível e configurada)
            )
            print("[Sentimento] Modelo carregado com sucesso.")
        except Exception as e:
            print(f"ERRO [Sentimento]: Falha ao carregar o modelo: {e}")
            print("Pode ser necessário instalar dependências adicionais: pip install torch torchvision torchaudio")
            self.sentiment_pipeline = None

    def analyze(self, text: str) -> str:
        """
        Analisa o sentimento de um texto.

        Args:
            text (str): O texto a ser analisado.

        Returns:
            str: O sentimento detectado ('positivo', 'negativo', 'neutro').
        """
        if not self.sentiment_pipeline or not text:
            return "neutro" # Retorna neutro se o modelo não carregou ou o texto é vazio

        try:
            result = self.sentiment_pipeline(text)
            # O modelo retorna 'positive', 'negative', ou 'neutral'.
            # Vamos traduzir para português para consistência.
            label = result[0]['label'].lower()
            if label == 'positive':
                return 'positivo'
            elif label == 'negative':
                return 'negativo'
            else:
                return 'neutro'
        except Exception as e:
            print(f"ERRO [Sentimento]: Falha ao analisar o texto: {e}")
            return "neutro" # Retorna neutro em caso de erro

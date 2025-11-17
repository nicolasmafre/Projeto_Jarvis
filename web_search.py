"""
Módulo para realizar pesquisas na web usando DuckDuckGo.
"""

# Usa a nova biblioteca 'ddgs' para evitar o RuntimeWarning
from ddgs import DDGS

def search_web(query: str, max_results: int = 3) -> str:
    """
    Realiza uma pesquisa na web e retorna os resultados formatados.
    """
    print(f"[WebSearch] Buscando por: '{query}'...")
    try:
        # A sintaxe para usar a biblioteca ddgs é a mesma
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        
        if not results:
            print("[WebSearch] Nenhum resultado encontrado.")
            return "Nenhum resultado encontrado na web para esta consulta."

        formatted_results = "Resultados da pesquisa na web:\n\n"
        for i, result in enumerate(results, 1):
            formatted_results += f"--- Fonte {i} ---\n"
            formatted_results += f"Título: {result.get('title', 'N/A')}\n"
            formatted_results += f"Trecho: {result.get('body', 'N/A')}\n"
            formatted_results += f"URL: {result.get('href', 'N/A')}\n\n"
        
        print(f"[WebSearch] {len(results)} resultados encontrados.")
        return formatted_results

    except Exception as e:
        print(f"ERRO [WebSearch]: Falha ao executar a busca: {e}")
        return f"Erro ao realizar a pesquisa na web: {e}"

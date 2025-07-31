from sqlalchemy import text
from database import get_session
from forecasting.forecasting_service import executar_previsao_completa
import os
import requests
import json
import logging

logger = logging.getLogger(__name__)
# Função para gerar o prompt, com base nos dados do usuário
def gerar_prompt_recomendacao(resultados_forecast: dict) -> str:
    """Gera um prompt textual para o Gemini baseado nos dados reais + previsão"""

    try:
        with get_session() as session:
            # Produto mais vendido
            produto_top = session.execute(text("""
                SELECT p.nome
                FROM itens_venda i
                JOIN produtos p ON p.id = i.id_produto
                GROUP BY p.nome
                ORDER BY SUM(i.quantidade) DESC
                LIMIT 1
            """)).scalar() or "Nenhum"

            # Produto com menor margem
            produto_menor_margem = session.execute(text("""
                SELECT nome
                FROM produtos
                WHERE preco_venda > 0
                ORDER BY (preco_venda - preco_compra) ASC
                LIMIT 1
            """)).scalar() or "Nenhum"

            # Médias
            receita_media = session.execute(text("""
                SELECT AVG(valor) FROM transacoes WHERE tipo = 'receita'
            """)).scalar() or 0

            despesa_media = session.execute(text("""
                SELECT AVG(valor) FROM transacoes WHERE tipo = 'despesa'
            """)).scalar() or 0

        # Dados da previsão
        total_previsto = resultados_forecast.get("previsao_total", 0)
        tipo = resultados_forecast.get("tipo", "geral")

        # Montar prompt
        prompt = f"""
Você é um assistente financeiro. Com base nos seguintes dados, forneça até 3 recomendações de negócio claras, objetivas e práticas:

- Receita média diária: R${receita_media:.2f}
- Despesa média diária: R${despesa_media:.2f}
- Produto mais vendido: {produto_top}
- Produto com menor margem de lucro: {produto_menor_margem}
- Previsão total de receita para os próximos 7 dias: R${total_previsto:.2f}

Use frases curtas e diretas para um gestor de pequenas empresas.
Responda em formato de tópicos.
        """.strip()

        return prompt

    except Exception as e:
        logger.error(f"Erro ao gerar prompt de recomendação: {e}")
        return "Não foi possível gerar recomendações no momento."

# Aqui faz a chamada para a API e retorna um text
def consultar_gemini(prompt: str) -> str:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"

    body = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    response = requests.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(body))
    data = response.json()

    texto = (
        data.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", " Nenhuma recomendação gerada.")
    )

    return texto.strip()

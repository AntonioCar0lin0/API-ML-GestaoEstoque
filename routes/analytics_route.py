# Define as rotas sobre análise e previsão
# Usa os dados das transações, aplica modelos ARIMA/SARIMA e retorna um JSON 
from fastapi import APIRouter, Query
from forecasting.forecasting_service import carregar_dados_transacao, prever
from forecasting.model_selector import selecionar_melhor_modelo
from forecasting.plot_service import gerar_grafico_forecast_json

router = APIRouter()

@router.get("/grafico-json")
def grafico_json(tipo: str = Query("receita", enum=["receita", "despesa"])):
    try:
        dados = carregar_dados_transacao(tipo)
        modelo, _ = selecionar_melhor_modelo(dados["valor"])
        previsao = prever(modelo, 30)
        return gerar_grafico_forecast_json(dados["valor"], previsao)
    except Exception as e:
        return {"erro": str(e)}


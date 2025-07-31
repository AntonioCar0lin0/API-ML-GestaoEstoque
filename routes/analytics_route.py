# Define as rotas sobre análise e previsão
# Usa os dados das transações, aplica modelos ARIMA/SARIMA e retorna um JSON 
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from forecasting.forecasting_service import carregar_dados_transacao, prever, executar_previsao_completa
from forecasting.model_selector import selecionar_melhor_modelo
from forecasting.plot_service import gerar_grafico_forecast_json
from forecasting.recommendation_service import gerar_prompt_recomendacao, consultar_gemini

router = APIRouter()

# Rota para gráficos de previsão
@router.get("/grafico-json")
def grafico_json(tipo: str = Query("receita", enum=["receita", "despesa"])):
    try:
        dados = carregar_dados_transacao(tipo)
        modelo, _ = selecionar_melhor_modelo(dados["valor"])
        previsao = prever(modelo, 30)
        return JSONResponse(content=gerar_grafico_forecast_json(dados["valor"], previsao))
    except Exception as e:
        return {"erro": str(e)}

# Rota de recomendações para o usuário 
@router.get("/recomendacoes")
def recomendacoes(id_usuario: int):
    resultados = executar_previsao_completa(id_usuario=id_usuario)
    prompt = gerar_prompt_recomendacao(resultados)
    texto = consultar_gemini(prompt)
    return {"recomendacoes": texto}



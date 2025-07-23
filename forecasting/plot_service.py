# Gera o gráfico JSON com série histórica e previsões (data/previsão)
import plotly.graph_objects as go

def gerar_grafico_forecast_json(serie_real, previsao_df):
    trace_real = go.Scatter(
        x=serie_real.index,
        y=serie_real.values,
        mode='lines',
        name='Histórico',
        line=dict(color='blue')
    )

    trace_forecast = go.Scatter(
        x=previsao_df['data'],
        y=previsao_df['previsao'],
        mode='lines',
        name='Previsão',
        line=dict(color='orange', dash='dash')
    )

    layout = {
        "title": "Previsão de Receita/Despesa",
        "xaxis": {"title": "Data"},
        "yaxis": {"title": "Valor"},
        "template": "plotly_white"
    }

    return {
        "data": [trace_real.to_plotly_json(), trace_forecast.to_plotly_json()],
        "layout": layout
    }

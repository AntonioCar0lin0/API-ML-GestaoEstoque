# Gera o gráfico JSON com série histórica e previsões (data/previsao)
import plotly.graph_objects as go

def gerar_grafico_forecast_json(serie_real, previsao_df):
    # Converte tudo para tipos compatíveis com JSON
    trace_real = go.Scatter(
        x=serie_real.index.astype(str).tolist(),  
        y=serie_real.values.tolist(),             
        mode='lines',
        name='Histórico',
        line=dict(color='blue')
    )

    trace_forecast = go.Scatter(
        x=previsao_df['data'].astype(str).tolist(),      
        y=previsao_df['previsao'].tolist(),              
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

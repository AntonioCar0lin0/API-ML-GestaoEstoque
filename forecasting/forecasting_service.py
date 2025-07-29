# Carrega os dados de transação e gera as previsões 
import pandas as pd
from database import engine
from forecasting.model_selector import selecionar_melhor_modelo

def carregar_dados_transacao(tipo: str = None):
    query = "SELECT data, valor FROM transacoes"
    if tipo in ["receita", "despesa"]:
        query += f" WHERE tipo = '{tipo}'"
    
    df = pd.read_sql(query, engine)
    df['data'] = pd.to_datetime(df['data'])
    df = df.groupby('data').sum().asfreq('D').fillna(0)

    df['valor'] = pd.to_numeric(df['valor'], errors='coerce').fillna(0)

    return df


def prever(modelo, periodo: int = 30):
    fitted = modelo.fit()
    previsao = fitted.forecast(steps=periodo)
    ult_data = fitted.data.dates[-1]
    datas = pd.date_range(start=ult_data + pd.Timedelta(days=1), periods=periodo)
    return pd.DataFrame({'data': datas, 'previsao': previsao})


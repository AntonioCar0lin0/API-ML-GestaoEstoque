# forecasting_service.py
import pandas as pd
from sqlalchemy import text
from database import get_session, engine
from forecasting.model_selector import selecionar_melhor_modelo
import logging

logger = logging.getLogger(__name__)

def carregar_dados_transacao(tipo: str = None):
    """Carrega dados de transação do banco usando a conexão correta"""
    try:
        # Constrói a query
        query = "SELECT data, valor FROM transacoes"
        params = {}
        
        if tipo in ["receita", "despesa"]:
            query += " WHERE tipo = :tipo"
            params["tipo"] = tipo
        
        query += " ORDER BY data"
        
        # Usa a sessão do contexto manager
        with get_session() as session:
            # ✅ CORREÇÃO: Usa a conexão da sessão corretamente
            df = pd.read_sql(
                sql=text(query), 
                con=session.connection(),  # Use session.connection() em vez de db.bind
                params=params
            )
            
            if df.empty:
                logger.warning(f"Nenhum dado encontrado para tipo: {tipo}")
                return pd.DataFrame(columns=['data', 'valor'])
            
            # Processa os dados
            df['data'] = pd.to_datetime(df['data'])
            df = df.set_index('data')
            df = df.groupby(df.index.date).sum()  # Agrupa por dia
            df.index = pd.to_datetime(df.index)
            df = df.asfreq('D').fillna(0)  # Preenche dias faltantes
            
            logger.info(f"Carregados {len(df)} registros para {tipo or 'todos os tipos'}")
            return df
            
    except Exception as e:
        logger.error(f"Erro ao carregar dados de transação: {e}")
        return pd.DataFrame(columns=['data', 'valor'])

def carregar_dados_transacao_alternativo(tipo: str = None):
    """Versão alternativa usando engine diretamente"""
    try:
        query = "SELECT data, valor FROM transacoes"
        params = {}
        
        if tipo in ["receita", "despesa"]:
            query += " WHERE tipo = %(tipo)s"
            params["tipo"] = tipo
        
        query += " ORDER BY data"
        
        # ✅ Usa engine diretamente - mais direto para pandas
        df = pd.read_sql(
            sql=query,
            con=engine,  # Engine funciona diretamente com pandas
            params=params
        )
        
        if df.empty:
            logger.warning(f"Nenhum dado encontrado para tipo: {tipo}")
            return pd.DataFrame(columns=['data', 'valor'])
        
        # Processa os dados
        df['data'] = pd.to_datetime(df['data'])
        df = df.set_index('data')
        df = df.groupby(df.index.date).sum()
        df.index = pd.to_datetime(df.index)
        df = df.asfreq('D').fillna(0)
        
        logger.info(f"Carregados {len(df)} registros para {tipo or 'todos os tipos'}")
        return df
        
    except Exception as e:
        logger.error(f"Erro ao carregar dados de transação: {e}")
        return pd.DataFrame(columns=['data', 'valor'])

def prever(modelo, periodo: int = 30):
    try:
        if not hasattr(modelo, 'forecast'):
            raise ValueError("Modelo fornecido não possui método forecast()")

        previsao = modelo.forecast(steps=periodo)

        if hasattr(modelo, 'data') and hasattr(modelo.data, 'dates'):
            ult_data = modelo.data.dates[-1]
        else:
            ult_data = pd.Timestamp.now().normalize()

        datas = pd.date_range(start=ult_data + pd.Timedelta(days=1), periods=periodo)

        return pd.DataFrame({'data': datas, 'previsao': previsao})

    except Exception as e:
        logger.error(f"Erro ao gerar previsão: {e}")
        return pd.DataFrame(columns=['data', 'previsao'])

from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error
import numpy as np

def treinar_arima(serie):
    # Exemplo básico: ordem (1,1,1) - você pode melhorar isso com autoescolha depois
    modelo = ARIMA(serie, order=(1,1,1))
    return modelo

def avaliar_arima(modelo, serie, horizon=15):
    treino = serie[:-horizon]
    teste = serie[-horizon:]

    try:
        fitted = modelo.fit()
        preds = fitted.forecast(steps=horizon)
        rmse = np.sqrt(mean_squared_error(teste, preds))
        return rmse
    except Exception:
        return np.inf

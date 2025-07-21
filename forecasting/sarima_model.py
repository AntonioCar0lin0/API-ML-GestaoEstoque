import pandas as pd
from pmdarima import auto_arima
from sklearn.metrics import mean_squared_error
import numpy as np

def treinar_sarima(serie: pd.Series):
    modelo = auto_arima(serie, seasonal=True, m=7, stepwise=True, suppress_warnings=True)
    return modelo

def avaliar_sarima(modelo, serie: pd.Series, horizon: int = 15):
    treino = serie[:-horizon]
    teste = serie[-horizon:]

    try:
        fitted = modelo.fit(treino)
        preds = fitted.predict(n_periods=horizon)
        rmse = np.sqrt(mean_squared_error(teste, preds))
        return rmse
    except Exception:
        return np.inf

from forecasting.arima_model import treinar_arima, avaliar_arima
from forecasting.sarima_model import treinar_sarima, avaliar_sarima

#  Treina modelos ARIMA e SARIMA e escolhe o melhor com base no RMSE
def selecionar_melhor_modelo(serie):
    arima = treinar_arima(serie)
    sarima = treinar_sarima(serie)

    rmse_arima = avaliar_arima(arima, serie)
    rmse_sarima = avaliar_sarima(sarima, serie)

    if rmse_arima <= rmse_sarima:
        return arima, "ARIMA"
    else:
        return sarima, "SARIMA"

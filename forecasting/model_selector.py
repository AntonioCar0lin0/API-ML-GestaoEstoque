from forecasting.arima_model import treinar_arima, avaliar_arima
from forecasting.sarima_model import treinar_sarima, avaliar_sarima

def selecionar_melhor_modelo(serie):
    arima_model = treinar_arima(serie)
    sarima_model = treinar_sarima(serie)

    rmse_arima = avaliar_arima(arima_model, serie)
    rmse_sarima = avaliar_sarima(sarima_model, serie)

    if rmse_arima <= rmse_sarima:
        melhor_modelo = arima_model.fit()
        return melhor_modelo, "ARIMA"
    else:
        melhor_modelo = sarima_model.fit(disp=False)
        return melhor_modelo, "SARIMA"


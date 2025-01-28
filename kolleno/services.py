import requests


class ExchangeRateException(Exception):
    pass


class ExchangeRateService:
    import requests

    def _get_bitcoin_price_in_eur(self):
        try:
            response = requests.get("https://blockchain.info/ticker")
            response.raise_for_status()
            data = response.json()
            return data["EUR"]["15m"]
        except Exception:
            raise ExchangeRateException("Error fetching BTC-EUR price")

    def _get_eur_to_gbp_rate_from_ecb(self):
        url = "https://sdw-wsrest.ecb.europa.eu/service/data/EXR/M.GBP.EUR.SP00.A?lastNObservations=1"
        try:
            response = requests.get(url, headers={"Accept": "application/json"})
            response.raise_for_status()
            data = response.json()
            observations = data["dataSets"][0]["series"]["0:0:0:0:0"]["observations"]
            latest_observation = list(observations.values())[0][0]
            return float(latest_observation)
        except Exception:
            raise ExchangeRateException("Error fetching EUR→GBP rate from ECB")

    def get_exchange_data(self):
        btc_eur = self._get_bitcoin_price_in_eur()
        eur_to_gbp = self._get_eur_to_gbp_rate_from_ecb()
        btc_gbp = btc_eur * eur_to_gbp

        data_dict = {
            "bitcoin_eur": btc_eur,
            "eur_to_gbp": eur_to_gbp,
            "bitcoin_gbp": btc_gbp,
        }
        return data_dict

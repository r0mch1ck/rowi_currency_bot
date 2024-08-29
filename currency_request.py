import requests


def exchange_rate(currency1, currency2='RUB', api_key=None):
    """
        This function retrieves the exchange rate between two currencies using the ExchangeRate-API.

        Parameters:
        currency1 (str): The base currency for the exchange rate.
        currency2 (str): The target currency for the exchange rate. Default is 'RUB'.
        api_key (str): The API key for the ExchangeRate-API. If not provided, the function will use the default key.

        Returns:
        tuple: A tuple containing the exchange rate and the time of the last update in UTC.
               If the request fails, the function will return (None, None).
        """
    request = requests.get(f'https://v6.exchangerate-api.com/v6/{api_key}/pair/{currency1}/{currency2}')
    if request.status_code == 200:
        request = request.json()
        return request['conversion_rate'], request['time_last_update_utc']
    else:
        return None, None
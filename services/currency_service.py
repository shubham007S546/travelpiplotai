"""Live Currency Exchange Service using Frankfurter (Free & No Key Required)."""

import requests
from services.base_provider import BaseCurrencyProvider
from utils.caching import api_cache
from utils.logging import logger


class FrankfurterCurrencyService(BaseCurrencyProvider):
    """Real-time foreign exchange converter via frankfurter.app."""

    BASE_URL = "https://api.frankfurter.app/latest"

    # Static fallback rates against USD in case of offline execution
    FALLBACK_RATES = {
        "USD": 1.0,
        "INR": 83.5,
        "EUR": 0.92,
        "GBP": 0.79,
        "JPY": 155.0,
    }

    def convert_currency(self, amount: float, from_curr: str, to_curr: str) -> float:
        from_c = from_curr.upper()
        to_c = to_curr.upper()

        if from_c == to_c:
            return round(amount, 2)

        cache_params = {"from": from_c, "to": to_c}
        cached_rate = api_cache.get("forex", cache_params)
        if cached_rate:
            return round(amount * cached_rate, 2)

        try:
            res = requests.get(
                self.BASE_URL,
                params={"from": from_c, "to": to_c},
                timeout=4
            )
            if res.status_code == 200:
                data = res.json()
                rate = data.get("rates", {}).get(to_c)
                if rate:
                    api_cache.set("forex", cache_params, rate, ttl=86400)
                    return round(amount * rate, 2)
        except Exception as e:
            logger.warning(f"Live currency API failed: {e}. Using fallback conversion table.")

        # Fallback math
        from_rate = self.FALLBACK_RATES.get(from_c, 1.0)
        to_rate = self.FALLBACK_RATES.get(to_c, 83.5)
        # Convert to USD then to target
        amount_in_usd = amount / from_rate
        converted = amount_in_usd * to_rate
        return round(converted, 2)

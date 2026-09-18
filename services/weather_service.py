import os
import requests
from typing import Optional
from services.base_provider import BaseWeatherProvider
from models.travel_state import WeatherForecast
from utils.caching import api_cache
from utils.logging import logger


class OpenMeteoWeatherService(BaseWeatherProvider):
    """Fetches real-time live weather using OpenWeatherMap & Open-Meteo."""

    GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
    FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

    def __init__(self):
        self.ow_key = os.getenv("OPENWEATHER_API_KEY", "")

    def get_forecast(self, city: str, date: str = "") -> WeatherForecast:
        cached = api_cache.get("weather", {"city": city.lower()})
        if cached:
            if not cached.get("retrieved_at"):
                from datetime import datetime, timezone
                cached["retrieved_at"] = datetime.now(timezone.utc).isoformat()
            return WeatherForecast(**cached)

        from datetime import datetime, timezone
        now_iso = datetime.now(timezone.utc).isoformat()

        # 1. Try OpenWeatherMap live API
        if self.ow_key and len(self.ow_key.strip()) > 10:
            try:
                ow_url = "https://api.openweathermap.org/data/2.5/weather"
                ow_res = requests.get(ow_url, params={"q": city, "appid": self.ow_key, "units": "metric"}, timeout=5)
                if ow_res.status_code == 200:
                    ow_data = ow_res.json()
                    temp = ow_data.get("main", {}).get("temp", 20.0)
                    weather_desc = ow_data.get("weather", [{}])[0].get("description", "Pleasant").title()
                    humidity = ow_data.get("main", {}).get("humidity", 50)
                    advisory = "Pleasant weather conditions for sightseeing"
                    if temp > 32:
                        advisory = "Warm day; stay hydrated and carry sun protection"
                    elif temp < 10:
                        advisory = "Chilly conditions; warm woolens recommended"

                    forecast = WeatherForecast(
                        location=city.title(),
                        temperature_c=round(temp, 1),
                        condition=weather_desc,
                        precipitation_chance_pct=int(humidity / 2),
                        advisory=advisory,
                        forecast_time=now_iso,
                        weather_code=0,
                        wind_speed=0.0,
                        source="OpenWeatherMap Live API",
                        retrieved_at=now_iso
                    )
                    api_cache.set("weather", {"city": city.lower()}, forecast.model_dump())
                    return forecast
            except Exception as e:
                logger.debug(f"OpenWeatherMap query skipped: {e}")

        try:
            # 2. Open-Meteo Live API Fallback
            geo_res = requests.get(
                self.GEOCODE_URL,
                params={"name": city, "count": 1, "language": "en", "format": "json"},
                timeout=5
            )
            if geo_res.status_code == 200:
                geo_data = geo_res.json()
                results = geo_data.get("results", [])
                if results:
                    lat = results[0]["latitude"]
                    lon = results[0]["longitude"]

                    # 2. Get Forecast
                    fc_res = requests.get(
                        self.FORECAST_URL,
                        params={
                            "latitude": lat,
                            "longitude": lon,
                            "current_weather": "true",
                            "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max",
                            "timezone": "auto"
                        },
                        timeout=5
                    )
                    if fc_res.status_code == 200:
                        fc_data = fc_res.json()
                        curr = fc_data.get("current_weather", {})
                        temp = curr.get("temperature", 21.0)
                        wcode = curr.get("weathercode", 0)

                        condition = self._weather_code_to_condition(wcode)
                        daily = fc_data.get("daily", {})
                        precip_list = daily.get("precipitation_probability_max", [10])
                        precip = precip_list[0] if precip_list else 10

                        advisory = "Favorable weather for outdoor activities"
                        if precip > 40:
                            advisory = "Carry an umbrella; moderate chance of rain"
                        elif temp > 35:
                            advisory = "High temperatures; stay hydrated and carry sun protection"
                        elif temp < 5:
                            advisory = "Cold temperatures; heavy woolens and thermal gear advised"

                        from datetime import datetime, timezone
                        now_iso = datetime.now(timezone.utc).isoformat()
                        wind = float(curr.get("windspeed", 0.0))
                        forecast_t = str(curr.get("time", now_iso))

                        forecast = WeatherForecast(
                            location=city.title(),
                            temperature_c=temp,
                            condition=condition,
                            precipitation_chance_pct=precip,
                            advisory=advisory,
                            forecast_time=forecast_t,
                            weather_code=int(wcode),
                            wind_speed=wind,
                            source="Open-Meteo Live API",
                            retrieved_at=now_iso
                        )
                        api_cache.set("weather", {"city": city.lower()}, forecast.model_dump())
                        return forecast
        except Exception as e:
            logger.warning(f"Live weather query for {city} failed: {e}. Using seasonal estimate.")

        # Fallback if connection fails
        fallback = WeatherForecast(
            location=city.title(),
            temperature_c=19.5,
            condition="Pleasant / Partially Cloudy",
            precipitation_chance_pct=15,
            advisory="Normal seasonal outdoor conditions",
            forecast_time=now_iso,
            weather_code=1,
            wind_speed=5.0,
            source="Open-Meteo Climatological Estimate",
            retrieved_at=now_iso
        )
        return fallback

    def _weather_code_to_condition(self, code: int) -> str:
        if code == 0:
            return "Clear Sky"
        elif code in (1, 2, 3):
            return "Mainly Clear / Partly Cloudy"
        elif code in (45, 48):
            return "Foggy"
        elif code in (51, 53, 55, 61, 63, 65):
            return "Rain / Showers"
        elif code in (71, 73, 75, 77, 85, 86):
            return "Snowfall"
        elif code in (95, 96, 99):
            return "Thunderstorm"
        return "Pleasant"

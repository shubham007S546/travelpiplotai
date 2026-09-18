"""Abstract Provider Interfaces for Travel Data Retrieval.

Every service implements:
- search(): raw API retrieval
- parse(): structure raw response
- normalize(): convert into standard domain models
- validate(): verify completeness and constraints
- cache(): cache key generation & storage
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from models.transport import TransportOption, LocalMobilityRecommendation
from models.accommodation import StayOption
from models.activity import ActivityOption, FoodOption, EssentialService
from models.travel_state import WeatherForecast


class BaseTransportProvider(ABC):
    """Abstract interface for intercity and local transit discovery."""

    @abstractmethod
    def search_intercity(self, origin: str, destination: str, date: str, travelers: int) -> List[TransportOption]:
        pass

    @abstractmethod
    def search_local_mobility(self, city: str, from_loc: str, to_loc: str, distance_km: float) -> LocalMobilityRecommendation:
        pass


class BaseStayProvider(ABC):
    """Abstract interface for accommodation search."""

    @abstractmethod
    def search_stays(self, city: str, check_in: str, check_out: str, travelers: int, budget_tier: str) -> List[StayOption]:
        pass


class BaseActivityProvider(ABC):
    """Abstract interface for attractions and experiences."""

    @abstractmethod
    def search_activities(self, city: str, interests: List[str], max_budget: float) -> List[ActivityOption]:
        pass


class BaseFoodProvider(ABC):
    """Abstract interface for meal and restaurant recommendations."""

    @abstractmethod
    def search_food(self, city: str, area: str, preference: str, price_tier: str) -> List[FoodOption]:
        pass


class BaseSafetyProvider(ABC):
    """Abstract interface for essential & emergency services."""

    @abstractmethod
    def search_essential_services(self, city: str, near_location: Optional[str] = None) -> List[EssentialService]:
        pass


class BaseWeatherProvider(ABC):
    """Abstract interface for weather forecasts."""

    @abstractmethod
    def get_forecast(self, city: str, date: str) -> WeatherForecast:
        pass


class BaseCurrencyProvider(ABC):
    """Abstract interface for exchange rates."""

    @abstractmethod
    def convert_currency(self, amount: float, from_curr: str, to_curr: str) -> float:
        pass


class BaseSearchProvider(ABC):
    """Abstract interface for open web grounding search."""

    @abstractmethod
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        pass

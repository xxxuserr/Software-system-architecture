from abc import ABC, abstractmethod
from typing import List
from app.core.entities.price_alert_entity import PriceAlertEntity

class AlertRepository(ABC):
    @abstractmethod
    def get_active_alerts(self) -> List[PriceAlertEntity]:
        raise NotImplementedError

    @abstractmethod
    def save(self, alert: PriceAlertEntity) -> None:
        raise NotImplementedError

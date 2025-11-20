from abc import ABC, abstractmethod

class Notifier(ABC):
    @abstractmethod
    def send_price_changed(self, email: str, product_name: str, old_price: float, new_price: float, link: str) -> None:
        raise NotImplementedError

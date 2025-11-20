from abc import ABC, abstractmethod
from typing import List, Optional
from app.core.entities.product_entity import ProductEntity

class ProductRepository(ABC):
    @abstractmethod
    def find_by_id(self, product_id: int) -> Optional[ProductEntity]:
        raise NotImplementedError

    @abstractmethod
    def search(self, query: str) -> List[ProductEntity]:
        raise NotImplementedError

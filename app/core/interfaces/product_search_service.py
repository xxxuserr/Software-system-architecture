from abc import ABC, abstractmethod
from typing import List
from app.core.entities.product_entity import ProductEntity

class ProductSearchService(ABC):
    @abstractmethod
    def search_products(self, query: str) -> List[ProductEntity]:
        raise NotImplementedError

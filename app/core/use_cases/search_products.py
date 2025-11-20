from typing import List
from app.core.entities.product_entity import ProductEntity
from app.core.interfaces.product_search_service import ProductSearchService

class SearchProductsUseCase:
    """Orchestrează căutarea produselor, independent de modul de implementare (scraper, API etc.)."""
    def __init__(self, search_service: ProductSearchService):
        self._search_service = search_service

    def execute(self, query: str) -> List[ProductEntity]:
        if not query:
            return []
        return self._search_service.search_products(query)

from typing import List
from app.core.entities.product_entity import ProductEntity
from app.core.interfaces.product_search_service import ProductSearchService
from app.scraper import search_product

class ProductSearchServiceImpl(ProductSearchService):
    """Adapter care folosește funcția existentă search_product din scraper.py."""

    def search_products(self, query: str) -> List[ProductEntity]:
        raw_results = search_product(query)
        entities: List[ProductEntity] = []

        for item in raw_results:
            # item poate fi dict sau model Product
            if isinstance(item, dict):
                entities.append(
                    ProductEntity(
                        id=item.get("id"),
                        name=item.get("name"),
                        price=item.get("price"),
                        image=item.get("image"),
                        link=item.get("link"),
                        specs=item.get("specs") or {},
                        domain=item.get("domain"),
                    )
                )
            else:
                entities.append(
                    ProductEntity(
                        id=getattr(item, "id", None),
                        name=getattr(item, "name", None),
                        price=getattr(item, "price", None),
                        image=getattr(item, "image", None),
                        link=getattr(item, "link", None),
                        specs=getattr(item, "specs", None),
                        domain=getattr(item, "domain", None),
                    )
                )
        return entities

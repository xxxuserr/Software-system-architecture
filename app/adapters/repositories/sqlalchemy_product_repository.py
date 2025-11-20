from typing import List, Optional
from app.core.entities.product_entity import ProductEntity
from app.core.interfaces.product_repository import ProductRepository
from app.models import Product

class SqlAlchemyProductRepository(ProductRepository):
    def _to_entity(self, model: Product) -> ProductEntity:
        return ProductEntity(
            id=model.id,
            name=model.name,
            price=model.price,
            image=model.image,
            link=model.link,
            specs=model.specs,
            domain=model.domain,
        )

    def find_by_id(self, product_id: int) -> Optional[ProductEntity]:
        model = Product.query.get(product_id)
        return self._to_entity(model) if model else None

    def search(self, query: str) -> List[ProductEntity]:
        if not query:
            models = Product.query.all()
        else:
            like = f"%{query}%"
            models = Product.query.filter(Product.name.ilike(like)).all()
        return [self._to_entity(m) for m in models]

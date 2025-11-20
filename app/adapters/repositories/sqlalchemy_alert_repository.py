from typing import List
from app.core.entities.price_alert_entity import PriceAlertEntity
from app.core.interfaces.alert_repository import AlertRepository
from app.models import PriceAlert
from app import db

class SqlAlchemyAlertRepository(AlertRepository):
    def _to_entity(self, model: PriceAlert) -> PriceAlertEntity:
        return PriceAlertEntity(
            id=model.id,
            user_id=model.user_id,
            product_id=model.product_id,
            initial_price=model.initial_price,
            active=model.active,
        )

    def _update_model(self, model: PriceAlert, entity: PriceAlertEntity):
        model.initial_price = entity.initial_price
        model.active = entity.active

    def get_active_alerts(self) -> List[PriceAlertEntity]:
        models = PriceAlert.query.filter_by(active=True).all()
        return [self._to_entity(m) for m in models]

    def save(self, alert: PriceAlertEntity) -> None:
        # presupunem că alerta există deja în DB
        model = PriceAlert.query.get(alert.id)
        if model:
            self._update_model(model, alert)
            db.session.commit()

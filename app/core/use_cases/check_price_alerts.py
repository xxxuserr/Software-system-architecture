from app.core.interfaces.alert_repository import AlertRepository
from app.core.interfaces.product_repository import ProductRepository
from app.core.interfaces.user_repository import UserRepository
from app.core.interfaces.notifier import Notifier

class CheckPriceAlertsUseCase:
    """Logica pentru verificarea alertelor de preț, fără să depindă de ORM sau Flask."""

    def __init__(self, alert_repo: AlertRepository, product_repo: ProductRepository,
                 user_repo: UserRepository, notifier: Notifier):
        self._alert_repo = alert_repo
        self._product_repo = product_repo
        self._user_repo = user_repo
        self._notifier = notifier

    def execute(self):
        alerts = self._alert_repo.get_active_alerts()
        for alert in alerts:
            product = self._product_repo.find_by_id(alert.product_id)
            if not product or product.price is None:
                continue

            current_price = product.price
            if current_price != alert.initial_price:
                user = self._user_repo.find_by_id(alert.user_id)
                if user and user.email:
                    self._notifier.send_price_changed(
                        email=user.email,
                        product_name=product.name,
                        old_price=alert.initial_price,
                        new_price=current_price,
                        link=product.link,
                    )
                # dezactivăm alerta și actualizăm prețul inițial
                alert.initial_price = current_price
                alert.active = False
                self._alert_repo.save(alert)

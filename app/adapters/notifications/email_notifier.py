from app.core.interfaces.notifier import Notifier
from app.email_utils import send_email_alert

class EmailNotifier(Notifier):
    def send_price_changed(self, email: str, product_name: str, old_price: float, new_price: float, link: str) -> None:
        subject = f"🔔 Preț modificat la {product_name}"
        body = (
            f"Noul preț este {new_price} lei (anterior: {old_price}).\n"
            f"Link: {link}"
        )
        send_email_alert(to_email=email, subject=subject, body=body)

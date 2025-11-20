from app import app
from flask_apscheduler import APScheduler

# --- Clean Architecture imports ---
from app.core.use_cases.check_price_alerts import CheckPriceAlertsUseCase
from app.adapters.repositories.sqlalchemy_alert_repository import SqlAlchemyAlertRepository
from app.adapters.repositories.sqlalchemy_product_repository import SqlAlchemyProductRepository
from app.adapters.repositories.sqlalchemy_user_repository import SqlAlchemyUserRepository
from app.adapters.notifications.email_notifier import EmailNotifier


def check_alerts():
    """Wrapper care apelează use-case-ul curat pentru verificarea alertelor de preț."""
    with app.app_context():
        use_case = CheckPriceAlertsUseCase(
            alert_repo=SqlAlchemyAlertRepository(),
            product_repo=SqlAlchemyProductRepository(),
            user_repo=SqlAlchemyUserRepository(),
            notifier=EmailNotifier(),
        )
        use_case.execute()


# Scheduler
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()
scheduler.add_job(
    id='CheckPriceAlerts',
    func=check_alerts,
    trigger='interval',
    minutes=1
)

if __name__ == "__main__":
    app.run(debug=True)

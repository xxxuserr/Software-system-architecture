class PriceAlertEntity:
    def __init__(self, id, user_id, product_id, initial_price, active=True):
        self.id = id
        self.user_id = user_id
        self.product_id = product_id
        self.initial_price = initial_price
        self.active = active

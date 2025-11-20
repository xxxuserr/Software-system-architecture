class ProductEntity:
    """Entitate de domeniu pentru produs, independentă de ORM / framework."""
    def __init__(self, id, name, price, image, link, specs=None, domain=None):
        self.id = id
        self.name = name
        self.price = price
        self.image = image
        self.link = link
        self.specs = specs or {}
        self.domain = domain

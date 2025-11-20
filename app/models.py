from app import db
from flask_login import UserMixin
from flask_bcrypt import Bcrypt
from datetime import datetime


bcrypt = Bcrypt()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

class FavoriteProduct(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('favorites', lazy=True))
    product = db.relationship('Product', backref=db.backref('favorited_by', lazy=True))

    def __repr__(self):
        return f'<FavoriteProduct user={self.user_id} product={self.product_id}>'

    
class PriceAlert(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id'),  nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

    initial_price = db.Column(db.Float)
    active        = db.Column(db.Boolean, default=True)

    # legături inverse (NU backref din nou!)
    product = db.relationship("Product", back_populates="price_alerts")
    user    = db.relationship("User",   backref="price_alerts")   # ăsta e ok


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=True)
    image = db.Column(db.String(500), nullable=True)
    link = db.Column(db.String(1000), unique=True, nullable=False)
    specs = db.Column(db.Text, nullable=True)
    domain = db.Column(db.String(255), nullable=True)
    currency = db.Column(db.String(10), nullable=True)  # <– AICI



    # un produs → multe alerte
    price_alerts = db.relationship(
        "PriceAlert",
        back_populates="product",
        lazy=True,
        cascade="all, delete-orphan"
    )

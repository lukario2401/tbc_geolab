from datetime import datetime, timezone

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user

from ext import db, app
from flask_login import LoginManager, UserMixin

login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(50), default='user')
    joined_date = db.Column(db.DateTime, default=datetime.utcnow)

    liked_products = db.relationship('Product', secondary='likes', backref=db.backref('likers', lazy='dynamic'))

    def __init__(self, username, email, password_hash,role):
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role

    @property
    def is_active(self):
        return True

    def __repr__(self):
        return f"<User {self.username}>"

    def get_id(self):
        return str(self.id)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def generate_hash(password):
        return generate_password_hash(password)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Like(db.Model):
    __tablename__ = 'likes'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id', ondelete='CASCADE'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

    db.UniqueConstraint('user_id', 'product_id', name='unique_like')


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    img = db.Column(db.String(200), nullable=True)
    likes = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"<Product {self.name}>"





# with app.app_context():
#     db.drop_all()
#     db.create_all()


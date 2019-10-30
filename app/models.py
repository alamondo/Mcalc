from app import db, login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    spending = db.relationship('Spending', backref='author', lazy='dynamic')
    income = db.relationship('Income', backref='author', lazy='dynamic')
    categories = db.relationship('UserCategory', backref='author', lazy='dynamic')
    income_categories = db.relationship('UserCategoryIncome', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class UserCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(150))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class UserCategoryIncome(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(150))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Spending(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Float)
    note = db.Column(db.String(150))
    category_name = db.Column(db.String(150))
    category = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.value)

    def __init__(self, **kwargs):
        super(Spending, self).__init__(**kwargs)
        self.category_name = UserCategory.query.filter(UserCategory.user_id == self.user_id,
                                                       UserCategory.id == self.category).first().value


class Income(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Float)
    note = db.Column(db.String(150))
    category_name = db.Column(db.String(150))
    category = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.value)

    def __init__(self, **kwargs):
        super(Income, self).__init__(**kwargs)
        self.category_name = UserCategoryIncome.query.filter(UserCategoryIncome.user_id == self.user_id,
                                                             UserCategoryIncome.id == self.category).first().value


@login.user_loader
def load_user(id):
    return User.query.get(int(id))

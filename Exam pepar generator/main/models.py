from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'user'  # Specify the table name explicitly
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    institution = db.Column(db.String(255))
    education_level = db.Column(db.String(100), nullable=False)  # Adjust the type and size as needed

    @staticmethod
    def get(user_id):
        return User.query.get(int(user_id))  # Ensure ID is converted to int

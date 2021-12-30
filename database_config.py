from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from decouple import config

app = Flask(__name__)
SECRET_KEY = config('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'

db = SQLAlchemy(app)
db:SQLAlchemy

class Post(db.Model):
    __tablename__ = 'posts'
    id_post = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    id_author = db.Column(db.Integer, db.ForeignKey('author.id_author'))

class Author(db.Model):
    __tablename__ = 'author'
    id_author = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String)
    password = db.Column(db.String)
    is_admin = db.Column(db.Boolean, default=False)
    posts = db.relationship('Post')

def initialize_database():
    db.drop_all()
    db.create_all()

    admin = Author(
        name='emidio', 
        email='emidio.valereto@gmail.com', 
        password='123456', 
        is_admin=True
        )
    db.session.add(admin)
    db.session.commit()

if __name__ == '__main__':
    initialize_database()
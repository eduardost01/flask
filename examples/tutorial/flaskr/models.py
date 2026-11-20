
from flaskr import db
from datetime import datetime


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(80), unique=True, nullable=False)

    password = db.Column(db.String(255), nullable=False)

    avatar = db.Column(db.String(255))

    posts = db.relationship(
        'Post',
        backref='author',
        lazy=True,
        cascade='all, delete-orphan'
    )


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    author_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )

    created = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.now
    )

    title = db.Column(db.String(100), nullable=False)

    body = db.Column(db.Text, nullable=False)

    imagem_post = db.Column(db.String(255))

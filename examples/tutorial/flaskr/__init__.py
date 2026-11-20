
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():

    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'chave-secreta-flaskr'

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flaskr.sqlite'

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['UPLOAD_FOLDER'] = os.path.join(
        app.static_folder,
        'uploads'
    )

    app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)

    from . import models

    with app.app_context():
        db.create_all()

    from . import auth
    from . import blog
    from . import calculos

    app.register_blueprint(auth.bp)
    app.register_blueprint(blog.bp)
    app.register_blueprint(calculos.bp)

    app.add_url_rule('/', endpoint='index')

    return app

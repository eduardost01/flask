from PIL import Image
import uuid
import os
import functools

from flask import (
    Blueprint, flash, g, redirect,
    render_template, request, session,
    url_for, current_app
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from werkzeug.utils import secure_filename

from . import db
from .models import User


bp = Blueprint('auth', __name__, url_prefix='/auth')


def salvar_imagem(arquivo):

    if arquivo and arquivo.filename:

        nome = secure_filename(arquivo.filename)

        if not nome or '.' not in nome:
            return None

        extensao = nome.rsplit('.', 1)[-1].lower()

        formatos = {
            'jpg': 'JPEG',
            'jpeg': 'JPEG',
            'png': 'PNG',
            'gif': 'GIF',
            'webp': 'WEBP'
        }

        if extensao not in formatos:
            return None

        try:

            imagem = Image.open(arquivo.stream)

            if imagem.format != formatos[extensao]:
                return None

            imagem.verify()

            arquivo.stream.seek(0)

            nome_final = uuid.uuid4().hex + '.' + extensao

            caminho = os.path.join(
                current_app.config['UPLOAD_FOLDER'],
                nome_final
            )

            arquivo.save(caminho)

            return nome_final

        except Exception:
            return None

    return None


@bp.before_app_request
def carregar_usuario():

    id_usuario = session.get('user_id')

    if id_usuario is None:
        g.user = None
    else:
        g.user = db.session.get(User, id_usuario)


@bp.route('/register', methods=('GET', 'POST'))
def register():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        arquivo = request.files.get('avatar')

        error = None

        if not username:
            error = 'O nome de usuário é obrigatório.'

        elif not password:
            error = 'A senha é obrigatória.'

        elif User.query.filter_by(username=username).first():
            error = 'Este usuário já está cadastrado.'

        nome_avatar = None

        if error is None and arquivo and arquivo.filename:
            nome_avatar = salvar_imagem(arquivo)

            if nome_avatar is None:
                error = 'Formato de imagem inválido.'

        if error is not None:
            flash(error)

        else:

            usuario = User(
                username=username,
                password=generate_password_hash(password),
                avatar=nome_avatar
            )

            db.session.add(usuario)
            db.session.commit()

            return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        error = None

        usuario = User.query.filter_by(
            username=username
        ).first()

        if usuario is None:
            error = 'Usuário não encontrado.'

        elif not check_password_hash(usuario.password, password):
            error = 'Senha incorreta.'

        if error is None:

            session.clear()
            session['user_id'] = usuario.id

            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.route('/logout')
def logout():

    session.clear()

    return redirect(url_for('index'))


def login_required(view):

    @functools.wraps(view)
    def wrapped_view(**kwargs):

        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

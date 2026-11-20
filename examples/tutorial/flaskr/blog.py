from PIL import Image
import uuid
import os

from flask import (
    Blueprint, flash, g, redirect,
    render_template, request, url_for,
    current_app
)

from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

from . import db
from .models import Post
from .auth import login_required


bp = Blueprint('blog', __name__)


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


@bp.route('/')
def index():

    posts = Post.query.order_by(
        Post.created.desc()
    ).all()

    return render_template(
        'blog/index.html',
        posts=posts
    )


def get_post(id, check_author=True):

    post = db.session.get(Post, id)

    if post is None:
        abort(404)

    if check_author and post.author_id != g.user.id:
        abort(403)

    return post


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():

    if request.method == 'POST':

        title = request.form['title']
        body = request.form['body']

        arquivo = request.files.get('imagem_post')

        error = None
        nome_imagem = None

        if not title:
            error = 'O título é obrigatório.'

        elif not body:
            error = 'O conteúdo é obrigatório.'

        if error is None and arquivo and arquivo.filename:

            nome_imagem = salvar_imagem(arquivo)

            if nome_imagem is None:
                error = 'Formato de imagem inválido.'

        if error is not None:
            flash(error)

        else:

            post = Post(
                title=title,
                body=body,
                author_id=g.user.id,
                imagem_post=nome_imagem
            )

            db.session.add(post)
            db.session.commit()

            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):

    post = get_post(id)

    if request.method == 'POST':

        title = request.form['title']
        body = request.form['body']

        arquivo = request.files.get('imagem_post')

        error = None

        if not title:
            error = 'O título é obrigatório.'

        elif not body:
            error = 'O conteúdo é obrigatório.'

        if error is None and arquivo and arquivo.filename:

            nome_imagem = salvar_imagem(arquivo)

            if nome_imagem is None:
                error = 'Formato de imagem inválido.'

            else:
                post.imagem_post = nome_imagem

        if error is not None:
            flash(error)

        else:

            post.title = title
            post.body = body

            db.session.commit()

            return redirect(url_for('blog.index'))

    return render_template(
        'blog/update.html',
        post=post
    )


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):

    post = get_post(id)

    db.session.delete(post)
    db.session.commit()

    return redirect(url_for('blog.index'))

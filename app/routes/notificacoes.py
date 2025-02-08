from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from app.models.notificacao import Notificacao
from app import db

bp = Blueprint('notificacoes', __name__)

@bp.route('/notificacoes')
@login_required
def index():
    notificacoes = Notificacao.query.filter_by(usuario_id=current_user.id)\
        .order_by(Notificacao.data_criacao.desc()).all()
    return render_template('notificacoes/index.html', notificacoes=notificacoes)

@bp.route('/notificacoes/nao-lidas')
@login_required
def nao_lidas():
    count = Notificacao.query.filter_by(
        usuario_id=current_user.id,
        lida=False
    ).count()
    return jsonify({'count': count})

@bp.route('/notificacoes/marcar-lida/<int:id>')
@login_required
def marcar_lida(id):
    notificacao = Notificacao.query.get_or_404(id)
    if notificacao.usuario_id == current_user.id:
        notificacao.lida = True
        db.session.commit()
    return jsonify({'success': True})

def criar_notificacao(usuario_id, titulo, mensagem, tipo='sistema', link=None):
    notificacao = Notificacao(
        usuario_id=usuario_id,
        titulo=titulo,
        mensagem=mensagem,
        tipo=tipo,
        link=link
    )
    db.session.add(notificacao)
    db.session.commit() 
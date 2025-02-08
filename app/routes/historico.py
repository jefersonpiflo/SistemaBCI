from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from app.models.historico import HistoricoImovel
from app.models.imovel import Imovel
from app import db

bp = Blueprint('historico', __name__)

@bp.route('/historico/imovel/<int:imovel_id>')
@login_required
def imovel(imovel_id):
    imovel = Imovel.query.get_or_404(imovel_id)
    historicos = HistoricoImovel.query.filter_by(imovel_id=imovel_id)\
        .order_by(HistoricoImovel.data_alteracao.desc()).all()
    return render_template('historico/imovel.html', imovel=imovel, historicos=historicos)

def registrar_alteracao(imovel_id, tipo_alteracao, campo=None, valor_anterior=None, valor_novo=None):
    historico = HistoricoImovel(
        imovel_id=imovel_id,
        usuario_id=current_user.id,
        tipo_alteracao=tipo_alteracao,
        campo_alterado=campo,
        valor_anterior=str(valor_anterior) if valor_anterior is not None else None,
        valor_novo=str(valor_novo) if valor_novo is not None else None
    )
    db.session.add(historico)
    db.session.commit() 
from flask import Blueprint, render_template, request
from flask_login import login_required
from app.models.auditoria import LogAuditoria
from datetime import datetime, timedelta
from sqlalchemy import desc

bp = Blueprint('auditoria', __name__)

@bp.route('/auditoria')
@login_required
def index():
    # Filtros
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    modulo = request.args.get('modulo')
    acao = request.args.get('acao')
    usuario_id = request.args.get('usuario_id', type=int)
    
    # Query base
    query = LogAuditoria.query
    
    # Aplicar filtros
    if data_inicio:
        query = query.filter(LogAuditoria.data_hora >= datetime.strptime(data_inicio, '%Y-%m-%d'))
    if data_fim:
        query = query.filter(LogAuditoria.data_hora <= datetime.strptime(data_fim, '%Y-%m-%d') + timedelta(days=1))
    if modulo:
        query = query.filter(LogAuditoria.modulo == modulo)
    if acao:
        query = query.filter(LogAuditoria.acao == acao)
    if usuario_id:
        query = query.filter(LogAuditoria.usuario_id == usuario_id)
    
    # Ordenar e paginar
    logs = query.order_by(desc(LogAuditoria.data_hora)).paginate()
    
    return render_template('auditoria/index.html', 
                         logs=logs,
                         data_inicio=data_inicio,
                         data_fim=data_fim,
                         modulo=modulo,
                         acao=acao,
                         usuario_id=usuario_id)

@bp.route('/auditoria/detalhes/<int:id>')
@login_required
def detalhes(id):
    log = LogAuditoria.query.get_or_404(id)
    return render_template('auditoria/detalhes.html', log=log) 
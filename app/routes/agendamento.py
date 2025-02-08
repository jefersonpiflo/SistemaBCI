from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models.agendamento import AgendamentoVistoria
from app.models.imovel import Imovel
from app.models.usuario import Usuario
from datetime import datetime, timedelta
from sqlalchemy import and_, or_

bp = Blueprint('agendamento', __name__)

@bp.route('/agendamentos')
@login_required
def index():
    # Filtros
    status = request.args.get('status', 'agendada')
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    fiscal_id = request.args.get('fiscal_id', type=int)
    
    query = AgendamentoVistoria.query
    
    if status:
        query = query.filter_by(status=status)
    if data_inicio:
        query = query.filter(AgendamentoVistoria.data_agendada >= datetime.strptime(data_inicio, '%Y-%m-%d'))
    if data_fim:
        query = query.filter(AgendamentoVistoria.data_agendada <= datetime.strptime(data_fim, '%Y-%m-%d'))
    if fiscal_id:
        query = query.filter_by(fiscal_id=fiscal_id)
    
    agendamentos = query.order_by(AgendamentoVistoria.data_agendada).all()
    fiscais = Usuario.query.filter_by(tipo='fiscal').all()
    
    return render_template('agendamento/index.html',
                         agendamentos=agendamentos,
                         fiscais=fiscais,
                         status=status,
                         data_inicio=data_inicio,
                         data_fim=data_fim,
                         fiscal_id=fiscal_id)

@bp.route('/agendamentos/calendario')
@login_required
def calendario():
    start = request.args.get('start')
    end = request.args.get('end')
    
    agendamentos = AgendamentoVistoria.query.filter(
        and_(
            AgendamentoVistoria.data_agendada >= start,
            AgendamentoVistoria.data_agendada <= end
        )
    ).all()
    
    eventos = [{
        'id': a.id,
        'title': f'Vistoria - {a.imovel.inscricao_imobiliaria}',
        'start': a.data_agendada.isoformat(),
        'end': (a.data_agendada + timedelta(hours=1)).isoformat(),
        'color': get_cor_status(a.status),
        'extendedProps': {
            'fiscal': a.fiscal.nome,
            'tipo': a.tipo_vistoria,
            'prioridade': a.prioridade
        }
    } for a in agendamentos]
    
    return jsonify(eventos)

@bp.route('/agendamentos/novo', methods=['GET', 'POST'])
@login_required
def novo():
    if request.method == 'POST':
        imovel_id = request.form['imovel_id']
        fiscal_id = request.form['fiscal_id']
        data_agendada = datetime.strptime(
            f"{request.form['data']} {request.form['hora']}", 
            '%Y-%m-%d %H:%M'
        )
        
        # Verificar disponibilidade do fiscal
        conflito = AgendamentoVistoria.query.filter(
            and_(
                AgendamentoVistoria.fiscal_id == fiscal_id,
                AgendamentoVistoria.data_agendada.between(
                    data_agendada - timedelta(hours=1),
                    data_agendada + timedelta(hours=1)
                )
            )
        ).first()
        
        if conflito:
            flash('Fiscal já possui agendamento neste horário', 'danger')
            return redirect(url_for('agendamento.novo'))
        
        agendamento = AgendamentoVistoria(
            imovel_id=imovel_id,
            fiscal_id=fiscal_id,
            data_agendada=data_agendada,
            tipo_vistoria=request.form['tipo_vistoria'],
            prioridade=request.form['prioridade'],
            motivo=request.form['motivo'],
            observacoes=request.form['observacoes']
        )
        
        db.session.add(agendamento)
        db.session.commit()
        
        flash('Agendamento criado com sucesso!', 'success')
        return redirect(url_for('agendamento.index'))
    
    imoveis = Imovel.query.all()
    fiscais = Usuario.query.filter_by(tipo='fiscal').all()
    return render_template('agendamento/novo.html', imoveis=imoveis, fiscais=fiscais)

def get_cor_status(status):
    cores = {
        'agendada': '#ffc107',  # amarelo
        'realizada': '#28a745',  # verde
        'cancelada': '#dc3545',  # vermelho
        'reagendada': '#17a2b8'  # azul
    }
    return cores.get(status, '#6c757d')  # cinza como padrão 
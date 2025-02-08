from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from app.models.aliquota import Aliquota
from app import db
from datetime import datetime

bp = Blueprint('aliquotas', __name__)

@bp.route('/aliquotas')
@login_required
def index():
    aliquotas = Aliquota.query.order_by(
        Aliquota.tipo_imovel,
        Aliquota.padrao_construcao,
        Aliquota.data_inicio.desc()
    ).all()
    return render_template('aliquotas/index.html', aliquotas=aliquotas)

@bp.route('/aliquotas/nova', methods=['GET', 'POST'])
@login_required
def nova():
    if request.method == 'POST':
        aliquota = Aliquota(
            tipo_imovel=request.form['tipo_imovel'],
            padrao_construcao=request.form['padrao_construcao'] or None,
            valor=float(request.form['valor']),
            data_inicio=datetime.strptime(request.form['data_inicio'], '%Y-%m-%d').date(),
            data_fim=datetime.strptime(request.form['data_fim'], '%Y-%m-%d').date() if request.form['data_fim'] else None,
            observacao=request.form['observacao']
        )
        
        db.session.add(aliquota)
        db.session.commit()
        
        flash('Alíquota cadastrada com sucesso!', 'success')
        return redirect(url_for('aliquotas.index'))
        
    return render_template('aliquotas/form.html')

@bp.route('/aliquotas/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    aliquota = Aliquota.query.get_or_404(id)
    
    if request.method == 'POST':
        aliquota.tipo_imovel = request.form['tipo_imovel']
        aliquota.padrao_construcao = request.form['padrao_construcao'] or None
        aliquota.valor = float(request.form['valor'])
        aliquota.data_inicio = datetime.strptime(request.form['data_inicio'], '%Y-%m-%d').date()
        aliquota.data_fim = datetime.strptime(request.form['data_fim'], '%Y-%m-%d').date() if request.form['data_fim'] else None
        aliquota.observacao = request.form['observacao']
        
        db.session.commit()
        flash('Alíquota atualizada com sucesso!', 'success')
        return redirect(url_for('aliquotas.index'))
        
    return render_template('aliquotas/form.html', aliquota=aliquota) 
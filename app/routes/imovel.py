from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from app import db
from app.models.imovel import Imovel
from datetime import datetime

bp = Blueprint('imovel', __name__)

@bp.route('/imoveis')
@login_required
def index():
    imoveis = Imovel.query.all()
    return render_template('imovel/index.html', imoveis=imoveis)

@bp.route('/imoveis/novo', methods=['GET', 'POST'])
@login_required
def novo():
    if request.method == 'POST':
        imovel = Imovel(
            inscricao_imobiliaria=request.form['inscricao'],
            tipo_imovel=request.form['tipo'],
            area_terreno=float(request.form['area_terreno']),
            area_construida=float(request.form.get('area_construida', 0)),
            valor_venal=float(request.form['valor_venal']),
            logradouro=request.form['logradouro'],
            numero=request.form['numero'],
            complemento=request.form.get('complemento'),
            bairro=request.form['bairro'],
            cidade=request.form['cidade'],
            estado=request.form['estado'],
            cep=request.form['cep']
        )
        
        db.session.add(imovel)
        db.session.commit()
        
        flash('Imóvel cadastrado com sucesso!', 'success')
        return redirect(url_for('imovel.index'))
        
    return render_template('imovel/form.html')

@bp.route('/imoveis/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    imovel = Imovel.query.get_or_404(id)
    
    if request.method == 'POST':
        imovel.inscricao_imobiliaria = request.form['inscricao']
        imovel.tipo_imovel = request.form['tipo']
        imovel.area_terreno = float(request.form['area_terreno'])
        imovel.area_construida = float(request.form.get('area_construida', 0))
        imovel.valor_venal = float(request.form['valor_venal'])
        imovel.logradouro = request.form['logradouro']
        imovel.numero = request.form['numero']
        imovel.complemento = request.form.get('complemento')
        imovel.bairro = request.form['bairro']
        imovel.cidade = request.form['cidade']
        imovel.estado = request.form['estado']
        imovel.cep = request.form['cep']
        
        db.session.commit()
        flash('Imóvel atualizado com sucesso!', 'success')
        return redirect(url_for('imovel.index'))
        
    return render_template('imovel/form.html', imovel=imovel)

@bp.route('/imovel/busca', methods=['GET'])
@login_required
def busca():
    query = request.args.get('q', '')
    tipo_busca = request.args.get('tipo', 'inscricao')
    
    imoveis = []
    if query:
        if tipo_busca == 'inscricao':
            imoveis = Imovel.query.filter(Imovel.inscricao_imobiliaria.like(f'%{query}%')).all()
        elif tipo_busca == 'proprietario':
            imoveis = Imovel.query.filter(Imovel.proprietario_nome.like(f'%{query}%')).all()
        elif tipo_busca == 'cpf':
            imoveis = Imovel.query.filter(Imovel.proprietario_cpf == query).all()
    
    return render_template('imovel/busca.html', imoveis=imoveis, query=query, tipo_busca=tipo_busca)

@bp.route('/imovel/<int:id>')
@login_required
def visualizar(id):
    imovel = Imovel.query.get_or_404(id)
    return render_template('imovel/visualizar.html', imovel=imovel)

@bp.route('/imoveis/busca-avancada', methods=['GET', 'POST'])
@login_required
def busca_avancada():
    query = Imovel.query

    if request.method == 'POST':
        # Filtros de busca
        inscricao = request.form.get('inscricao')
        tipo = request.form.get('tipo')
        bairro = request.form.get('bairro')
        logradouro = request.form.get('logradouro')
        area_min = request.form.get('area_min')
        area_max = request.form.get('area_max')
        valor_min = request.form.get('valor_min')
        valor_max = request.form.get('valor_max')

        if inscricao:
            query = query.filter(Imovel.inscricao_imobiliaria.like(f'%{inscricao}%'))
        if tipo:
            query = query.filter(Imovel.tipo_imovel == tipo)
        if bairro:
            query = query.filter(Imovel.bairro.like(f'%{bairro}%'))
        if logradouro:
            query = query.filter(Imovel.logradouro.like(f'%{logradouro}%'))
        if area_min:
            query = query.filter(Imovel.area_terreno >= float(area_min))
        if area_max:
            query = query.filter(Imovel.area_terreno <= float(area_max))
        if valor_min:
            query = query.filter(Imovel.valor_venal >= float(valor_min))
        if valor_max:
            query = query.filter(Imovel.valor_venal <= float(valor_max))

        imoveis = query.all()
        return render_template('imovel/busca_avancada.html', 
                            imoveis=imoveis, 
                            filtros=request.form)

    # GET: mostra o formulário de busca
    return render_template('imovel/busca_avancada.html') 

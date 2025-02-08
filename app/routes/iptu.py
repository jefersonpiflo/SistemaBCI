from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file, jsonify
from flask_login import login_required
from app import db
from app.models.imovel import Imovel
from app.models.aliquota import Aliquota
from app.models.configuracao_boleto import ConfiguracaoBoleto
from app.utils.boleto import gerar_boleto as gerar_boleto_pdf
from datetime import datetime, date
import os
from dateutil.relativedelta import relativedelta

bp = Blueprint('iptu', __name__, url_prefix='/iptu')

@bp.route('/')
def index():
    imoveis = Imovel.query.all()
    return render_template('iptu/index.html', imoveis=imoveis, datetime=datetime)

@bp.route('/calculo/<int:imovel_id>')
def calculo(imovel_id):
    imovel = Imovel.query.get_or_404(imovel_id)
    aliquota = Aliquota.query.filter_by(tipo_imovel=imovel.tipo_imovel, ativo=True).first()
    
    if not aliquota:
        flash('Alíquota não encontrada para este tipo de imóvel', 'error')
        return redirect(url_for('iptu.index'))
    
    valor_iptu = imovel.valor_venal * (aliquota.valor / 100)
    
    # Salvar o valor do IPTU no imóvel
    imovel.valor_iptu = valor_iptu
    db.session.commit()
    
    return render_template('iptu/calculo.html', imovel=imovel, valor_iptu=valor_iptu)

@bp.route('/gerar_boleto/<int:imovel_id>')
def gerar_boleto(imovel_id):
    try:
        imovel = Imovel.query.get_or_404(imovel_id)
        config_boleto = ConfiguracaoBoleto.query.filter_by(ativo=True).first()
        
        if not config_boleto:
            flash('Configuração de boleto não encontrada', 'error')
            return redirect(url_for('iptu.calculo', imovel_id=imovel_id))
        
        aliquota = Aliquota.query.filter_by(tipo_imovel=imovel.tipo_imovel, ativo=True).first()
        if not aliquota:
            flash('Alíquota não encontrada para este tipo de imóvel', 'error')
            return redirect(url_for('iptu.calculo', imovel_id=imovel_id))
        
        valor_iptu = imovel.valor_venal * (aliquota.valor / 100)
        
        # Calcula a data de vencimento corretamente usando relativedelta
        hoje = datetime.now()
        vencimento = hoje + relativedelta(months=1)  # Vencimento em 1 mês
        vencimento = vencimento.replace(hour=0, minute=0, second=0, microsecond=0)
        
        dados_boleto = {
            'valor': valor_iptu,
            'vencimento': vencimento,
            'numero_documento': f'IPTU{imovel.id}2024',
            'sacado': imovel.proprietario
        }
        
        arquivo_boleto = gerar_boleto_pdf(dados_boleto, config_boleto)
        
        response = send_file(
            arquivo_boleto,
            as_attachment=True,
            download_name='boleto_iptu.pdf'
        )
        
        @response.call_on_close
        def remove_file():
            try:
                os.remove(arquivo_boleto)
            except:
                pass
        
        return response
        
    except Exception as e:
        flash(f'Erro ao gerar boleto: {str(e)}', 'error')
        return redirect(url_for('iptu.calculo', imovel_id=imovel_id))

@bp.route('/atualizar_imovel/<int:imovel_id>', methods=['POST'])
def atualizar_imovel(imovel_id):
    try:
        imovel = Imovel.query.get_or_404(imovel_id)
        
        # Atualizar dados do imóvel
        if 'proprietario' in request.form:
            imovel.proprietario = request.form['proprietario']
        if 'endereco' in request.form:
            imovel.endereco = request.form['endereco']
        if 'bairro' in request.form:
            imovel.bairro = request.form['bairro']
        if 'cep' in request.form:
            imovel.cep = request.form['cep']
        if 'area_terreno' in request.form:
            imovel.area_terreno = float(request.form['area_terreno'])
        if 'area_construida' in request.form:
            imovel.area_construida = float(request.form['area_construida'])
        if 'valor_venal' in request.form:
            imovel.valor_venal = float(request.form['valor_venal'])
        if 'tipo_imovel' in request.form:
            imovel.tipo_imovel = request.form['tipo_imovel']
        
        # Salvar as alterações
        db.session.add(imovel)
        db.session.commit()
        
        flash('Imóvel atualizado com sucesso!', 'success')
        return redirect(url_for('iptu.index'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao atualizar imóvel: {str(e)}', 'error')
        return redirect(url_for('iptu.index'))

@bp.route('/editar_imovel/<int:imovel_id>')
def editar_imovel(imovel_id):
    imovel = Imovel.query.get_or_404(imovel_id)
    return render_template('iptu/editar_imovel.html', imovel=imovel)

@bp.route('/novo', methods=['GET', 'POST'])
def novo_imovel():
    if request.method == 'POST':
        try:
            imovel = Imovel(
                inscricao=request.form['inscricao'],
                proprietario=request.form['proprietario'],
                endereco=request.form['endereco'],
                bairro=request.form['bairro'],
                cep=request.form['cep'],
                area_terreno=float(request.form['area_terreno']),
                area_construida=float(request.form['area_construida']),
                valor_venal=float(request.form['valor_venal']),
                tipo_imovel=request.form['tipo_imovel']
            )
            
            db.session.add(imovel)
            db.session.commit()
            
            flash('Imóvel cadastrado com sucesso!', 'success')
            return redirect(url_for('iptu.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar imóvel: {str(e)}', 'error')
            return render_template('iptu/novo_imovel.html')
    
    return render_template('iptu/novo_imovel.html') 

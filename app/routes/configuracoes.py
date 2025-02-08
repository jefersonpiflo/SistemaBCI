from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.models.configuracao_boleto import ConfiguracaoBoleto
from app import db

bp = Blueprint('configuracoes', __name__, url_prefix='/configuracoes')

@bp.route('/boleto', methods=['GET'])
def boleto():
    config = ConfiguracaoBoleto.query.filter_by(ativo=True).first()
    return render_template('configuracoes/boleto.html', config=config)

@bp.route('/boleto/salvar', methods=['POST'])
def salvar_boleto():
    try:
        # Desativar configuração anterior
        config_antiga = ConfiguracaoBoleto.query.filter_by(ativo=True).first()
        if config_antiga:
            config_antiga.ativo = False
            db.session.add(config_antiga)
        
        # Criar nova configuração
        config = ConfiguracaoBoleto(
            banco=request.form['banco'],
            agencia=request.form['agencia'],
            conta=request.form['conta'],
            carteira=request.form['carteira'],
            convenio=request.form['convenio'],
            cedente=request.form['cedente'],
            cedente_documento=request.form['cedente_documento'],
            local_pagamento=request.form['local_pagamento'],
            instrucoes=request.form['instrucoes'],
            especie=request.form.get('especie', 'R$'),
            moeda=request.form.get('moeda', 'BRL'),
            ativo=True
        )
        
        db.session.add(config)
        db.session.commit()
        
        flash('Configuração do boleto salva com sucesso!', 'success')
        return redirect(url_for('configuracoes.boleto'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao salvar configuração: {str(e)}', 'error')
        return redirect(url_for('configuracoes.boleto')) 
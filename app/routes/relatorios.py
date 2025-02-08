from flask import Blueprint, render_template, request, send_file
from flask_login import login_required
from app.utils.relatorios import GeradorRelatorio
from app.models.imovel import Imovel
from sqlalchemy import func
import pandas as pd
from io import BytesIO
from datetime import datetime, timedelta
from app.utils.relatorios_avancados import RelatorioAvancado
import os
from flask import current_app

bp = Blueprint('relatorios', __name__)

@bp.route('/relatorios')
@login_required
def index():
    return render_template('relatorios/index.html')

@bp.route('/relatorios/imoveis', methods=['GET', 'POST'])
@login_required
def imoveis():
    gerador = GeradorRelatorio()
    
    if request.method == 'POST':
        filtros = {
            'bairro': request.form.get('bairro'),
            'tipo': request.form.get('tipo'),
            'area_min': float(request.form.get('area_min')) if request.form.get('area_min') else None,
            'area_max': float(request.form.get('area_max')) if request.form.get('area_max') else None
        }
    else:
        filtros = None
    
    dados = gerador.relatorio_imoveis(filtros)
    bairros = db.session.query(Imovel.bairro).distinct().all()
    tipos = db.session.query(Imovel.tipo_imovel).distinct().all()
    
    return render_template('relatorios/imoveis.html',
                         dados=dados,
                         bairros=bairros,
                         tipos=tipos,
                         filtros=filtros)

@bp.route('/relatorios/vistorias', methods=['GET', 'POST'])
@login_required
def vistorias():
    gerador = GeradorRelatorio()
    
    if request.method == 'POST':
        periodo = {
            'inicio': datetime.strptime(request.form['data_inicio'], '%Y-%m-%d'),
            'fim': datetime.strptime(request.form['data_fim'], '%Y-%m-%d')
        }
    else:
        periodo = None
    
    dados = gerador.relatorio_vistorias(periodo)
    return render_template('relatorios/vistorias.html', dados=dados, periodo=periodo)

@bp.route('/relatorios/comparativo', methods=['GET', 'POST'])
@login_required
def comparativo():
    gerador = RelatorioAvancado()
    
    if request.method == 'POST':
        # Período atual
        data_inicio_atual = datetime.strptime(request.form['data_inicio_atual'], '%Y-%m-%d')
        data_fim_atual = datetime.strptime(request.form['data_fim_atual'], '%Y-%m-%d')
        
        # Período anterior
        data_inicio_anterior = datetime.strptime(request.form['data_inicio_anterior'], '%Y-%m-%d')
        data_fim_anterior = datetime.strptime(request.form['data_fim_anterior'], '%Y-%m-%d')
        
        dados_atual = gerador.relatorio_imoveis({
            'data_inicio': data_inicio_atual,
            'data_fim': data_fim_atual
        })
        
        dados_anterior = gerador.relatorio_imoveis({
            'data_inicio': data_inicio_anterior,
            'data_fim': data_fim_anterior
        })
        
        comparativo = gerador.comparativo_periodos(
            dados_anterior['dados_tabela'],
            dados_atual['dados_tabela']
        )
        
        kpis_atual = gerador.gerar_kpis(
            dados_atual['dados_tabela'],
            data_inicio_atual.strftime('%Y-%m')
        )
        
        kpis_anterior = gerador.gerar_kpis(
            dados_anterior['dados_tabela'],
            data_inicio_anterior.strftime('%Y-%m')
        )
        
        return render_template('relatorios/comparativo.html',
                             dados_atual=dados_atual,
                             dados_anterior=dados_anterior,
                             comparativo=comparativo,
                             kpis_atual=kpis_atual,
                             kpis_anterior=kpis_anterior)
    
    return render_template('relatorios/comparativo.html')

@bp.route('/relatorios/exportar/<tipo>/<formato>')
@login_required
def exportar(tipo, formato):
    gerador = RelatorioAvancado()
    
    if tipo == 'imoveis':
        dados = gerador.relatorio_imoveis()['dados_tabela']
    elif tipo == 'vistorias':
        dados = gerador.relatorio_vistorias()['dados_tabela']
    else:
        abort(404)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if formato == 'pdf':
        nome_arquivo = f'relatorio_{tipo}_{timestamp}.pdf'
        caminho_arquivo = os.path.join(current_app.config['UPLOAD_FOLDER'], nome_arquivo)
        gerador.exportar_pdf(dados, caminho_arquivo)
        return send_file(caminho_arquivo, as_attachment=True)
    
    elif formato == 'csv':
        nome_arquivo = f'relatorio_{tipo}_{timestamp}.csv'
        caminho_arquivo = os.path.join(current_app.config['UPLOAD_FOLDER'], nome_arquivo)
        gerador.exportar_csv(dados, caminho_arquivo)
        return send_file(caminho_arquivo, as_attachment=True)
    
    elif formato == 'excel':
        # Mantém a exportação Excel existente
        return exportar_excel(tipo)
    
    abort(404)

@bp.route('/relatorios/exportar/<tipo>')
@login_required
def exportar_excel(tipo):
    gerador = GeradorRelatorio()
    
    if tipo == 'imoveis':
        dados = gerador.relatorio_imoveis()['dados_tabela']
    elif tipo == 'vistorias':
        dados = gerador.relatorio_vistorias()['dados_tabela']
    else:
        abort(404)
    
    df = pd.DataFrame(dados)
    
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Dados', index=False)
    writer.close()
    output.seek(0)
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'relatorio_{tipo}_{datetime.now().strftime("%Y%m%d")}.xlsx'
    ) 
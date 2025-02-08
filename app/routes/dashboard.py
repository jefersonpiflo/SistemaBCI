from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from app import db
from app.models.imovel import Imovel
from app.models.vistoria import Vistoria
from app.models.auditoria import LogAuditoria
from sqlalchemy import func, desc, and_
from datetime import datetime, timedelta
import calendar
from collections import defaultdict

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@bp.route('/')
def index():
    # Buscar todos os imóveis
    imoveis = Imovel.query.all()
    
    # Estatísticas gerais
    total_imoveis = len(imoveis)
    total_area_terreno = sum(imovel.area_terreno or 0 for imovel in imoveis)
    total_area_construida = sum(imovel.area_construida or 0 for imovel in imoveis)
    total_valor_venal = sum(imovel.valor_venal or 0 for imovel in imoveis)
    total_iptu = sum((imovel.valor_venal or 0) * 0.02 for imovel in imoveis)  # Considerando alíquota de 2%
    
    # Distribuição por tipo de imóvel
    tipos_imovel = defaultdict(int)
    for imovel in imoveis:
        tipos_imovel[imovel.tipo_imovel] += 1
    
    # Média de valor venal por tipo
    media_valor_por_tipo = defaultdict(float)
    contagem_por_tipo = defaultdict(int)
    for imovel in imoveis:
        if imovel.valor_venal:
            media_valor_por_tipo[imovel.tipo_imovel] += imovel.valor_venal
            contagem_por_tipo[imovel.tipo_imovel] += 1
    
    for tipo in media_valor_por_tipo:
        if contagem_por_tipo[tipo] > 0:
            media_valor_por_tipo[tipo] = media_valor_por_tipo[tipo] / contagem_por_tipo[tipo]
    
    # Distribuição por bairro
    imoveis_por_bairro = defaultdict(int)
    valor_por_bairro = defaultdict(float)
    for imovel in imoveis:
        imoveis_por_bairro[imovel.bairro] += 1
        valor_por_bairro[imovel.bairro] += imovel.valor_venal or 0
    
    # Imóveis recentes (últimos 30 dias)
    data_limite = datetime.now() - timedelta(days=30)
    imoveis_recentes = [i for i in imoveis if i.data_cadastro >= data_limite]
    
    return render_template('dashboard/index.html',
                         imoveis=imoveis,
                         total_imoveis=total_imoveis,
                         total_area_terreno=total_area_terreno,
                         total_area_construida=total_area_construida,
                         total_valor_venal=total_valor_venal,
                         total_iptu=total_iptu,
                         tipos_imovel=dict(tipos_imovel),
                         media_valor_por_tipo=dict(media_valor_por_tipo),
                         imoveis_por_bairro=dict(imoveis_por_bairro),
                         valor_por_bairro=dict(valor_por_bairro),
                         imoveis_recentes=imoveis_recentes)

@bp.route('/dashboard/dados-mapa')
@login_required
def dados_mapa():
    imoveis = db.session.query(
        Imovel.latitude,
        Imovel.longitude,
        Imovel.tipo_imovel,
        func.count(Imovel.id)
    ).filter(
        Imovel.latitude.isnot(None),
        Imovel.longitude.isnot(None)
    ).group_by(
        Imovel.latitude,
        Imovel.longitude,
        Imovel.tipo_imovel
    ).all()
    
    return jsonify([{
        'lat': float(i[0]),
        'lng': float(i[1]),
        'tipo': i[2],
        'quantidade': i[3]
    } for i in imoveis]) 
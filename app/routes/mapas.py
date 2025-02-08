from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from app.models.imovel import Imovel

bp = Blueprint('mapas', __name__)

@bp.route('/mapa')
@login_required
def index():
    return render_template('mapas/index.html')

@bp.route('/api/imoveis/geo')
@login_required
def imoveis_geo():
    imoveis = Imovel.query.filter(
        Imovel.latitude.isnot(None),
        Imovel.longitude.isnot(None)
    ).all()
    
    features = [{
        'type': 'Feature',
        'geometry': {
            'type': 'Point',
            'coordinates': [imovel.longitude, imovel.latitude]
        },
        'properties': {
            'id': imovel.id,
            'inscricao': imovel.inscricao_imobiliaria,
            'endereco': f'{imovel.logradouro}, {imovel.numero}',
            'tipo': imovel.tipo_imovel
        }
    } for imovel in imoveis]
    
    return jsonify({
        'type': 'FeatureCollection',
        'features': features
    }) 
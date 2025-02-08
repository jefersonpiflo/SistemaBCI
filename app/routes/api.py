from flask import Blueprint, jsonify, request
from flask_login import login_required
from app.models.imovel import Imovel
from app.models.historico import HistoricoImovel
from app import db
from functools import wraps
import jwt
from datetime import datetime, timedelta

bp = Blueprint('api', __name__, url_prefix='/api/v1')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token não fornecido'}), 401
        
        try:
            token = token.split(' ')[1]
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = Usuario.query.get(data['user_id'])
        except:
            return jsonify({'message': 'Token inválido'}), 401
            
        return f(current_user, *args, **kwargs)
    return decorated

@bp.route('/imoveis', methods=['GET'])
@token_required
def get_imoveis(current_user):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    imoveis = Imovel.query.paginate(page=page, per_page=per_page)
    
    return jsonify({
        'imoveis': [{
            'id': i.id,
            'inscricao': i.inscricao_imobiliaria,
            'logradouro': i.logradouro,
            'numero': i.numero,
            'bairro': i.bairro,
            'area_construida': i.area_construida,
            'valor_venal': i.valor_venal,
            'proprietario': i.proprietario_nome
        } for i in imoveis.items],
        'total': imoveis.total,
        'pages': imoveis.pages,
        'current_page': imoveis.page
    })

@bp.route('/imoveis/<int:id>', methods=['GET'])
@token_required
def get_imovel(current_user, id):
    imovel = Imovel.query.get_or_404(id)
    return jsonify({
        'id': imovel.id,
        'inscricao': imovel.inscricao_imobiliaria,
        'logradouro': imovel.logradouro,
        'numero': imovel.numero,
        'bairro': imovel.bairro,
        'area_terreno': imovel.area_terreno,
        'area_construida': imovel.area_construida,
        'valor_venal': imovel.valor_venal,
        'tipo_imovel': imovel.tipo_imovel,
        'proprietario': {
            'nome': imovel.proprietario_nome,
            'cpf': imovel.proprietario_cpf,
            'email': imovel.proprietario_email,
            'telefone': imovel.proprietario_telefone
        }
    })

@bp.route('/auth/token', methods=['POST'])
def get_token():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('senha'):
        return jsonify({'message': 'Dados inválidos'}), 400
        
    usuario = Usuario.query.filter_by(email=data['email']).first()
    
    if not usuario or not usuario.check_senha(data['senha']):
        return jsonify({'message': 'Credenciais inválidas'}), 401
    
    token = jwt.encode({
        'user_id': usuario.id,
        'exp': datetime.utcnow() + timedelta(days=1)
    }, current_app.config['SECRET_KEY'])
    
    return jsonify({'token': token}) 
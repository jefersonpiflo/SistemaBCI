from app import db
from datetime import datetime

class HistoricoImovel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    imovel_id = db.Column(db.Integer, db.ForeignKey('imovel.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    data_alteracao = db.Column(db.DateTime, default=datetime.utcnow)
    tipo_alteracao = db.Column(db.String(50), nullable=False)  # 'criação', 'atualização', 'exclusão'
    campo_alterado = db.Column(db.String(50))
    valor_anterior = db.Column(db.String(200))
    valor_novo = db.Column(db.String(200))
    
    # Relacionamentos
    imovel = db.relationship('Imovel', backref='historicos')
    usuario = db.relationship('Usuario', backref='alteracoes_realizadas') 
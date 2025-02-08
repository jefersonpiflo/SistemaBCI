from app import db
from datetime import datetime

class Notificacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    titulo = db.Column(db.String(100), nullable=False)
    mensagem = db.Column(db.Text, nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    lida = db.Column(db.Boolean, default=False)
    tipo = db.Column(db.String(50))  # 'sistema', 'imovel', 'iptu'
    link = db.Column(db.String(200))
    
    # Relacionamento
    usuario = db.relationship('Usuario', backref='notificacoes') 
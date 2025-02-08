from app import db
from datetime import datetime

class Vistoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_agendada = db.Column(db.DateTime, nullable=False)
    data_realizada = db.Column(db.DateTime)
    status = db.Column(db.String(20), nullable=False, default='agendada')  # agendada, realizada, cancelada
    tipo_vistoria = db.Column(db.String(20), nullable=False)  # inicial, regular, denúncia
    observacoes = db.Column(db.Text)
    
    # Chave estrangeira para Imóvel
    imovel_id = db.Column(db.Integer, db.ForeignKey('imovel.id'), nullable=False)
    
    # Metadados
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Vistoria {self.id} - Imóvel {self.imovel_id}>'

class FotoVistoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vistoria_id = db.Column(db.Integer, db.ForeignKey('vistoria.id'), nullable=False)
    arquivo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.String(200))
    data_upload = db.Column(db.DateTime, default=datetime.utcnow) 
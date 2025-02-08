from app import db
from datetime import datetime
import json

class LogAuditoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_hora = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    ip_address = db.Column(db.String(45))
    acao = db.Column(db.String(50))  # login, logout, criar, editar, excluir, visualizar
    modulo = db.Column(db.String(50))  # imovel, vistoria, iptu, etc
    entidade_id = db.Column(db.Integer)
    dados_anteriores = db.Column(db.Text)
    dados_novos = db.Column(db.Text)
    detalhes = db.Column(db.Text)
    
    # Relacionamento
    usuario = db.relationship('Usuario', backref='logs_auditoria')
    
    @staticmethod
    def registrar(usuario_id, ip_address, acao, modulo, entidade_id=None, 
                 dados_anteriores=None, dados_novos=None, detalhes=None):
        log = LogAuditoria(
            usuario_id=usuario_id,
            ip_address=ip_address,
            acao=acao,
            modulo=modulo,
            entidade_id=entidade_id,
            dados_anteriores=json.dumps(dados_anteriores) if dados_anteriores else None,
            dados_novos=json.dumps(dados_novos) if dados_novos else None,
            detalhes=detalhes
        )
        db.session.add(log)
        db.session.commit()
        return log 
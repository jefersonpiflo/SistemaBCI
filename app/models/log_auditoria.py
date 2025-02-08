from app import db
from datetime import datetime

class LogAuditoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    acao = db.Column(db.String(50), nullable=False)
    tabela = db.Column(db.String(50), nullable=False)
    registro_id = db.Column(db.Integer)
    detalhes = db.Column(db.Text)
    
    # Chave estrangeira para o usuário
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

    def __repr__(self):
        return f'<LogAuditoria {self.acao} {self.tabela} {self.data}>' 
from app import db
from datetime import datetime

class AgendamentoVistoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    imovel_id = db.Column(db.Integer, db.ForeignKey('imovel.id'), nullable=False)
    fiscal_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    data_agendada = db.Column(db.DateTime, nullable=False)
    tipo_vistoria = db.Column(db.String(50), nullable=False)  # regular, denuncia, obra
    prioridade = db.Column(db.String(20), default='normal')  # baixa, normal, alta, urgente
    status = db.Column(db.String(20), default='agendada')
    motivo = db.Column(db.Text)
    observacoes = db.Column(db.Text)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Campos para controle de reagendamento
    reagendamentos = db.Column(db.Integer, default=0)
    data_anterior = db.Column(db.DateTime)
    motivo_reagendamento = db.Column(db.Text)
    
    # Relacionamentos
    imovel = db.relationship('Imovel', backref='agendamentos')
    fiscal = db.relationship('Usuario', backref='vistorias_agendadas')
    
    def reagendar(self, nova_data, motivo):
        self.data_anterior = self.data_agendada
        self.data_agendada = nova_data
        self.motivo_reagendamento = motivo
        self.reagendamentos += 1 
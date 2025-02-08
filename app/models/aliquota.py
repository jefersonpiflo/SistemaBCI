from app import db
from datetime import datetime

class Aliquota(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo_imovel = db.Column(db.String(20), nullable=False)  # residencial, comercial, industrial, terreno
    padrao_construcao = db.Column(db.String(20), nullable=True)  # baixo, normal, alto
    valor = db.Column(db.Float, nullable=False)  # valor em porcentagem
    data_inicio = db.Column(db.Date, nullable=False)
    data_fim = db.Column(db.Date)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    ativo = db.Column(db.Boolean, default=True)
    observacao = db.Column(db.Text)
    
    # Metadados
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Aliquota {self.tipo_imovel} - {self.valor}%>'
    
    @staticmethod
    def get_aliquota_atual(tipo_imovel, padrao_construcao=None):
        """Retorna a alíquota atual para o tipo de imóvel e padrão"""
        hoje = datetime.now().date()
        query = Aliquota.query.filter(
            Aliquota.tipo_imovel == tipo_imovel,
            Aliquota.data_inicio <= hoje,
            (Aliquota.data_fim >= hoje) | (Aliquota.data_fim.is_(None)),
            Aliquota.ativo == True
        )
        
        if padrao_construcao:
            query = query.filter(Aliquota.padrao_construcao == padrao_construcao)
        else:
            query = query.filter(Aliquota.padrao_construcao.is_(None))
            
        aliquota = query.first()
        return aliquota.valor if aliquota else 1.0  # retorna 1% como padrão 
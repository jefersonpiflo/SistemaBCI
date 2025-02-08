from datetime import datetime
from app import db

class Imovel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    inscricao = db.Column(db.String(20), unique=True, nullable=False)
    proprietario = db.Column(db.String(100), nullable=False)
    endereco = db.Column(db.String(200), nullable=False)
    bairro = db.Column(db.String(100), nullable=False)
    cep = db.Column(db.String(8))
    area_terreno = db.Column(db.Float)
    area_construida = db.Column(db.Float)
    valor_venal = db.Column(db.Float)
    tipo_imovel = db.Column(db.String(20), nullable=False)  # Mudando de 'tipo' para 'tipo_imovel'
    valor_iptu = db.Column(db.Float)  # Adicionando campo para valor do IPTU
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    ativo = db.Column(db.Boolean, default=True)
    
    # Relacionamentos
    vistorias = db.relationship('Vistoria', backref='imovel', lazy=True)
    
    def __repr__(self):
        return f'<Imovel {self.inscricao}>'
    
    def calcular_iptu(self, aliquota=None):
        """Calcula o IPTU do imóvel"""
        from app.models.aliquota import Aliquota
        
        if aliquota is None:
            # Busca a alíquota atual para o tipo do imóvel
            aliquota = Aliquota.get_aliquota_atual(self.tipo_imovel)
        
        return (self.valor_venal * aliquota) / 100
    
    def to_dict(self):
        """Retorna uma representação em dicionário do imóvel"""
        return {
            'id': self.id,
            'inscricao': self.inscricao,
            'tipo': self.tipo_imovel,
            'area_terreno': self.area_terreno,
            'area_construida': self.area_construida,
            'valor_venal': self.valor_venal,
            'endereco': self.endereco,
            'bairro': self.bairro,
            'cep': self.cep
        }

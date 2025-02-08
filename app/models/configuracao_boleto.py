from app import db
from datetime import datetime

class ConfiguracaoBoleto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    banco = db.Column(db.String(50), nullable=False)
    agencia = db.Column(db.String(10), nullable=False)
    conta = db.Column(db.String(20), nullable=False)
    carteira = db.Column(db.String(10), nullable=False)
    convenio = db.Column(db.String(20), nullable=False)
    cedente = db.Column(db.String(100), nullable=False)
    cedente_documento = db.Column(db.String(20), nullable=False)
    local_pagamento = db.Column(db.String(250), nullable=False)
    instrucoes = db.Column(db.Text)
    especie = db.Column(db.String(20), default='R$')
    moeda = db.Column(db.String(3), default='BRL')
    nosso_numero_sequencia = db.Column(db.Integer, default=1)  # Para gerar números sequenciais
    nosso_numero_formato = db.Column(db.String(20), default='%08d')  # Formato do nosso número
    codigo_beneficiario = db.Column(db.String(20))  # Código do beneficiário no banco
    tipo_cobranca = db.Column(db.String(10), default='SIMPLES')  # SIMPLES, REGISTRADA
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    ativo = db.Column(db.Boolean, default=True)

    def gerar_nosso_numero(self):
        """Gera o próximo número sequencial"""
        numero = self.nosso_numero_sequencia
        self.nosso_numero_sequencia += 1
        return self.nosso_numero_formato % numero

    def __repr__(self):
        return f'<ConfiguracaoBoleto {self.banco} - {self.cedente}>' 
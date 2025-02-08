from app import create_app, db
from app.models.usuario import Usuario
from app.models.imovel import Imovel
from app.models.vistoria import Vistoria
from app.models.aliquota import Aliquota
from app.models.configuracao_boleto import ConfiguracaoBoleto
from datetime import datetime, date

app = create_app()

with app.app_context():
    # Criar todas as tabelas
    db.drop_all()  # Limpa o banco de dados
    db.create_all()  # Cria todas as tabelas
    
    # Criar usuário admin
    admin = Usuario(
        nome='Administrador',
        email='admin@bci.com',
        tipo='admin'
    )
    admin.set_senha('admin123')
    db.session.add(admin)
    
    # Criar alíquotas padrão
    aliquotas = [
        Aliquota(
            tipo_imovel='residencial',
            valor=1.0,
            data_inicio=date(2024, 1, 1),
            ativo=True
        ),
        Aliquota(
            tipo_imovel='comercial',
            valor=2.0,
            data_inicio=date(2024, 1, 1),
            ativo=True
        ),
        Aliquota(
            tipo_imovel='industrial',
            valor=2.5,
            data_inicio=date(2024, 1, 1),
            ativo=True
        ),
        Aliquota(
            tipo_imovel='terreno',
            valor=3.0,
            data_inicio=date(2024, 1, 1),
            ativo=True
        )
    ]
    
    for aliquota in aliquotas:
        db.session.add(aliquota)
    
    # Adicionar configuração padrão do boleto
    config_boleto = ConfiguracaoBoleto(
        banco='001',  # Código do Banco do Brasil
        agencia='1234',
        conta='123456',
        carteira='17',
        convenio='123456',
        cedente='Prefeitura Municipal',
        cedente_documento='00.000.000/0001-00',
        local_pagamento='Pagável em qualquer banco até o vencimento',
        instrucoes='Após o vencimento cobrar multa de 2% e juros de 1% ao mês.\nNão receber após 60 dias de atraso.',
        especie='R$',
        moeda='BRL',
        ativo=True
    )
    db.session.add(config_boleto)
    
    # Criar alguns imóveis de teste
    imoveis = [
        Imovel(
            inscricao='123456',
            proprietario='João Silva',
            endereco='Rua A, 123',
            bairro='Centro',
            cep='12345678',
            area_terreno=250.0,
            area_construida=150.0,
            valor_venal=200000.0,
            tipo_imovel='residencial'
        ),
        Imovel(
            inscricao='234567',
            proprietario='Maria Santos',
            endereco='Av B, 456',
            bairro='Jardim',
            cep='87654321',
            area_terreno=500.0,
            area_construida=300.0,
            valor_venal=500000.0,
            tipo_imovel='comercial'
        ),
        Imovel(
            inscricao='345678',
            proprietario='Pedro Costa',
            endereco='Rua C, 789',
            bairro='Industrial',
            cep='23456789',
            area_terreno=1000.0,
            area_construida=0.0,
            valor_venal=300000.0,
            tipo_imovel='terreno'
        )
    ]
    
    for imovel in imoveis:
        db.session.add(imovel)
    
    # Commit das alterações
    db.session.commit()
    
    print("Banco de dados inicializado com sucesso!") 
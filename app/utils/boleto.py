from datetime import datetime
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import mm, inch
from reportlab.lib import colors
from decimal import Decimal
from .boleto_utils import calcular_fator_vencimento, gerar_linha_digitavel, formatar_linha_digitavel
from reportlab.graphics.barcode.code128 import Code128

class GeradorBoleto:
    def __init__(self, dados, config):
        self.dados = dados
        self.config = config
        
    def gerar(self):
        """Gera um boleto bancário em PDF"""
        # Cria o diretório temporário se não existir
        if not os.path.exists('tmp'):
            os.makedirs('tmp')
        
        # Nome do arquivo
        nome_arquivo = f'tmp/boleto_{datetime.now().strftime("%Y%m%d%H%M%S")}.pdf'
        
        # Cria o PDF
        c = canvas.Canvas(nome_arquivo, pagesize=A4)
        
        # Posições base
        x1, y1 = 50, 750  # Primeira coluna
        x2, y2 = 300, 750  # Segunda coluna
        
        # Dados do cedente
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x1, y1, self.config.banco)
        c.setFont("Helvetica", 10)
        c.drawString(x1, y1-20, f"Cedente: {self.config.cedente}")
        c.drawString(x1, y1-40, f"CNPJ: {self.config.cedente_documento}")
        c.drawString(x1, y1-60, f"Agência/Código: {self.config.agencia}/{self.config.conta}")
        
        # Dados do pagamento
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x2, y2, "Dados do Pagamento")
        c.setFont("Helvetica", 10)
        c.drawString(x2, y2-20, f"Valor: R$ {self.dados['valor']:.2f}")
        c.drawString(x2, y2-40, f"Vencimento: {self.dados['vencimento'].strftime('%d/%m/%Y')}")
        c.drawString(x2, y2-60, f"Nº Documento: {self.dados['numero_documento']}")
        
        # Dados do sacado
        c.setFont("Helvetica", 10)
        c.drawString(x1, y1-100, f"Sacado: {self.dados['sacado']}")
        c.drawString(x1, y1-120, f"Parcela: {self.dados.get('parcela', '1/1')}")
        
        # Local de pagamento e instruções
        c.drawString(x1, y1-160, f"Local de Pagamento: {self.config.local_pagamento}")
        
        # Instruções - quebra em várias linhas se necessário
        y_instrucoes = y1-200
        for linha in self.config.instrucoes.split('\n'):
            c.drawString(x1, y_instrucoes, linha)
            y_instrucoes -= 15
        
        # Finaliza o PDF
        c.save()
        return nome_arquivo

def desenhar_linha_horizontal(canvas, y, x_start=20*mm, x_end=190*mm):
    canvas.line(x_start, y, x_end, y)

def desenhar_linha_vertical(canvas, x, y_start, y_end):
    canvas.line(x, y_start, x, y_end)

def gerar_boleto(dados_boleto, config_boleto):
    """Gera um boleto bancário em PDF com código de barras"""
    # Criar diretório temporário
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    tmp_dir = os.path.join(base_dir, 'tmp')
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    
    # Nome do arquivo
    filename = os.path.join(tmp_dir, f'boleto_{datetime.now().strftime("%Y%m%d%H%M%S")}.pdf')
    
    # Criar PDF
    c = canvas.Canvas(filename, pagesize=A4)
    
    # Margens e posições base
    margin_left = 20*mm
    margin_top = 280*mm
    
    # Desenhar linhas do recibo do sacado
    desenhar_linha_horizontal(c, margin_top - 40*mm)  # Linha superior
    
    # Cabeçalho do boleto
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin_left, margin_top - 10*mm, f"{config_boleto.banco} - Recibo do Pagador")
    
    # Dados do cedente
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin_left, margin_top - 20*mm, "Cedente")
    c.setFont("Helvetica", 10)
    c.drawString(margin_left + 50*mm, margin_top - 20*mm, config_boleto.cedente)
    
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin_left + 120*mm, margin_top - 20*mm, "CNPJ")
    c.setFont("Helvetica", 10)
    c.drawString(margin_left + 140*mm, margin_top - 20*mm, config_boleto.cedente_documento)
    
    # Dados do documento
    y_doc = margin_top - 60*mm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin_left, y_doc, "Data do Documento")
    c.drawString(margin_left + 50*mm, y_doc, "Número do Documento")
    c.drawString(margin_left + 100*mm, y_doc, "Valor")
    c.drawString(margin_left + 140*mm, y_doc, "Vencimento")
    
    c.setFont("Helvetica", 10)
    c.drawString(margin_left, y_doc - 5*mm, datetime.now().strftime('%d/%m/%Y'))
    c.drawString(margin_left + 50*mm, y_doc - 5*mm, dados_boleto['numero_documento'])
    c.drawString(margin_left + 100*mm, y_doc - 5*mm, f"R$ {dados_boleto['valor']:.2f}")
    c.drawString(margin_left + 140*mm, y_doc - 5*mm, dados_boleto['vencimento'].strftime('%d/%m/%Y'))
    
    # Dados do pagador
    y_pagador = margin_top - 80*mm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin_left, y_pagador, "Pagador")
    c.setFont("Helvetica", 10)
    c.drawString(margin_left + 50*mm, y_pagador, dados_boleto['sacado'])
    
    # Instruções
    y_instrucoes = margin_top - 100*mm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin_left, y_instrucoes, "Instruções")
    c.setFont("Helvetica", 8)
    y_atual = y_instrucoes - 5*mm
    for linha in config_boleto.instrucoes.split('\n'):
        c.drawString(margin_left, y_atual, linha)
        y_atual -= 4*mm
    
    # Linha digitável e código de barras
    y_codigo = margin_top - 140*mm
    
    # Gerar código de barras
    valor = str(int(dados_boleto['valor'] * 100)).zfill(10)
    fator = str(calcular_fator_vencimento(dados_boleto['vencimento'])).zfill(4)
    nosso_numero = config_boleto.gerar_nosso_numero().zfill(11)
    
    linha = gerar_linha_digitavel(
        config_boleto.banco,
        '9',  # moeda (Real)
        fator,
        valor,
        config_boleto.agencia.zfill(4),
        config_boleto.conta.zfill(10),
        nosso_numero,
        config_boleto.carteira.zfill(2)
    )
    
    # Desenhar linha digitável
    c.setFont("Courier-Bold", 12)
    linha_formatada = formatar_linha_digitavel(linha)
    c.drawString(margin_left, y_codigo, linha_formatada)
    
    # Desenhar código de barras
    barcode = Code128(linha, barWidth=0.3*mm, barHeight=13*mm)
    barcode.drawOn(c, margin_left, y_codigo - 20*mm)
    
    # Informações adicionais
    c.setFont("Helvetica", 8)
    c.drawString(margin_left, y_codigo - 35*mm, "Autenticação Mecânica")
    
    # Linha final
    desenhar_linha_horizontal(c, y_codigo - 40*mm)
    
    # Adicionar marca de tesoura
    c.setDash(1, 2)
    c.setLineWidth(0.2)
    desenhar_linha_horizontal(c, margin_top, x_start=10*mm, x_end=15*mm)
    c.drawString(5*mm, margin_top - 3*mm, "✂")
    
    # Finalizar PDF
    c.save()
    return filename 
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
from datetime import datetime

class DocumentoGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=30
        )

    def gerar_bci(self, imovel):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []

        # Título
        elements.append(Paragraph(
            "Boletim de Cadastro Imobiliário (BCI)",
            self.title_style
        ))

        # Dados do Imóvel
        dados_imovel = [
            ["Inscrição Imobiliária:", imovel.inscricao_imobiliaria],
            ["Logradouro:", f"{imovel.logradouro}, {imovel.numero}"],
            ["Bairro:", imovel.bairro],
            ["CEP:", imovel.cep],
            ["Área do Terreno:", f"{imovel.area_terreno} m²"],
            ["Área Construída:", f"{imovel.area_construida} m²"],
            ["Valor Venal:", f"R$ {imovel.valor_venal:.2f}"],
            ["Tipo do Imóvel:", imovel.tipo_imovel.title()],
        ]

        table = Table(dados_imovel, colWidths=[150, 350])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)
        elements.append(Spacer(1, 20))

        # Dados do Proprietário
        elements.append(Paragraph("Dados do Proprietário", self.styles['Heading2']))
        dados_proprietario = [
            ["Nome:", imovel.proprietario_nome],
            ["CPF:", imovel.proprietario_cpf],
            ["Email:", imovel.proprietario_email or "-"],
            ["Telefone:", imovel.proprietario_telefone or "-"],
        ]

        table = Table(dados_proprietario, colWidths=[150, 350])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)

        # Rodapé
        elements.append(Spacer(1, 50))
        elements.append(Paragraph(
            f"Documento gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}",
            self.styles['Normal']
        ))

        doc.build(elements)
        buffer.seek(0)
        return buffer 
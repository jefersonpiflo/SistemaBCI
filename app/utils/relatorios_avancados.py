from app.utils.relatorios import GeradorRelatorio
import numpy as np
from scipy import stats
import seaborn as sns
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import csv

class RelatorioAvancado(GeradorRelatorio):
    def __init__(self):
        super().__init__()
        
    def analise_estatistica(self, dados):
        """Realiza análises estatísticas avançadas dos dados"""
        if not dados:
            return None
            
        valores = np.array([d['valor'] for d in dados])
        areas = np.array([d['area'] for d in dados])
        
        return {
            'valor_medio': np.mean(valores),
            'valor_mediano': np.median(valores),
            'valor_desvio': np.std(valores),
            'valor_quartis': np.percentile(valores, [25, 50, 75]),
            'area_media': np.mean(areas),
            'area_mediana': np.median(areas),
            'area_desvio': np.std(areas),
            'area_quartis': np.percentile(areas, [25, 50, 75]),
            'correlacao_valor_area': np.corrcoef(valores, areas)[0,1],
            'valor_m2_medio': np.mean(valores/areas)
        }
    
    def comparativo_periodos(self, dados_anterior, dados_atual):
        """Compara dados entre dois períodos"""
        stats_anterior = self.analise_estatistica(dados_anterior)
        stats_atual = self.analise_estatistica(dados_atual)
        
        if not stats_anterior or not stats_atual:
            return None
            
        return {
            'variacao_valor_medio': ((stats_atual['valor_medio'] - stats_anterior['valor_medio']) / 
                                   stats_anterior['valor_medio']) * 100,
            'variacao_area_media': ((stats_atual['area_media'] - stats_anterior['area_media']) / 
                                  stats_anterior['area_media']) * 100,
            'variacao_valor_m2': ((stats_atual['valor_m2_medio'] - stats_anterior['valor_m2_medio']) / 
                                stats_anterior['valor_m2_medio']) * 100
        }
    
    def gerar_kpis(self, dados, periodo=None):
        """Gera indicadores chave de desempenho"""
        total_imoveis = len(dados)
        if total_imoveis == 0:
            return None
            
        valores = [d['valor'] for d in dados]
        areas = [d['area'] for d in dados]
        
        return {
            'densidade_cadastral': total_imoveis / len(set(d['bairro'] for d in dados)),
            'valor_medio_m2': sum(v/a for v, a in zip(valores, areas)) / total_imoveis,
            'concentracao_tipo': max(
                len([d for d in dados if d['tipo'] == t]) / total_imoveis 
                for t in set(d['tipo'] for d in dados)
            ) * 100,
            'taxa_atualizacao': len([d for d in dados if d.get('data_atualizacao', '').startswith(periodo)]) / total_imoveis * 100 if periodo else None
        }
    
    def exportar_pdf(self, dados, nome_arquivo):
        """Exporta relatório em formato PDF"""
        doc = SimpleDocTemplate(nome_arquivo, pagesize=A4)
        elementos = []
        styles = getSampleStyleSheet()
        
        # Título
        elementos.append(Paragraph("Relatório de Análise Imobiliária", styles['Title']))
        elementos.append(Paragraph("<br/><br/>", styles['Normal']))
        
        # Estatísticas
        stats = self.analise_estatistica(dados)
        if stats:
            elementos.append(Paragraph("Análise Estatística", styles['Heading1']))
            tabela_dados = [
                ["Indicador", "Valor"],
                ["Valor Médio", f"R$ {stats['valor_medio']:.2f}"],
                ["Valor Mediano", f"R$ {stats['valor_mediano']:.2f}"],
                ["Desvio Padrão", f"R$ {stats['valor_desvio']:.2f}"],
                ["Valor m² Médio", f"R$ {stats['valor_m2_medio']:.2f}"]
            ]
            
            tabela = Table(tabela_dados)
            tabela.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elementos.append(tabela)
        
        doc.build(elementos)
    
    def exportar_csv(self, dados, nome_arquivo):
        """Exporta dados em formato CSV"""
        with open(nome_arquivo, 'w', newline='', encoding='utf-8') as arquivo:
            writer = csv.DictWriter(arquivo, fieldnames=dados[0].keys() if dados else [])
            writer.writeheader()
            writer.writerows(dados) 
from app import db
from app.models.imovel import Imovel
from app.models.vistoria import Vistoria
from app.models.agendamento import AgendamentoVistoria
from sqlalchemy import func, and_, or_
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64

class GeradorRelatorio:
    def __init__(self):
        self.plt = plt
        sns.set_style("whitegrid")
        
    def gerar_grafico(self, dados, tipo='bar', titulo='', xlabel='', ylabel=''):
        plt.figure(figsize=(10, 6))
        
        if tipo == 'bar':
            sns.barplot(x=dados.index, y=dados.values)
        elif tipo == 'pie':
            plt.pie(dados.values, labels=dados.index, autopct='%1.1f%%')
        elif tipo == 'line':
            sns.lineplot(data=dados)
            
        plt.title(titulo)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        
        # Salvar gráfico em memória
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        
        # Converter para base64
        graphic = base64.b64encode(image_png).decode('utf-8')
        plt.close()
        
        return graphic

    def relatorio_imoveis(self, filtros=None):
        query = db.session.query(Imovel)
        
        if filtros:
            if filtros.get('bairro'):
                query = query.filter(Imovel.bairro == filtros['bairro'])
            if filtros.get('tipo'):
                query = query.filter(Imovel.tipo_imovel == filtros['tipo'])
            if filtros.get('area_min'):
                query = query.filter(Imovel.area_construida >= filtros['area_min'])
            if filtros.get('area_max'):
                query = query.filter(Imovel.area_construida <= filtros['area_max'])
        
        imoveis = query.all()
        
        # Análises
        total_imoveis = len(imoveis)
        valor_total = sum(i.valor_venal for i in imoveis)
        area_media = sum(i.area_construida for i in imoveis) / total_imoveis if total_imoveis > 0 else 0
        
        # Distribuição por tipo
        tipos = pd.Series([i.tipo_imovel for i in imoveis]).value_counts()
        grafico_tipos = self.gerar_grafico(
            tipos, 
            tipo='pie',
            titulo='Distribuição por Tipo de Imóvel'
        )
        
        # Valor médio por bairro
        valores_bairro = pd.DataFrame([
            {'bairro': i.bairro, 'valor': i.valor_venal} 
            for i in imoveis
        ]).groupby('bairro')['valor'].mean()
        
        grafico_valores = self.gerar_grafico(
            valores_bairro,
            titulo='Valor Médio por Bairro',
            xlabel='Bairro',
            ylabel='Valor Médio (R$)'
        )
        
        return {
            'total_imoveis': total_imoveis,
            'valor_total': valor_total,
            'area_media': area_media,
            'grafico_tipos': grafico_tipos,
            'grafico_valores': grafico_valores,
            'dados_tabela': [
                {
                    'inscricao': i.inscricao_imobiliaria,
                    'tipo': i.tipo_imovel,
                    'area': i.area_construida,
                    'valor': i.valor_venal,
                    'bairro': i.bairro
                }
                for i in imoveis
            ]
        }

    def relatorio_vistorias(self, periodo=None):
        query = db.session.query(Vistoria)
        
        if periodo:
            data_inicio = periodo.get('inicio')
            data_fim = periodo.get('fim')
            if data_inicio and data_fim:
                query = query.filter(Vistoria.data_realizada.between(data_inicio, data_fim))
        
        vistorias = query.all()
        
        # Análises
        total_vistorias = len(vistorias)
        vistorias_por_status = pd.Series([v.status for v in vistorias]).value_counts()
        
        grafico_status = self.gerar_grafico(
            vistorias_por_status,
            tipo='pie',
            titulo='Distribuição por Status'
        )
        
        # Evolução temporal
        vistorias_tempo = pd.DataFrame([
            {'data': v.data_realizada, 'status': v.status}
            for v in vistorias if v.data_realizada
        ])
        if not vistorias_tempo.empty:
            vistorias_tempo['data'] = pd.to_datetime(vistorias_tempo['data'])
            evolucao = vistorias_tempo.groupby([
                vistorias_tempo['data'].dt.to_period('M'),
                'status'
            ]).size().unstack(fill_value=0)
            
            grafico_evolucao = self.gerar_grafico(
                evolucao,
                tipo='line',
                titulo='Evolução de Vistorias',
                xlabel='Mês',
                ylabel='Quantidade'
            )
        else:
            grafico_evolucao = None
        
        return {
            'total_vistorias': total_vistorias,
            'grafico_status': grafico_status,
            'grafico_evolucao': grafico_evolucao,
            'dados_tabela': [
                {
                    'data': v.data_realizada,
                    'imovel': v.imovel.inscricao_imobiliaria,
                    'fiscal': v.fiscal.nome,
                    'status': v.status,
                    'tipo': v.tipo_vistoria
                }
                for v in vistorias
            ]
        } 
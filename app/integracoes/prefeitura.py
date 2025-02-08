from .base import IntegracaoBase
import jwt
from datetime import datetime, timedelta

class IntegracaoPrefeitura(IntegracaoBase):
    def __init__(self, config):
        super().__init__(config)
        self.token = None
        self.base_url = config['PREFEITURA_API_URL']

    def autenticar(self):
        dados = {
            'client_id': self.config['PREFEITURA_CLIENT_ID'],
            'client_secret': self.config['PREFEITURA_CLIENT_SECRET']
        }
        response = self.fazer_requisicao(
            'POST',
            f'{self.base_url}/auth/token',
            dados=dados
        )
        self.token = response['access_token']
        return self.token

    def consultar_cadastro(self, inscricao):
        headers = {'Authorization': f'Bearer {self.token}'}
        return self.fazer_requisicao(
            'GET',
            f'{self.base_url}/imoveis/{inscricao}',
            headers=headers
        )

    def enviar_atualizacao(self, inscricao, dados):
        headers = {'Authorization': f'Bearer {self.token}'}
        return self.fazer_requisicao(
            'PUT',
            f'{self.base_url}/imoveis/{inscricao}',
            dados=dados,
            headers=headers
        )

    def sincronizar_iptu(self, inscricao, ano, valor):
        headers = {'Authorization': f'Bearer {self.token}'}
        dados = {
            'inscricao': inscricao,
            'ano': ano,
            'valor': valor,
            'data_calculo': datetime.now().isoformat()
        }
        return self.fazer_requisicao(
            'POST',
            f'{self.base_url}/iptu/sincronizar',
            dados=dados,
            headers=headers
        ) 
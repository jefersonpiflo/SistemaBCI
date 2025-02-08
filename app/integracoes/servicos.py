from .base import IntegracaoBase
import re

class ServicoCEP(IntegracaoBase):
    def __init__(self, config):
        super().__init__(config)
        self.base_url = 'https://viacep.com.br/ws'

    def autenticar(self):
        pass  # Não necessita autenticação

    def consultar_cep(self, cep):
        cep_limpo = re.sub(r'\D', '', cep)
        return self.fazer_requisicao(
            'GET',
            f'{self.base_url}/{cep_limpo}/json'
        )

class ServicoValidacao(IntegracaoBase):
    def __init__(self, config):
        super().__init__(config)
        self.token = config.get('VALIDACAO_TOKEN')

    def autenticar(self):
        pass  # Usa token fixo

    def validar_cpf(self, cpf):
        # Implementar validação real de CPF
        cpf_limpo = re.sub(r'\D', '', cpf)
        return len(cpf_limpo) == 11 and cpf_limpo != cpf_limpo[0] * 11

    def validar_cnpj(self, cnpj):
        # Implementar validação real de CNPJ
        cnpj_limpo = re.sub(r'\D', '', cnpj)
        return len(cnpj_limpo) == 14 and cnpj_limpo != cnpj_limpo[0] * 14 
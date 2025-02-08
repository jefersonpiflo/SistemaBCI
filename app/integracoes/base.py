from abc import ABC, abstractmethod
import requests
import json
import logging

class IntegracaoBase(ABC):
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def autenticar(self):
        pass

    def fazer_requisicao(self, metodo, url, dados=None, headers=None):
        try:
            response = requests.request(
                method=metodo,
                url=url,
                json=dados if dados else None,
                headers=headers if headers else {}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f'Erro na requisição: {str(e)}')
            raise 
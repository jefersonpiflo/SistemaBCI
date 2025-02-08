class CalculadoraIPTU:
    def __init__(self):
        self.aliquotas = {
            'residencial': {
                'padrao_alto': 0.004,    # 0.4%
                'padrao_medio': 0.003,   # 0.3%
                'padrao_baixo': 0.002    # 0.2%
            },
            'comercial': {
                'padrao_alto': 0.005,    # 0.5%
                'padrao_medio': 0.004,   # 0.4%
                'padrao_baixo': 0.003    # 0.3%
            },
            'industrial': 0.006,         # 0.6%
            'terreno': 0.007            # 0.7%
        }
        
        self.fatores_correcao = {
            'estado_conservacao': {
                'otimo': 1.0,
                'bom': 0.9,
                'regular': 0.8,
                'ruim': 0.7
            },
            'localizacao': {
                'zona_1': 1.2,
                'zona_2': 1.0,
                'zona_3': 0.8
            }
        }
    
    def calcular_valor_venal(self, area_construida, valor_m2, terreno_area, 
                            valor_m2_terreno, estado_conservacao, zona):
        # Valor da construção
        valor_construcao = area_construida * valor_m2 * \
                          self.fatores_correcao['estado_conservacao'][estado_conservacao]
        
        # Valor do terreno
        valor_terreno = terreno_area * valor_m2_terreno * \
                       self.fatores_correcao['localizacao'][zona]
        
        return valor_construcao + valor_terreno
    
    def calcular_iptu(self, valor_venal, tipo_imovel, padrao=None):
        if tipo_imovel in ['industrial', 'terreno']:
            aliquota = self.aliquotas[tipo_imovel]
        else:
            aliquota = self.aliquotas[tipo_imovel][f'padrao_{padrao}']
        
        return valor_venal * aliquota
    
    def simular_iptu(self, imovel, novo_valor_venal=None):
        valor_base = novo_valor_venal if novo_valor_venal else imovel.valor_venal
        
        return {
            'valor_venal': valor_base,
            'valor_iptu': self.calcular_iptu(
                valor_base,
                imovel.tipo_imovel,
                imovel.padrao_construcao
            ),
            'aliquota_aplicada': self.aliquotas[imovel.tipo_imovel] if imovel.tipo_imovel in ['industrial', 'terreno']
                                else self.aliquotas[imovel.tipo_imovel][f'padrao_{imovel.padrao_construcao}']
        } 
from datetime import datetime

def calcular_fator_vencimento(data_vencimento):
    """Calcula o fator de vencimento a partir da data base 07/10/1997"""
    data_base = datetime(1997, 10, 7)
    delta = data_vencimento.date() - data_base.date()
    return delta.days

def modulo11(num):
    """Calcula o dígito verificador usando módulo 11"""
    soma = 0
    peso = 2
    for c in reversed(str(num)):
        soma += int(c) * peso
        peso = peso + 1 if peso < 9 else 2
    dv = 11 - (soma % 11)
    return '0' if dv > 9 else str(dv)

def gerar_linha_digitavel(banco, moeda, fator_vencimento, valor, agencia, conta, nosso_numero, carteira):
    """Gera a linha digitável do boleto"""
    # Campo 1 - Código do banco, moeda, primeiros dígitos
    campo1 = f"{banco}{moeda}{carteira}{nosso_numero[:5]}"
    dv1 = modulo11(campo1)
    
    # Campo 2 - Restante do nosso número, início da conta
    campo2 = f"{nosso_numero[5:]}{conta[:7]}"
    dv2 = modulo11(campo2)
    
    # Campo 3 - Restante da conta, primeiro dígito verificador
    campo3 = f"{conta[7:]}{agencia}"
    dv3 = modulo11(campo3)
    
    # Campo 4 - DV geral (módulo 11)
    dv_geral = modulo11(f"{banco}{moeda}{fator_vencimento}{valor}{campo1}{campo2}{campo3}")
    
    # Campo 5 - Fator de vencimento e valor
    campo5 = f"{fator_vencimento}{valor}"
    
    linha = f"{campo1}{dv1}{campo2}{dv2}{campo3}{dv3}{dv_geral}{campo5}"
    return linha

def formatar_linha_digitavel(linha):
    """Formata a linha digitável com pontos e espaços"""
    return f"{linha[:5]}.{linha[5:10]} {linha[10:15]}.{linha[15:21]} {linha[21:26]}.{linha[26:32]} {linha[32]} {linha[33:]}" 
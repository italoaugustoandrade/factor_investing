"""
    Script que avalia a aplicação de magic fomula na bolsa brasileira.
    
"""
import pandas as pd
import quantstats as qs

dados_raw = pd.read_csv("dados_empresas.csv")
# Filtrar liquidez
dados_empresas = dados_raw[dados_raw['volume_negociado'] > 1000000]

# Split, aplly, combine
dados_empresas['retorno'] = dados_empresas.groupby(
    'ticker')['preco_fechamento_ajustado'].pct_change()
dados_empresas['retorno'] = dados_empresas.groupby('ticker')[
    'retorno'].shift(-1)

# evbit ev ao invés de ev_ebit para maior ficar melhor. Negativo ruim prejuízo.
dados_empresas['ranking_ebit_ev'] = dados_empresas.groupby(
    'data')['ebit_ev'].rank(ascending=False)

dados_empresas['ranking_roic'] = dados_empresas.groupby(
    'data')['roic'].rank(ascending=False)
dados_empresas['ranking_final'] = dados_empresas['ranking_ebit_ev'] + \
    dados_empresas['ranking_roic']
dados_empresas['ranking_final'] = dados_empresas.groupby('data')[
    'ranking_final'].rank()

dados_empresas = dados_empresas[dados_empresas['ranking_final'] <= 10]

rentabilidade_carteiras = dados_empresas.groupby('data')['retorno'].mean()
rentabilidade_carteiras = rentabilidade_carteiras.to_frame()

rentabilidade_carteiras['modelo_acumulado'] = (
    rentabilidade_carteiras['retorno'] + 1).cumprod() - 1
# Voltar a rentabilidade para a data correta.
rentabilidade_carteiras = rentabilidade_carteiras.shift(1)
rentabilidade_carteiras = rentabilidade_carteiras.dropna()


ibov = pd.read_csv('ibov.csv')

retorno_ibov = ibov['fechamento'].pct_change().dropna()
rentabilidade_carteiras['ibovespa_acumulado'] = (
    1 + retorno_ibov.values).cumprod() - 1
rentabilidade_carteiras = rentabilidade_carteiras.drop('retorno', axis=1)

qs.extend_pandas()
rentabilidade_carteiras.index = pd.to_datetime(rentabilidade_carteiras.index)

# rentabilidade_carteiras['modelo_acumulado'].plot_monthly_heatmap()
# rentabilidade_carteiras['ibovespa_acumulado'].plot_monthly_heatmap()

rentabilidade_carteiras.plot()
rentabilidade_ao_ano = (
    1 + rentabilidade_carteiras.loc['2023-06-30', 'modelo_acumulado']) ** (1/7.5) - 1  # anualizar taxa

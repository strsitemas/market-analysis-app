"""
Lista estatica de ativos disponiveis para selecao no frontend.

NOTA: isto e apenas um catalogo de tickers/nomes/setores para
popular a tela de selecao -- NAO contem nenhum dado financeiro
(preco, indicador, etc). Pode ser substituido futuramente por uma
tabela no banco ou por uma API de listagem da B3.
"""

ATIVOS_DISPONIVEIS = [
    {"ticker": "PETR4", "nome": "Petrobras", "setor": "Energia"},
    {"ticker": "VALE3", "nome": "Vale", "setor": "Materiais Basicos"},
    {"ticker": "ITUB4", "nome": "Itau Unibanco", "setor": "Financeiro"},
    {"ticker": "BBDC4", "nome": "Bradesco", "setor": "Financeiro"},
    {"ticker": "ABEV3", "nome": "Ambev", "setor": "Consumo"},
    {"ticker": "WEGE3", "nome": "WEG", "setor": "Industrial"},
    {"ticker": "MGLU3", "nome": "Magazine Luiza", "setor": "Varejo"},
    {"ticker": "B3SA3", "nome": "B3", "setor": "Financeiro"},
    {"ticker": "BBAS3", "nome": "Banco do Brasil", "setor": "Financeiro"},
    {"ticker": "RENT3", "nome": "Localiza", "setor": "Consumo"},
]
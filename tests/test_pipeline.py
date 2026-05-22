"""
Testes unitários para a skill Análise Processual Judicial.
"""
import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from analise_processual_judicial.extrair_dados import extrair_metadados, extrair_indice
from analise_processual_judicial.identificar_irregularidades import identificar_irregularidades
from analise_processual_judicial.estatisticas import calcular_estatisticas


def test_extrair_metadados():
    texto = """
Processo nº 1234567-89.2024.8.05.0001
Classe: Procedimento do Juizado Especial Cível
Assunto: Crédito Direto ao Consumidor - CDC
Prioridade: IDOSO(A) - 60 A 79 ANOS
Data da Distribuição: 01/01/2024
Valor da Causa: R$ 10.000,00
Segredo de Justiça: Não
Promovente(s):
JOSE DA SILVA
CPF 123.456.789-00
Promovido(s):
BANCO TESTE S A
CNPJ 12.345.678/0001-90
"""
    meta = extrair_metadados(texto)
    assert meta['numero_processo'] == '1234567-89.2024.8.05.0001'
    assert 'Juizado Especial' in meta['classe']
    assert meta['data_distribuicao'] == '01/01/2024'
    assert meta['valor_causa'] == 'R$ 10.000,00'
    assert meta['segredo_justica'] == 'Não'
    assert len(meta['partes']) >= 2


def test_identificar_irregularidades_citacao_atrasada():
    dados = {
        'metadados': {
            'classe': 'Procedimento do Juizado Especial Cível',
            'data_distribuicao': '01/01/2024',
            'prioridade': ''
        },
        'linha_do_tempo': [
            {'data': '01/01/2024', 'hora': '10:00', 'documento': 'PETICAO INICIAL.pdf', 'tipo': 'Petição Inicial', 'origem': 'indice'},
            {'data': '15/02/2024', 'hora': '10:00', 'documento': 'CITACAO', 'tipo': 'Citação', 'origem': 'indice'},
        ],
        'indice_documentos': [
            {'id': '1', 'data': '01/01/2024', 'hora': '10:00', 'documento': 'PETICAO INICIAL.pdf', 'tipo': 'Petição Inicial'},
            {'id': '2', 'data': '15/02/2024', 'hora': '10:00', 'documento': 'CITACAO', 'tipo': 'Citação'},
        ]
    }
    irregs = identificar_irregularidades(dados)
    assert len(irregs) >= 1
    assert any(i['categoria'] == 'CITAÇÃO' for i in irregs)


def test_identificar_irregularidades_sem_irregularidade():
    dados = {
        'metadados': {
            'classe': 'Procedimento Comum Cível',
            'data_distribuicao': '01/01/2024',
            'prioridade': ''
        },
        'linha_do_tempo': [
            {'data': '01/01/2024', 'hora': '10:00', 'documento': 'PETICAO INICIAL.pdf', 'tipo': 'Petição Inicial', 'origem': 'indice'},
            {'data': '05/01/2024', 'hora': '10:00', 'documento': 'CITACAO', 'tipo': 'Citação', 'origem': 'indice'},
        ],
        'indice_documentos': []
    }
    irregs = identificar_irregularidades(dados)
    # Sem irregularidades óbvias neste cenário mínimo
    assert isinstance(irregs, list)


def test_calcular_estatisticas():
    dados = {
        'metadados': {'numero_processo': 'TESTE'},
        'linha_do_tempo': [
            {'data': '01/01/2024', 'hora': '10:00', 'documento': 'A.pdf', 'tipo': 'Petição', 'origem': 'indice'},
            {'data': '15/01/2024', 'hora': '10:00', 'documento': 'B.pdf', 'tipo': 'Citação', 'origem': 'indice'},
            {'data': '01/02/2024', 'hora': '10:00', 'documento': 'C.pdf', 'tipo': 'Petição', 'origem': 'indice'},
        ],
        'irregularidades': []
    }
    stats = calcular_estatisticas(dados)
    assert stats['total_andamentos'] == 3
    assert stats['periodo_analisado']['duracao_dias'] == 31
    assert stats['indicadores']['media_movimentacoes_mes'] > 0

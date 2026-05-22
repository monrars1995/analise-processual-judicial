#!/usr/bin/env python3
"""
Extrai dados estruturados de PDF de processo judicial digital (PROJUDI, PJe, etc.).
Saída: JSON com metadados do processo, partes, índice de documentos e andamentos.
"""
import json
import re
import sys
from pathlib import Path
from datetime import datetime

try:
    import pdfplumber
except ImportError:
    print("Erro: pdfplumber não instalado. Execute: pip install pdfplumber")
    sys.exit(1)


def parse_data_br(data_str):
    try:
        return datetime.strptime(data_str, "%d/%m/%Y")
    except ValueError:
        return None


def extrair_metadados(text):
    """Extrai metadados da capa do processo."""
    meta = {}
    # Número do processo
    m = re.search(r'Processo n[º°]\s*([\d\.\-]+)', text)
    if m:
        meta['numero_processo'] = m.group(1)
    # Classe
    m = re.search(r'Classe:\s*([^\n]+)', text)
    if m:
        meta['classe'] = m.group(1).strip()
    # Assunto
    m = re.search(r'Assunto:\s*([^\n]+)', text)
    if m:
        meta['assunto'] = m.group(1).strip()
    # Prioridade
    m = re.search(r'Prioridade:\s*([^\n]+)', text)
    if m:
        meta['prioridade'] = m.group(1).strip()
    # Distribuição
    m = re.search(r'Data da Distribuição:\s*([\d/]+)', text)
    if m:
        meta['data_distribuicao'] = m.group(1)
    # Valor
    m = re.search(r'Valor da Causa:\s*([^\n]+)', text)
    if m:
        meta['valor_causa'] = m.group(1).strip()
    # Segredo
    m = re.search(r'Segredo de Justiça:\s*([^\n]+)', text)
    if m:
        meta['segredo_justica'] = m.group(1).strip()
    # Partes - promovente
    partes = []
    # Regex simples para promovente/promovido
    promovente_match = re.search(r'Promovente\(s\):\s*(.+?)(?=Promovido\(s\):)', text, re.DOTALL)
    if promovente_match:
        bloco = promovente_match.group(1)
        nomes = re.findall(r'^([A-Z][A-Z\s]+)(?=\s+(?:CPF|CNPJ|OAB|\d))', bloco, re.MULTILINE)
        for nome in nomes:
            nome_l = nome.strip()
            if len(nome_l) > 3:
                partes.append({'polo': 'ativo', 'nome': nome_l})
    promovido_match = re.search(r'Promovido\(s\):\s*(.+?)(?=Testemunha|Classe:|$)', text, re.DOTALL)
    if promovido_match:
        bloco = promovido_match.group(1)
        nomes = re.findall(r'^([A-Z][A-Z\s]+)(?=\s+(?:CPF|CNPJ|OAB|\d))', bloco, re.MULTILINE)
        for nome in nomes:
            nome_l = nome.strip()
            if len(nome_l) > 3:
                partes.append({'polo': 'passivo', 'nome': nome_l})
    meta['partes'] = partes
    return meta


def extrair_indice(pages):
    """Extrai índice de documentos das primeiras páginas."""
    itens = []
    for page in pages[:3]:
        text = page.extract_text()
        if not text:
            continue
        for line in text.split('\n'):
            # Padrão: ID DATA HORA NOME_DOC TIPO
            m = re.match(
                r'(\d+)\s+(\d{2}/\d{2}/\d{4})\s+(\d{2}:\d{2})\s+(.+?)\s+([A-Za-zÀ-ú\s\-\.]+)$',
                line.strip()
            )
            if m and len(m.group(1)) > 5:
                doc_id, date, time, filename, doc_type = m.groups()
                itens.append({
                    'id': doc_id.strip(),
                    'data': date.strip(),
                    'hora': time.strip(),
                    'documento': filename.strip(),
                    'tipo': doc_type.strip()
                })
    return itens


def extrair_andamentos_adicionais(pages):
    """Tenta extrair andamentos de movimentação do meio do PDF."""
    andamentos = []
    # Em PROJUDI, os andamentos costumam estar em páginas com headers específicos
    for i, page in enumerate(pages):
        text = page.extract_text()
        if not text:
            continue
        # Detecta padrões de despacho/decisão com data
        # Ex: "Salvador, 17 de Novembro de 2025" seguido de assinatura
        datas_assinatura = re.findall(r'(?:Salvador|Brasília|[A-Z][a-z]+),?\s+(\d{1,2})\s+de\s+([A-Za-zç]+)\s+de\s+(\d{4})', text)
        # Se página tem menos de 800 chars e tem data, pode ser ato simples
        if len(text) < 1200 and datas_assinatura:
            # Identifica tipo pelo conteúdo
            tipo = 'Ato'
            if 'DESPACHO' in text.upper():
                tipo = 'Despacho'
            elif 'DECISÃO' in text.upper():
                tipo = 'Decisão'
            elif 'SENTENÇA' in text.upper():
                tipo = 'Sentença'
            elif 'CERTIDÃO' in text.upper():
                tipo = 'Certidão'
            elif 'CITAÇÃO' in text.upper():
                tipo = 'Citação'
            elif 'CONCLUSÃO' in text.upper():
                tipo = 'Conclusão'
            for d, mes, ano in datas_assinatura:
                mes_num = {
                    'janeiro': '01', 'fevereiro': '02', 'março': '03', 'abril': '04',
                    'maio': '05', 'junho': '06', 'julho': '07', 'agosto': '08',
                    'setembro': '09', 'outubro': '10', 'novembro': '11', 'dezembro': '12'
                }.get(mes.lower(), '00')
                data_fmt = f"{d.zfill(2)}/{mes_num}/{ano}"
                andamentos.append({
                    'data': data_fmt,
                    'tipo': tipo,
                    'resumo': text[:300].replace('\n', ' '),
                    'fonte': f'pagina_{i+1}'
                })
    return andamentos


def main():
    if len(sys.argv) < 2:
        print("Uso: python extrair_dados.py <arquivo.pdf> [saida.json]")
        sys.exit(1)
    pdf_path = Path(sys.argv[1])
    saida = Path(sys.argv[2]) if len(sys.argv) > 2 else pdf_path.with_suffix('.json')

    with pdfplumber.open(str(pdf_path)) as pdf:
        texto_capa = pdf.pages[0].extract_text() or ""
        metadados = extrair_metadados(texto_capa)
        indice = extrair_indice(pdf.pages)
        andamentos = extrair_andamentos_adicionais(pdf.pages)

    resultado = {
        'fonte': str(pdf_path),
        'total_paginas': len(pdf.pages),
        'metadados': metadados,
        'indice_documentos': indice,
        'andamentos_detectados': andamentos,
        'linha_do_tempo': sorted(
            [{**item, 'origem': 'indice'} for item in indice] +
            [{**a, 'documento': a['resumo'][:80], 'origem': a['fonte']} for a in andamentos],
            key=lambda x: parse_data_br(x['data']) or datetime.min
        )
    }

    with open(saida, 'w', encoding='utf-8') as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
    print(f"Dados extraídos para: {saida}")


if __name__ == '__main__':
    main()

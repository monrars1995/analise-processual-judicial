#!/usr/bin/env python3
"""
Compara dois ou mais processos judiciais extraídos.
Útil para identificar padrões, diferenças de ritmo e comparação de irregularidades.
"""
import json
import sys
from pathlib import Path
from datetime import datetime
from collections import Counter


def parse_data(data_str):
    try:
        return datetime.strptime(data_str, "%d/%m/%Y")
    except ValueError:
        return None


def calcular_duracao(linha):
    datas = [parse_data(item['data']) for item in linha if parse_data(item['data'])]
    if len(datas) >= 2:
        return (max(datas) - min(datas)).days
    return 0


def comparar_processos(arquivos_json):
    processos = []
    for arq in arquivos_json:
        with open(arq, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        meta = dados.get('metadados', {})
        linha = dados.get('linha_do_tempo', [])
        irregs = dados.get('irregularidades', [])
        processos.append({
            'arquivo': Path(arq).name,
            'numero': meta.get('numero_processo', 'N/A'),
            'classe': meta.get('classe', 'N/A'),
            'assunto': meta.get('assunto', 'N/A'),
            'valor': meta.get('valor_causa', 'N/A'),
            'prioridade': meta.get('prioridade', ''),
            'total_andamentos': len(linha),
            'duracao_dias': calcular_duracao(linha),
            'tipos': Counter(item.get('tipo', 'Outros') for item in linha),
            'total_irregularidades': len(irregs),
            'irregularidades_alta': sum(1 for i in irregs if i['gravidade'] == 'ALTA'),
            'irregularidades_media': sum(1 for i in irregs if i['gravidade'] == 'MEDIA'),
            'irregularidades_baixa': sum(1 for i in irregs if i['gravidade'] == 'BAIXA'),
        })

    print("=" * 80)
    print("📊 COMPARAÇÃO DE PROCESSOS JUDICIAIS")
    print("=" * 80)

    # Tabela resumo
    print(f"\n{'Processo':<30} {'Andam.':<8} {'Dias':<8} {'Irregs':<8} {'Alta':<6} {'Média':<6} {'Baixa':<6}")
    print("-" * 80)
    for p in processos:
        print(f"{p['numero']:<30} {p['total_andamentos']:<8} {p['duracao_dias']:<8} {p['total_irregularidades']:<8} {p['irregularidades_alta']:<6} {p['irregularidades_media']:<6} {p['irregularidades_baixa']:<6}")

    # Destaques
    if len(processos) > 1:
        print("\n" + "=" * 80)
        print("🏆 DESTAQUES")
        print("=" * 80)
        mais_andamentos = max(processos, key=lambda x: x['total_andamentos'])
        menos_andamentos = min(processos, key=lambda x: x['total_andamentos'])
        mais_irregs = max(processos, key=lambda x: x['total_irregularidades'])
        mais_rapido = min(processos, key=lambda x: x['duracao_dias'] if x['duracao_dias'] > 0 else float('inf'))

        print(f"   📁 Mais andamentos:      {mais_andamentos['numero']} ({mais_andamentos['total_andamentos']})")
        print(f"   📁 Menos andamentos:     {menos_andamentos['numero']} ({menos_andamentos['total_andamentos']})")
        print(f"   ⚠️  Mais irregularidades: {mais_irregs['numero']} ({mais_irregs['total_irregularidades']})")
        print(f"   ⚡ Mais rápido:          {mais_rapido['numero']} ({mais_rapido['duracao_dias']} dias)")

    # Tipos de documento comparados
    print("\n" + "=" * 80)
    print("📋 TIPOS DE DOCUMENTO COMPARADOS")
    print("=" * 80)
    todos_tipos = set()
    for p in processos:
        todos_tipos.update(p['tipos'].keys())
    tipos_lista = sorted(todos_tipos)
    print(f"{'Tipo':<25} " + " ".join(f"{p['numero'][:12]:<14}" for p in processos))
    print("-" * 80)
    for t in tipos_lista:
        valores = [str(p['tipos'].get(t, 0)) for p in processos]
        print(f"{t:<25} " + " ".join(f"{v:<14}" for v in valores))

    print("\n" + "=" * 80)


def main():
    if len(sys.argv) < 3:
        print("Uso: python comparar.py <processo1.json> <processo2.json> [processoN.json ...]")
        sys.exit(1)
    comparar_processos(sys.argv[1:])


if __name__ == '__main__':
    main()

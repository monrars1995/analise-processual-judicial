#!/usr/bin/env python3
"""
Gera estatísticas quantitativas do processo judicial a partir do JSON extraído.
Útil para dashboards, comparativos e análise de produtividade processual.
"""
import json
import sys
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict


def parse_data(data_str):
    try:
        return datetime.strptime(data_str, "%d/%m/%Y")
    except ValueError:
        return None


def calcular_estatisticas(dados):
    linha = dados.get('linha_do_tempo', [])
    meta = dados.get('metadados', {})
    irregs = dados.get('irregularidades', [])

    if not linha:
        return {"erro": "Nenhum dado de linha do tempo encontrado."}

    # Datas parseadas
    datas = [(item, parse_data(item['data'])) for item in linha]
    datas_validas = [(item, dt) for item, dt in datas if dt]

    if not datas_validas:
        return {"erro": "Nenhuma data válida encontrada na linha do tempo."}

    datas_validas.sort(key=lambda x: x[1])
    primeira_data = datas_validas[0][1]
    ultima_data = datas_validas[-1][1]
    duracao_dias = (ultima_data - primeira_data).days

    # Contagem por tipo
    tipos = Counter(item.get('tipo', 'Desconhecido') for item, _ in datas_validas)

    # Andamentos por mês
    por_mes = defaultdict(int)
    for _, dt in datas_validas:
        por_mes[dt.strftime("%Y-%m")] += 1

    # Intervalos entre andamentos
    intervalos = []
    for i in range(1, len(datas_validas)):
        dias = (datas_validas[i][1] - datas_validas[i-1][1]).days
        intervalos.append(dias)

    media_intervalo = sum(intervalos) / len(intervalos) if intervalos else 0
    max_intervalo = max(intervalos) if intervalos else 0
    min_intervalo = min(intervalos) if intervalos else 0

    # Irregularidades por categoria e gravidade
    irreg_por_categoria = Counter(i['categoria'] for i in irregs)
    irreg_por_gravidade = Counter(i['gravidade'] for i in irregs)

    # Detecção de meses sem movimentação
    meses_sem_mov = []
    if duracao_dias > 60:
        meses_completos = set()
        for _, dt in datas_validas:
            meses_completos.add(dt.strftime("%Y-%m"))
        mes_atual = primeira_data
        while mes_atual <= ultima_data:
            chave = mes_atual.strftime("%Y-%m")
            if chave not in meses_completos:
                meses_sem_mov.append(chave)
            # Avança 1 mês
            if mes_atual.month == 12:
                mes_atual = mes_atual.replace(year=mes_atual.year + 1, month=1)
            else:
                mes_atual = mes_atual.replace(month=mes_atual.month + 1)

    return {
        "numero_processo": meta.get('numero_processo', 'N/A'),
        "total_andamentos": len(linha),
        "periodo_analisado": {
            "inicio": primeira_data.strftime("%d/%m/%Y"),
            "fim": ultima_data.strftime("%d/%m/%Y"),
            "duracao_dias": duracao_dias
        },
        "tipos_de_documento": dict(tipos.most_common(10)),
        "andamentos_por_mes": dict(sorted(por_mes.items())),
        "intervalos_entre_andamentos": {
            "media_dias": round(media_intervalo, 1),
            "maximo_dias": max_intervalo,
            "minimo_dias": min_intervalo
        },
        "meses_sem_movimentacao": meses_sem_mov,
        "irregularidades": {
            "total": len(irregs),
            "por_categoria": dict(irreg_por_categoria),
            "por_gravidade": dict(irreg_por_gravidade)
        },
        "indicadores": {
            "media_movimentacoes_mes": round(len(linha) / max(len(por_mes), 1), 1),
            "tempo_medio_entre_andamentos_dias": round(media_intervalo, 1),
            "meses_parados": len(meses_sem_mov)
        }
    }


def main():
    if len(sys.argv) < 2:
        print("Uso: python estatisticas.py <dados.json> [saida.json]")
        sys.exit(1)
    entrada = Path(sys.argv[1])
    saida = Path(sys.argv[2]) if len(sys.argv) > 2 else entrada.with_name(entrada.stem + '_estatisticas.json')

    with open(entrada, 'r', encoding='utf-8') as f:
        dados = json.load(f)

    stats = calcular_estatisticas(dados)

    with open(saida, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    print(f"Estatísticas calculadas: {stats['total_andamentos']} andamentos em {stats['periodo_analisado']['duracao_dias']} dias.")
    print(f"Salvo em: {saida}")


if __name__ == '__main__':
    main()

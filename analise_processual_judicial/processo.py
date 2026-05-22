#!/usr/bin/env python3
"""
CLI unificada da skill Análise Processual Judicial.
Substitui a execução de múltiplos scripts por um único comando.

Uso:
    python processo.py analisar <pdf> [pasta_saida]
    python processo.py extrair <pdf> [saida.json]
    python processo.py irregularidades <dados.json> [saida.json]
    python processo.py estatisticas <dados.json> [saida.json]
    python processo.py relatorio <dados.json> <irregularidades.json> [saida.pdf]
"""
import sys
import os
import subprocess
import argparse
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()


def run_script(name, *args):
    script = SCRIPT_DIR / f"{name}.py"
    if not script.exists():
        print(f"Erro: script não encontrado: {script}")
        sys.exit(1)
    cmd = [sys.executable, str(script)] + list(args)
    result = subprocess.run(cmd)
    return result.returncode


def cmd_analisar(args):
    pdf = Path(args.pdf)
    out_dir = Path(args.output) if args.output else Path.cwd()
    out_dir.mkdir(parents=True, exist_ok=True)

    base = out_dir / pdf.stem
    dados_json = base.with_suffix('.json')
    irregs_json = base.with_name(base.stem + '_irregularidades.json')
    stats_json = base.with_name(base.stem + '_estatisticas.json')
    relatorio_pdf = base.with_suffix('.pdf')

    print("=" * 60)
    print("📄 ANÁLISE PROCESSUAL JUDICIAL - PIPELINE COMPLETO")
    print("=" * 60)

    print(f"\n[1/4] Extraindo dados de: {pdf}")
    rc = run_script('extrair_dados', str(pdf), str(dados_json))
    if rc != 0:
        print("❌ Falha na extração.")
        sys.exit(rc)

    print(f"\n[2/4] Identificando irregularidades...")
    rc = run_script('identificar_irregularidades', str(dados_json), str(irregs_json))
    if rc != 0:
        print("❌ Falha na identificação de irregularidades.")
        sys.exit(rc)

    print(f"\n[3/4] Calculando estatísticas...")
    import json
    with open(dados_json, 'r', encoding='utf-8') as f:
        dados = json.load(f)
    with open(irregs_json, 'r', encoding='utf-8') as f:
        ir = json.load(f)
    dados['irregularidades'] = ir.get('irregularidades', [])
    merged = base.with_name(base.stem + '_merged.json')
    with open(merged, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    rc = run_script('estatisticas', str(merged), str(stats_json))
    if rc != 0:
        print("⚠️ Falha nas estatísticas (continuando).")

    print(f"\n[4/4] Gerando relatório PDF...")
    rc = run_script('gerar_relatorio', str(dados_json), str(irregs_json), str(relatorio_pdf))
    if rc != 0:
        print("❌ Falha na geração do PDF.")
        sys.exit(rc)

    print("\n" + "=" * 60)
    print("✅ ANÁLISE CONCLUÍDA")
    print("=" * 60)
    print(f"📁 Pasta de saída: {out_dir}")
    print(f"   • Dados:        {dados_json.name}")
    print(f"   • Irregularidades: {irregs_json.name}")
    print(f"   • Estatísticas: {stats_json.name}")
    print(f"   • Relatório PDF: {relatorio_pdf.name}")
    print("=" * 60)
    return 0


def main():
    parser = argparse.ArgumentParser(
        prog='processo.py',
        description='CLI unificada da skill Análise Processual Judicial'
    )
    subparsers = parser.add_subparsers(dest='command', required=True)

    # analisar
    p_analisar = subparsers.add_parser('analisar', help='Pipeline completo de análise')
    p_analisar.add_argument('pdf', help='Caminho do PDF do processo')
    p_analisar.add_argument('output', nargs='?', help='Pasta de saída (padrão: atual)')
    p_analisar.set_defaults(func=cmd_analisar)

    # extrair
    p_extrair = subparsers.add_parser('extrair', help='Extrair dados do PDF')
    p_extrair.add_argument('pdf', help='Caminho do PDF do processo')
    p_extrair.add_argument('output', nargs='?', help='Arquivo JSON de saída')
    p_extrair.set_defaults(func=lambda a: run_script('extrair_dados', a.pdf, a.output or 'processo.json'))

    # irregularidades
    p_irreg = subparsers.add_parser('irregularidades', help='Identificar irregularidades')
    p_irreg.add_argument('json', help='Arquivo JSON com dados extraídos')
    p_irreg.add_argument('output', nargs='?', help='Arquivo JSON de saída')
    p_irreg.set_defaults(func=lambda a: run_script('identificar_irregularidades', a.json, a.output or 'irregularidades.json'))

    # estatisticas
    p_stats = subparsers.add_parser('estatisticas', help='Gerar estatísticas')
    p_stats.add_argument('json', help='Arquivo JSON com dados extraídos')
    p_stats.add_argument('output', nargs='?', help='Arquivo JSON de saída')
    p_stats.set_defaults(func=lambda a: run_script('estatisticas', a.json, a.output or 'estatisticas.json'))

    # relatorio
    p_rel = subparsers.add_parser('relatorio', help='Gerar relatório PDF')
    p_rel.add_argument('dados', help='Arquivo JSON com dados extraídos')
    p_rel.add_argument('irregularidades', help='Arquivo JSON com irregularidades')
    p_rel.add_argument('output', nargs='?', help='Arquivo PDF de saída')
    p_rel.set_defaults(func=lambda a: run_script('gerar_relatorio', a.dados, a.irregularidades, a.output or 'relatorio.pdf'))

    # batch
    p_batch = subparsers.add_parser('batch', help='Processar todos os PDFs de uma pasta')
    p_batch.add_argument('pasta', help='Pasta com PDFs de processos')
    p_batch.add_argument('output', nargs='?', help='Pasta de saída (padrão: atual)')
    p_batch.set_defaults(func=cmd_batch)

    args = parser.parse_args()
    sys.exit(args.func(args))


def cmd_batch(args):
    pasta = Path(args.pasta)
    out_dir = Path(args.output) if args.output else Path.cwd()
    out_dir.mkdir(parents=True, exist_ok=True)

    pdfs = list(pasta.glob('*.pdf'))
    if not pdfs:
        print(f"❌ Nenhum PDF encontrado em: {pasta}")
        sys.exit(1)

    print("=" * 60)
    print(f"📁 MODO BATCH: {len(pdfs)} PDF(s) encontrado(s)")
    print("=" * 60)

    resultados = []
    for idx, pdf in enumerate(pdfs, 1):
        print(f"\n[{idx}/{len(pdfs)}] Processando: {pdf.name}")
        sub_out = out_dir / pdf.stem
        sub_out.mkdir(exist_ok=True)
        rc = cmd_analisar(type('Args', (), {'pdf': str(pdf), 'output': str(sub_out)})())
        resultados.append((pdf.name, rc))

    print("\n" + "=" * 60)
    print("✅ BATCH CONCLUÍDO")
    print("=" * 60)
    for nome, rc in resultados:
        status = "✅ OK" if rc == 0 else "❌ Falha"
        print(f"   {status} — {nome}")
    print("=" * 60)
    return 0


if __name__ == '__main__':
    main()

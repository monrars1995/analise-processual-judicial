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
    if len(args) < 1:
        print("Uso: processo.py analisar <arquivo.pdf> [pasta_saida]")
        sys.exit(1)
    pdf = Path(args[0])
    out_dir = Path(args[1]) if len(args) > 1 else Path.cwd()
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
    # Merge irregularidades into dados for estatisticas
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
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    comando = sys.argv[1].lower()
    resto = sys.argv[2:]

    comandos = {
        'analisar': cmd_analisar,
        'extrair': lambda a: run_script('extrair_dados', *a),
        'irregularidades': lambda a: run_script('identificar_irregularidades', *a),
        'estatisticas': lambda a: run_script('estatisticas', *a),
        'relatorio': lambda a: run_script('gerar_relatorio', *a),
    }

    if comando not in comandos:
        print(f"Comando desconhecido: {comando}")
        print(f"Comandos disponíveis: {', '.join(comandos.keys())}")
        sys.exit(1)

    sys.exit(comandos[comando](resto))


if __name__ == '__main__':
    main()

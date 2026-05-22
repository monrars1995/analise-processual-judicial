#!/usr/bin/env python3
"""
Interface web Streamlit para Análise Processual Judicial.
Permite upload de PDF, visualização dos resultados e download dos arquivos gerados.

Uso:
    streamlit run app.py
"""
import sys
from pathlib import Path

# Add package to path
sys.path.insert(0, str(Path(__file__).parent))

import json
import tempfile
import subprocess
from datetime import datetime

try:
    import streamlit as st
except ImportError:
    print("Erro: streamlit não instalado. Execute: pip install streamlit")
    sys.exit(1)

st.set_page_config(
    page_title="Análise Processual Judicial",
    page_icon="⚖️",
    layout="wide"
)

st.title("⚖️ Análise Processual Judicial")
st.markdown("Analise processos judiciais digitais (PROJUDI, PJe) de forma automatizada.")

uploaded_file = st.file_uploader("📄 Faça upload do PDF do processo", type=["pdf"])

if uploaded_file:
    with tempfile.TemporaryDirectory() as tmpdir:
        pdf_path = Path(tmpdir) / uploaded_file.name
        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.getvalue())

        base = Path(tmpdir) / pdf_path.stem
        dados_json = base.with_suffix('.json')
        irregs_json = base.with_name(base.stem + '_irregularidades.json')
        stats_json = base.with_name(base.stem + '_estatisticas.json')
        relatorio_pdf = base.with_suffix('.pdf')

        progress = st.progress(0, text="Iniciando análise...")

        # Extrair
        progress.progress(10, text="Extraindo dados do PDF...")
        subprocess.run([sys.executable, "-m", "analise_processual_judicial.extrair_dados", str(pdf_path), str(dados_json)], check=True)

        with open(dados_json, 'r', encoding='utf-8') as f:
            dados = json.load(f)

        meta = dados.get('metadados', {})

        # Info cards
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Número", meta.get('numero_processo', 'N/A'))
        col2.metric("Classe", meta.get('classe', 'N/A'))
        col3.metric("Valor", meta.get('valor_causa', 'N/A'))
        col4.metric("Andamentos", len(dados.get('linha_do_tempo', [])))

        # Irregularidades
        progress.progress(40, text="Identificando irregularidades...")
        subprocess.run([sys.executable, "-m", "analise_processual_judicial.identificar_irregularidades", str(dados_json), str(irregs_json)], check=True)

        with open(irregs_json, 'r', encoding='utf-8') as f:
            irreg_data = json.load(f)

        irregs = irreg_data.get('irregularidades', [])

        st.subheader("🚨 Irregularidades Identificadas")
        if irregs:
            for ir in irregs:
                cor = "🔴" if ir['gravidade'] == 'ALTA' else ("🟠" if ir['gravidade'] == 'MEDIA' else "🟡")
                with st.expander(f"{cor} {ir['categoria']} — Gravidade: {ir['gravidade']}"):
                    st.write(f"**Descrição:** {ir['descricao']}")
                    st.write(f"**Fundamento:** {ir['fundamento']}")
                    st.write(f"**Recomendação:** {ir['recomendacao']}")
        else:
            st.success("✅ Nenhuma irregularidade detectada automaticamente.")

        # Estatísticas
        progress.progress(60, text="Calculando estatísticas...")
        dados['irregularidades'] = irregs
        merged = base.with_name(base.stem + '_merged.json')
        with open(merged, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        subprocess.run([sys.executable, "-m", "analise_processual_judicial.estatisticas", str(merged), str(stats_json)], check=True)

        with open(stats_json, 'r', encoding='utf-8') as f:
            stats = json.load(f)

        st.subheader("📊 Estatísticas")
        c1, c2, c3 = st.columns(3)
        c1.metric("Duração (dias)", stats['periodo_analisado']['duracao_dias'])
        c2.metric("Média dias entre andamentos", stats['intervalos_entre_andamentos']['media_dias'])
        c3.metric("Meses sem movimentação", len(stats.get('meses_sem_movimentacao', [])))

        # PDF
        progress.progress(80, text="Gerando relatório PDF...")
        subprocess.run([sys.executable, "-m", "analise_processual_judicial.gerar_relatorio", str(dados_json), str(irregs_json), str(relatorio_pdf)], check=True)

        # Downloads
        st.subheader("📥 Downloads")
        dcol1, dcol2, dcol3 = st.columns(3)
        with dcol1:
            with open(dados_json, 'rb') as f:
                st.download_button("📄 Dados JSON", f, file_name=dados_json.name, mime="application/json")
        with dcol2:
            with open(irregs_json, 'rb') as f:
                st.download_button("🚨 Irregularidades JSON", f, file_name=irregs_json.name, mime="application/json")
        with dcol3:
            with open(relatorio_pdf, 'rb') as f:
                st.download_button("📊 Relatório PDF", f, file_name=relatorio_pdf.name, mime="application/pdf")

        progress.progress(100, text="Análise concluída!")
        st.success("✅ Análise concluída com sucesso!")

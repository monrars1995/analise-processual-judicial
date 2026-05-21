#!/usr/bin/env python3
"""
Gera relatório PDF estruturado e bem diagramado com linha do tempo
e irregularidades processuais identificadas.
"""
import json
import sys
from pathlib import Path
from datetime import datetime

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        PageBreak, ListFlowable, ListItem, KeepTogether
    )
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
except ImportError:
    print("Erro: reportlab não instalado. Execute: pip install reportlab")
    sys.exit(1)


def criar_estilos():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='TituloPrincipal',
        fontName='Helvetica-Bold',
        fontSize=22,
        textColor=colors.HexColor('#1a237e'),
        alignment=TA_CENTER,
        spaceAfter=20,
        leading=26
    ))
    styles.add(ParagraphStyle(
        name='Subtitulo',
        fontName='Helvetica-Bold',
        fontSize=14,
        textColor=colors.HexColor('#283593'),
        alignment=TA_CENTER,
        spaceAfter=30,
        leading=18
    ))
    styles.add(ParagraphStyle(
        name='Secao',
        fontName='Helvetica-Bold',
        fontSize=16,
        textColor=colors.HexColor('#1a237e'),
        spaceBefore=20,
        spaceAfter=12,
        leading=20,
        borderWidth=0,
        borderColor=colors.HexColor('#1a237e'),
        borderPadding=5,
        leftIndent=0
    ))
    styles.add(ParagraphStyle(
        name='SecaoSub',
        fontName='Helvetica-Bold',
        fontSize=13,
        textColor=colors.HexColor('#3949ab'),
        spaceBefore=14,
        spaceAfter=8,
        leading=16
    ))
    styles.add(ParagraphStyle(
        name='Corpo',
        fontName='Helvetica',
        fontSize=10,
        alignment=TA_JUSTIFY,
        leading=14,
        spaceAfter=8
    ))
    styles.add(ParagraphStyle(
        name='CorpoNegrito',
        fontName='Helvetica-Bold',
        fontSize=10,
        alignment=TA_LEFT,
        leading=14,
        spaceAfter=4
    ))
    styles.add(ParagraphStyle(
        name='CaixaAlerta',
        fontName='Helvetica',
        fontSize=10,
        alignment=TA_JUSTIFY,
        leading=14,
        spaceAfter=10,
        backColor=colors.HexColor('#fff3e0'),
        borderColor=colors.HexColor('#ef6c00'),
        borderWidth=1,
        borderPadding=8,
        leftIndent=5,
        rightIndent=5
    ))
    styles.add(ParagraphStyle(
        name='CaixaGrave',
        fontName='Helvetica-Bold',
        fontSize=10,
        alignment=TA_JUSTIFY,
        leading=14,
        spaceAfter=10,
        backColor=colors.HexColor('#ffebee'),
        borderColor=colors.HexColor('#c62828'),
        borderWidth=1,
        borderPadding=8,
        leftIndent=5,
        rightIndent=5
    ))
    styles.add(ParagraphStyle(
        name='Rodape',
        fontName='Helvetica-Oblique',
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER,
        spaceBefore=10
    ))
    styles.add(ParagraphStyle(
        name='InfoBox',
        fontName='Helvetica',
        fontSize=9,
        alignment=TA_LEFT,
        leading=12,
        backColor=colors.HexColor('#e8eaf6'),
        borderColor=colors.HexColor('#1a237e'),
        borderWidth=1,
        borderPadding=6,
        leftIndent=5,
        rightIndent=5,
        spaceAfter=8
    ))
    return styles


def cor_gravidade(grav):
    return {
        'ALTA': colors.HexColor('#c62828'),
        'MEDIA': colors.HexColor('#ef6c00'),
        'BAIXA': colors.HexColor('#f9a825')
    }.get(grav, colors.grey)


def cor_gravidade_bg(grav):
    return {
        'ALTA': colors.HexColor('#ffebee'),
        'MEDIA': colors.HexColor('#fff3e0'),
        'BAIXA': colors.HexColor('#fffde7')
    }.get(grav, colors.HexColor('#f5f5f5'))


def build_capa(meta, styles):
    elements = []
    elements.append(Spacer(1, 3*cm))
    elements.append(Paragraph("RELATÓRIO DE ANÁLISE PROCESSUAL", styles['TituloPrincipal']))
    elements.append(Paragraph("Linha do Tempo e Identificação de Irregularidades", styles['Subtitulo']))
    elements.append(Spacer(1, 1.5*cm))

    # Caixa de informações do processo
    info_data = []
    campos = [
        ("Número do Processo", meta.get('numero_processo', 'N/A')),
        ("Classe", meta.get('classe', 'N/A')),
        ("Assunto", meta.get('assunto', 'N/A')),
        ("Prioridade", meta.get('prioridade', 'N/A')),
        ("Data de Distribuição", meta.get('data_distribuicao', 'N/A')),
        ("Valor da Causa", meta.get('valor_causa', 'N/A')),
        ("Segredo de Justiça", meta.get('segredo_justica', 'N/A')),
    ]
    for rotulo, valor in campos:
        info_data.append([Paragraph(f"<b>{rotulo}:</b>", styles['CorpoNegrito']), Paragraph(valor, styles['Corpo'])])

    info_table = Table(info_data, colWidths=[5.5*cm, 10*cm])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#e8eaf6')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#1a237e')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#c5cae9')),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.8*cm))

    # Partes
    elements.append(Paragraph("PARTES", styles['SecaoSub']))
    partes = meta.get('partes', [])
    if partes:
        partes_data = []
        for p in partes:
            polo = "Autor(a)" if p.get('polo') == 'ativo' else "Réu/Ré"
            partes_data.append([Paragraph(f"<b>{polo}:</b>", styles['CorpoNegrito']), Paragraph(p.get('nome', ''), styles['Corpo'])])
        partes_table = Table(partes_data, colWidths=[3*cm, 12.5*cm])
        partes_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(partes_table)
    else:
        elements.append(Paragraph("Partes não identificadas.", styles['Corpo']))

    elements.append(PageBreak())
    return elements


def build_resumo(irregs, styles):
    elements = []
    elements.append(Paragraph("RESUMO EXECUTIVO", styles['Secao']))
    total = len(irregs)
    altas = sum(1 for i in irregs if i['gravidade'] == 'ALTA')
    medias = sum(1 for i in irregs if i['gravidade'] == 'MEDIA')
    baixas = sum(1 for i in irregs if i['gravidade'] == 'BAIXA')

    if total == 0:
        elements.append(Paragraph(
            "Não foram identificadas irregularidades processuais evidentes com base nos dados extraídos. "
            "Recomenda-se revisão manual para conferência de aspectos subtis.",
            styles['Corpo']
        ))
    else:
        texto = (
            f"Foram identificadas <b>{total}</b> irregularidade(s) processual(is): "
            f"<font color='#c62828'><b>{altas}</b> de gravidade ALTA</font>, "
            f"<font color='#ef6c00'><b>{medias}</b> de gravidade MÉDIA</font> e "
            f"<font color='#f9a825'><b>{baixas}</b> de gravidade BAIXA</font>."
        )
        elements.append(Paragraph(texto, styles['Corpo']))
        elements.append(Spacer(1, 0.3*cm))

        # Tabela resumo
        resumo_data = [['Gravidade', 'Qtd', 'Categorias']]
        for g, label in [('ALTA', 'Alta'), ('MEDIA', 'Média'), ('BAIXA', 'Baixa')]:
            cats = [i['categoria'] for i in irregs if i['gravidade'] == g]
            resumo_data.append([
                Paragraph(f'<b>{label}</b>', styles['CorpoNegrito']),
                Paragraph(str(len(cats)), styles['Corpo']),
                Paragraph(', '.join(set(cats)), styles['Corpo'])
            ])
        resumo_table = Table(resumo_data, colWidths=[3*cm, 2*cm, 10.5*cm])
        resumo_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f5f5f5')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fafafa')])
        ]))
        elements.append(resumo_table)
    elements.append(PageBreak())
    return elements


def build_linha_tempo(linha, styles):
    elements = []
    elements.append(Paragraph("LINHA DO TEMPO PROCESSUAL", styles['Secao']))
    elements.append(Paragraph(
        "Cronologia completa dos andamentos e documentos juntados aos autos, em ordem cronológica.",
        styles['Corpo']
    ))
    elements.append(Spacer(1, 0.3*cm))

    # Tabela timeline
    timeline_data = [['Data', 'Hora', 'Tipo', 'Documento / Resumo']]
    for item in linha:
        timeline_data.append([
            Paragraph(item.get('data', ''), styles['Corpo']),
            Paragraph(item.get('hora', ''), styles['Corpo']),
            Paragraph(item.get('tipo', ''), styles['CorpoNegrito']),
            Paragraph(item.get('documento', '')[:200], styles['Corpo'])
        ])

    timeline_table = Table(timeline_data, colWidths=[2.2*cm, 1.8*cm, 3.5*cm, 8*cm], repeatRows=1)
    timeline_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
        ('TOPPADDING', (0, 1), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
        ('WORDWRAP', (0, 0), (-1, -1), True),
    ]))
    elements.append(timeline_table)
    elements.append(PageBreak())
    return elements


def build_irregularidades(irregs, styles):
    elements = []
    elements.append(Paragraph("IRREGULARIDADES PROCESSUAIS IDENTIFICADAS", styles['Secao']))
    if not irregs:
        elements.append(Paragraph(
            "Nenhuma irregularidade processual foi detectada automaticamente com base nos parâmetros analisados.",
            styles['Corpo']
        ))
        elements.append(PageBreak())
        return elements

    elements.append(Paragraph(
        "Detalhamento de cada irregularidade identificada, com fundamento legal e recomendação.",
        styles['Corpo']
    ))
    elements.append(Spacer(1, 0.3*cm))

    for idx, ir in enumerate(irregs, 1):
        grav = ir['gravidade']
        cor = cor_gravidade(grav)
        cor_bg = cor_gravidade_bg(grav)
        caixa_style = 'CaixaGrave' if grav == 'ALTA' else 'CaixaAlerta'

        header = Paragraph(
            f"<font color='{cor.hexval()}'><b>#{idx} — {ir['categoria']} [GRAVIDADE: {grav}]</b></font>",
            styles['SecaoSub']
        )
        elements.append(header)

        detalhes = [
            Paragraph(f"<b>Descrição:</b> {ir['descricao']}", styles[caixa_style]),
            Paragraph(f"<b>Fundamento Legal:</b> {ir['fundamento']}", styles['InfoBox']),
            Paragraph(f"<b>Data da Ocorrência:</b> {ir.get('data_ocorrencia') or 'Não identificada'}", styles['Corpo']),
            Paragraph(f"<b>Recomendação:</b> {ir['recomendacao']}", styles['Corpo']),
        ]
        for p in detalhes:
            elements.append(p)
        elements.append(Spacer(1, 0.2*cm))

    elements.append(PageBreak())
    return elements


def build_recomendacoes_finais(irregs, styles):
    elements = []
    elements.append(Paragraph("RECOMENDAÇÕES FINAIS", styles['Secao']))
    if not irregs:
        elements.append(Paragraph(
            "Com base na análise automatizada, não há recomendações específicas de correção processual. "
            "Mantenha acompanhamento regular do feito.",
            styles['Corpo']
        ))
    else:
        recs = [f"{i+1}. {ir['recomendacao']}" for i, ir in enumerate(irregs)]
        for r in recs:
            elements.append(Paragraph(r, styles['Corpo']))
        elements.append(Spacer(1, 0.3*cm))
        elements.append(Paragraph(
            "<b>Nota:</b> Esta análise é automatizada e tem caráter auxiliar. Recomenda-se conferência manual "
            "por profissional habilitado para decisões estratégicas processuais.",
            styles['CaixaAlerta']
        ))
    return elements


def gerar_pdf(dados, irregularidades, saida_pdf):
    doc = SimpleDocTemplate(
        str(saida_pdf),
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    styles = criar_estilos()
    story = []

    meta = dados.get('metadados', {})
    linha = dados.get('linha_do_tempo', [])
    irregs = irregularidades.get('irregularidades', [])

    # Capa
    story.extend(build_capa(meta, styles))
    # Resumo
    story.extend(build_resumo(irregs, styles))
    # Linha do tempo
    story.extend(build_linha_tempo(linha, styles))
    # Irregularidades
    story.extend(build_irregularidades(irregs, styles))
    # Recomendações
    story.extend(build_recomendacoes_finais(irregs, styles))

    # Rodapé em todas as páginas via onPage
    def add_page_num(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica-Oblique', 8)
        canvas.setFillColor(colors.grey)
        canvas.drawCentredString(A4[0]/2, 1*cm, f"Relatório de Análise Processual — Página {doc.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=add_page_num, onLaterPages=add_page_num)
    print(f"PDF gerado com sucesso: {saida_pdf}")


def main():
    if len(sys.argv) < 3:
        print("Uso: python gerar_relatorio.py <dados.json> <irregularidades.json> [saida.pdf]")
        sys.exit(1)
    dados_path = Path(sys.argv[1])
    irreg_path = Path(sys.argv[2])
    saida = Path(sys.argv[3]) if len(sys.argv) > 3 else dados_path.with_suffix('.pdf')

    with open(dados_path, 'r', encoding='utf-8') as f:
        dados = json.load(f)
    with open(irreg_path, 'r', encoding='utf-8') as f:
        irregularidades = json.load(f)

    gerar_pdf(dados, irregularidades, saida)


if __name__ == '__main__':
    main()

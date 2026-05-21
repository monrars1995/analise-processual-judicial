---
name: analise-processual-judicial
description: Analisa processos judiciais digitais (PROJUDI, PJe, e-TJ, etc.) baixados em PDF. Extrai linha do tempo dos andamentos, identifica irregularidades processuais baseadas no CPC/CDC/Lei 9.099/95 (prazos, prioridade, tutela, intimação, citação, audiência, sentença, recurso) e gera relatório PDF estruturado e bem diagramado com a análise completa. Use quando o usuário precisar analisar um PDF de processo judicial, gerar cronologia de andamentos, identificar nulidades, prazos vencidos, violação de prioridade de tramitação, ausência de intimação, ou criar relatório forense em PDF.
---

# Análise Processual Judicial

Skill para análise automatizada de processos judiciais digitais em PDF, com extração de linha do tempo, identificação de irregularidades processuais e geração de relatório PDF profissional.

## Workflow

Sempre siga esta sequência:

1. **Extrair dados** do PDF do processo
2. **Identificar irregularidades** na linha do tempo
3. **Gerar relatório PDF** estruturado e bem diagramado

### 1. Extração de Dados

Use o script `scripts/extrair_dados.py`:

```bash
python scripts/extrair_dados.py <processo.pdf> [saida.json]
```

O script extrai:
- Metadados do processo (número, classe, assunto, prioridade, valor, partes)
- Índice de documentos do PROJUDI/PJe (datas, tipos, nomes)
- Andamentos adicionais detectados em páginas de despacho/decisão/certidão
- Linha do tempo unificada e ordenada cronologicamente

**Dependência**: `pdfplumber`. Instalar com `pip install pdfplumber` se necessário.

### 2. Identificação de Irregularidades

Use o script `scripts/identificar_irregularidades.py`:

```bash
python scripts/identificar_irregularidades.py <dados.json> [saida_irregularidades.json]
```

O script analisa a linha do tempo e detecta:
- **Citação**: atraso acima de 30 dias (JEC) ou 15 dias (comum)
- **Contestação**: intempestividade (prazo 15 dias úteis)
- **Tutela antecipada/liminar**: ausência de decisão por mais de 21 dias
- **Audiência (JEC)**: não designada em até 60 dias da citação
- **Sentença (JEC)**: proferida com mais de 15 dias corridos da audiência
- **Prioridade idoso**: intervalos superiores a 60 dias sem andamentos
- **Recurso**: intempestividade (15 dias úteis)
- **Conclusão**: autos conclusos há mais de 30 dias sem decisão
- **Intimação**: ausência de intimação sobre contestação
- **Gratuidade de justiça**: pedido sem decisão expressa

Cada irregularidade inclui: gravidade (ALTA/MÉDIA/BAIXA), categoria, descrição, fundamento legal, data e recomendação.

**Para ajustar regras ou adicionar novas**: consulte `references/regras_processuais.md`.

### 3. Geração do Relatório PDF

Use o script `scripts/gerar_relatorio.py`:

```bash
python scripts/gerar_relatorio.py <dados.json> <irregularidades.json> [saida.pdf]
```

O relatório PDF contém:
- **Capa**: dados do processo, partes, valor
- **Resumo Executivo**: quantitativo de irregularidades por gravidade
- **Linha do Tempo**: tabela cronológica completa (data, hora, tipo, documento)
- **Irregularidades**: detalhamento por item com fundamento e recomendação
- **Recomendações Finais**: síntese das ações sugeridas

**Dependência**: `reportlab`. Instalar com `pip install reportlab` se necessário.

### Uso Direto (Pipeline Completo)

Para executar os 3 passos de uma vez:

```bash
python scripts/extrair_dados.py processo.pdf processo.json && \
python scripts/identificar_irregularidades.py processo.json irregularidades.json && \
python scripts/gerar_relatorio.py processo.json irregularidades.json relatorio.pdf
```

## Quando Não Usar os Scripts

Se o PDF não for de sistema judicial digital (ex: simples petição avulsa, texto de doutrina), os scripts podem não extrair dados corretamente. Neste caso, leia o PDF manualmente e elabore a análise com base no conteúdo.

## Estrutura do PDF de Processo Digital

Os sistemas PROJUDI, PJe e similares geram PDFs com padrões previsíveis:
- **Página 1**: capa com metadados, partes, índice de documentos
- **Páginas seguintes**: documentos juntados na ordem do índice
- **Páginas de atos**: despachos, decisões e certidões costumam ser páginas curtas com data de assinatura no formato "Salvador, 17 de Novembro de 2025"

O script de extração usa regex para capturar esses padrões. Se o formato do tribunal for diferente, ajuste as expressões regulares em `extrair_dados.py`.

## Extensão e Personalização

Para adicionar novas regras de irregularidade:
1. Edite `scripts/identificar_irregularidades.py`
2. Adicione bloco de lógica no método `identificar_irregularidades`
3. Atualize `references/regras_processuais.md` com o fundamento legal
4. Teste com um processo real antes de usar em produção

Para alterar o layout do PDF:
1. Edite `scripts/gerar_relatorio.py`
2. Os estilos e cores estão centralizados em `criar_estilos()`
3. Seções individuais são construídas por funções separadas (`build_capa`, `build_linha_tempo`, etc.)

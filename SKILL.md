---
name: analise-processual-judicial
description: Analisa processos judiciais digitais (PROJUDI, PJe, e-TJ, etc.) baixados em PDF. Extrai linha do tempo dos andamentos, identifica irregularidades processuais baseadas no CPC/CDC/Lei 9.099/95 (prazos, prioridade, tutela, intimação, citação, audiência, sentença, recurso) e gera relatório PDF estruturado e bem diagramado com a análise completa. Use quando o usuário precisar analisar um PDF de processo judicial, gerar cronologia de andamentos, identificar nulidades, prazos vencidos, violação de prioridade de tramitação, ausência de intimação, ou criar relatório forense em PDF. Comandos disponíveis: /processo analisar, /processo extrair, /processo irregularidades, /processo relatorio.
risk: unknown
source: community
---

# Análise Processual Judicial

Skill para análise automatizada de processos judiciais digitais em PDF, com extração de linha do tempo, identificação de irregularidades processuais e geração de relatório PDF profissional.

## Comandos Interativos

Esta skill responde aos seguintes comandos `/`:

### `/processo analisar <caminho-do-pdf>`

Executa o pipeline completo: extrai dados, identifica irregularidades, calcula estatísticas e gera o relatório PDF em um único comando.

```
Run command: /processo analisar processo.pdf
```

**Saída:**
- `{nome}.json` — dados extraídos
- `{nome}_irregularidades.json` — irregularidades identificadas
- `{nome}_estatisticas.json` — estatísticas quantitativas
- `{nome}.pdf` — relatório final

### `/processo extrair <caminho-do-pdf> [saida.json]`

Extrai apenas os dados estruturados do PDF do processo.

```
Run command: /processo extrair processo.pdf
```

**Saída:** JSON com metadados, partes, índice de documentos e linha do tempo.

### `/processo irregularidades <dados.json> [saida.json]`

Analisa um JSON previamente extraído e identifica irregularidades processuais.

```
Run command: /processo irregularidades processo.json
```

**Saída:** JSON com lista de irregularidades classificadas por gravidade.

### `/processo relatorio <dados.json> <irregularidades.json> [saida.pdf]`

Gera o relatório PDF a partir dos dados e irregularidades já extraídos.

```
Run command: /processo relatorio processo.json irregularidades.json
```

**Saída:** PDF estruturado e bem diagramado.

### `/processo estatisticas <dados.json> [saida.json]`

Gera estatísticas quantitativas do processo: duração, andamentos por mês, intervalos médios, tipos de documento, meses sem movimentação e indicadores de produtividade.

```
Run command: /processo estatisticas processo.json
```

**Saída:** JSON com métricas e indicadores do processo.

### `/processo batch <pasta> [pasta_saida]`

Processa todos os PDFs de uma pasta em modo batch, executando o pipeline completo em cada um.

```
Run command: /processo batch /caminho/dos/processos /caminho/saida
```

**Saída:** Para cada PDF, gera subpasta com JSON, irregularidades, estatísticas e PDF.

### `/processo exportar <dados.json> <irregularidades.json> [saida.xlsx] [saida.csv]`

Exporta os dados do processo para planilha Excel (XLSX) e CSV, com abas separadas para metadados, linha do tempo e irregularidades.

```
Run command: /processo exportar processo.json irregularidades.json
```

**Saída:** Arquivo XLSX com formatação profissional e CSV da linha do tempo.

**Dependência:** `openpyxl`. Instalar com `pip install openpyxl` se necessário.

### `/processo comparar <processo1.json> <processo2.json> [...]`

Compara dois ou mais processos judiciais extraídos, mostrando diferenças de ritmo, quantidade de andamentos, irregularidades e tipos de documento.

```
Run command: /processo comparar processo_a.json processo_b.json
```

**Saída:** Tabela comparativa no terminal com destaques e ranking.

### CLI Unificada

Para uso direto no terminal sem comandos `/`, use o script `processo.py`:

```bash
python scripts/processo.py analisar processo.pdf [pasta_saida]
python scripts/processo.py extrair processo.pdf [saida.json]
python scripts/processo.py irregularidades dados.json [saida.json]
python scripts/processo.py estatisticas dados.json [saida.json]
python scripts/processo.py relatorio dados.json irregularidades.json [saida.pdf]
```

---

## Workflow

Sempre siga esta sequência quando o usuário não usar um comando `/` específico:

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

### 4. Estatísticas do Processo (opcional)

Use o script `scripts/estatisticas.py`:

```bash
python scripts/estatisticas.py <dados.json> [saida_estatisticas.json]
```

O script calcula:
- Período analisado (início, fim, duração em dias)
- Total de andamentos e média por mês
- Tipos de documento mais frequentes
- Intervalos entre andamentos (média, máximo, mínimo)
- Meses sem movimentação
- Indicadores de produtividade processual

Requer que o JSON de entrada contenha a chave `irregularidades` (mesclar com o resultado de `identificar_irregularidades.py` se necessário).

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

### Pipeline Completo

Para executar os 3 passos de uma vez:

```bash
python scripts/extrair_dados.py processo.pdf processo.json && \
python scripts/identificar_irregularidades.py processo.json irregularidades.json && \
python scripts/gerar_relatorio.py processo.json irregularidades.json relatorio.pdf
```

---

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

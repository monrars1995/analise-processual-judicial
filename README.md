# Análise Processual Judicial

[![Tests](https://github.com/monrars1995/analise-processual-judicial/actions/workflows/tests.yml/badge.svg)](https://github.com/monrars1995/analise-processual-judicial/actions/workflows/tests.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Skill para análise automatizada de **processos judiciais digitais** baixados em PDF (PROJUDI, PJe, e-TJ, etc.). Extrai a **linha do tempo** dos andamentos, **identifica irregularidades processuais** e gera um **relatório PDF estruturado e bem diagramado**.

> ⚖️ Transforme PDFs de processos em análises forenses estruturadas em segundos.

---

## Funcionalidades

| Funcionalidade | Descrição |
|---------------|-----------|
| 📄 **Extração de Dados** | Lê PDFs do PROJUDI/PJe e extrai metadados, partes, índice de documentos e andamentos |
| ⏱️ **Linha do Tempo** | Gera cronologia completa dos andamentos em ordem cronológica |
| 🚨 **Identificação de Irregularidades** | Detecta automaticamente prazos vencidos, nulidades e descumprimento de regras processuais |
| 📊 **Relatório PDF Profissional** | Gera documento bem diagramado com capa, resumo, timeline, irregularidades e recomendações |
| ⚖️ **Base Legal** | Fundamentação em CPC/2015, CDC, Lei 9.099/95, Estatuto do Idoso e Resoluções CNJ |

---

## Irregularidades Detectadas

A skill verifica automaticamente:

- **Citação** — atraso acima de 30 dias (JEC) ou 15 dias (comum)
- **Contestação** — intempestividade (prazo de 15 dias úteis)
- **Tutela Antecipada/Liminar** — ausência de decisão por mais de 21 dias
- **Audiência (JEC)** — não designada em até 60 dias da citação
- **Sentença (JEC)** — proferida com mais de 15 dias corridos da audiência
- **Prioridade de Tramitação (Idoso)** — intervalos superiores a 60 dias sem andamentos
- **Recurso** — intempestividade (15 dias úteis)
- **Conclusão para Decisão** — autos conclusos há mais de 30 dias sem decisão
- **Intimação** — ausência de intimação da autora sobre contestação
- **Gratuidade de Justiça** — pedido sem decisão expressa detectada

Cada irregularidade inclui: **gravidade** (Alta/Média/Baixa), **descrição**, **fundamento legal** e **recomendação**.

---

## Instalação

### Opção 1: Instalação via pip (recomendado)

```bash
pip install git+https://github.com/monrars1995/analise-processual-judicial.git
```

Após instalar, o comando `analise-processual` estará disponível globalmente:

```bash
analise-processual analisar processo.pdf
```

### Opção 2: Clone e instalação local

```bash
git clone https://github.com/monrars1995/analise-processual-judicial.git
cd analise-processual-judicial
pip install -e .
```

### Opção 3: Apenas dependências (uso direto dos scripts)

```bash
pip install pdfplumber reportlab
```

### Docker (opcional)

```bash
docker build -t analise-processual-judicial .
docker run -v $(pwd):/data analise-processual-judicial python /app/scripts/extrair_dados.py /data/processo.pdf /data/processo.json
```

Ou use um ambiente virtual:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
pip install pdfplumber reportlab
```

---

## Como Usar

### Pipeline Completo (3 passos)

```bash
# 1. Extrair dados do PDF do processo
python scripts/extrair_dados.py processo.pdf processo.json

# 2. Identificar irregularidades na linha do tempo
python scripts/identificar_irregularidades.py processo.json irregularidades.json

# 3. Gerar relatório PDF estruturado
python scripts/gerar_relatorio.py processo.json irregularidades.json relatorio.pdf
```

### Execução em uma linha

```bash
# Via pip install
analise-processual analisar processo.pdf [pasta_saida]

# Ou diretamente
python scripts/processo.py analisar processo.pdf [pasta_saida]
```

Ou passo a passo:

```bash
python scripts/extrair_dados.py processo.pdf processo.json && \
python scripts/identificar_irregularidades.py processo.json irregularidades.json && \
python scripts/gerar_relatorio.py processo.json irregularidades.json relatorio.pdf && \
python scripts/estatisticas.py processo.json estatisticas.json
```

---

## Exemplo Prático

Analisando um processo real do PROJUDI-TJBA:

```bash
# Baixe o PDF do processo no PROJUDI e salve como processo.pdf

# Extração
python scripts/extrair_dados.py processo.pdf processo.json
# → Dados extraídos para: processo.json
# → Total: 454 páginas, 58 andamentos/documentos

# Análise
python scripts/identificar_irregularidades.py processo.json irregularidades.json
# → Irregularidades identificadas: 1
# → Contestação apresentada em 27 dias (prazo: 15 dias úteis)

# Relatório
python scripts/gerar_relatorio.py processo.json irregularidades.json relatorio.pdf
# → PDF gerado com sucesso: relatorio.pdf (8 páginas)
```

---

## Estrutura do Relatório PDF

O relatório gerado contém:

1. **Capa** — número do processo, classe, assunto, prioridade, valor da causa e partes
2. **Resumo Executivo** — quantitativo de irregularidades por gravidade (tabela colorida)
3. **Gráficos e Visualizações** — representação visual dos dados:
   - Gráfico de barras: andamentos por mês
   - Gráfico de pizza: distribuição por tipo de documento (top 5)
4. **Linha do Tempo Processual** — tabela cronológica completa com data, hora, tipo e documento
5. **Irregularidades Identificadas** — detalhamento por item com:
   - Gravidade e categoria
   - Descrição da irregularidade
   - Fundamento legal
   - Data da ocorrência
   - Recomendação de ação
6. **Recomendações Finais** — síntese das ações sugeridas

> O PDF usa paleta de cores profissional (azul institucional, alertas em laranja/vermelho/amarelo) e numeração de páginas.

---

## Arquivos da Skill

```
analise-processual-judicial/
├── SKILL.md                              # Instruções para agentes IA
├── README.md                             # Esta documentação
├── scripts/
│   ├── extrair_dados.py                  # Extrai metadados, índice e timeline
│   ├── identificar_irregularidades.py    # Detecta nulidades e prazos
│   └── gerar_relatorio.py                # Gera PDF profissional
└── references/
    └── regras_processuais.md             # Fundamentos legais (CPC, CDC, Lei 9099/95)
```

### `scripts/extrair_dados.py`

**Entrada:** PDF do processo judicial digital
**Saída:** `JSON` com:
- `metadados` — número, classe, assunto, prioridade, valor, partes
- `indice_documentos` — lista de documentos juntados
- `andamentos_detectados` — despachos, decisões, certidões
- `linha_do_tempo` — cronologia unificada ordenada

**Uso:**
```bash
python scripts/extrair_dados.py <processo.pdf> [saida.json]
```

### `scripts/identificar_irregularidades.py`

**Entrada:** JSON gerado por `extrair_dados.py`
**Saída:** `JSON` com lista de irregularidades classificadas por gravidade

**Uso:**
```bash
python scripts/identificar_irregularidades.py <dados.json> [saida_irregularidades.json]
```

### `scripts/gerar_relatorio.py`

**Entrada:** JSON de dados + JSON de irregularidades
**Saída:** `PDF` estruturado e bem diagramado

**Uso:**
```bash
python scripts/gerar_relatorio.py <dados.json> <irregularidades.json> [saida.pdf]
```

### `scripts/estatisticas.py`

**Entrada:** JSON gerado por `extrair_dados.py` (com irregularidades mescladas)
**Saída:** `JSON` com estatísticas quantitativas do processo

**Uso:**
```bash
python scripts/estatisticas.py <dados.json> [saida_estatisticas.json]
```

**Métricas calculadas:**
- Período analisado (início, fim, duração)
- Total de andamentos e média por mês
- Tipos de documento mais frequentes
- Intervalos entre andamentos (média, máximo, mínimo)
- Meses sem movimentação
- Indicadores de produtividade processual

---

## Personalização

### Adicionar novas regras de irregularidade

1. Edite `scripts/identificar_irregularidades.py`
2. Adicione bloco de lógica no método `identificar_irregularidades`
3. Atualize `references/regras_processuais.md` com o fundamento legal
4. Teste com um processo real

### Alterar layout do PDF

1. Edite `scripts/gerar_relatorio.py`
2. Ajuste cores e fontes em `criar_estilos()`
3. Modifique seções em `build_capa`, `build_linha_tempo`, etc.

### Adaptar para outros sistemas judiciais

O script usa regex para padrões PROJUDI/PJe. Se o formato do tribunal for diferente:
1. Ajuste `extrair_metadados()` para capturar campos específicos
2. Ajuste `extrair_indice()` para o padrão de índice do sistema
3. Ajuste `extrair_andamentos_adicionais()` para datas e tipos de atos

---

## Requisitos

- Python 3.8+
- `pdfplumber` — extração de texto de PDFs
- `reportlab` — geração de PDFs

```bash
pip install pdfplumber reportlab
```

---

## Instalação Automática

Use o script `install.sh` para instalar a skill em todas as plataformas detectadas automaticamente:

```bash
chmod +x install.sh
./install.sh
```

O script detecta e instala em:
- **Claude Code** (`~/.claude/skills/`)
- **Codex** (`~/.codex/skills/`)
- **Antigravity (Gemini)** (`~/.gemini/config/skills/`)

## CI/CD

O repositório inclui GitHub Actions que testa os scripts em Python 3.10, 3.11, 3.12 e 3.13:
- Lint com flake8
- Teste de imports
- Teste end-to-end com dados simulados

## Licença

MIT — livre para uso, modificação e distribuição.

---

## Contato

Repositório: https://github.com/monrars1995/analise-processual-judicial

Para reportar bugs ou sugerir melhorias, abra uma **issue** no repositório.

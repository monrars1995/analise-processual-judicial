# Changelog

Todas as mudanças notáveis deste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [1.0.0] - 2024-05-21

### Adicionado
- Extração de dados de PDFs do PROJUDI/PJe (metadados, índice, timeline)
- Identificação automatizada de 10 tipos de irregularidades processuais
- Geração de relatório PDF estruturado com capa, resumo, timeline e recomendações
- Gráficos no PDF: barras (andamentos por mês) e pizza (tipos de documento)
- CLI unificada `processo.py` com argparse e subcomandos
- Comandos `/` interativos para Claude Code, Codex e Antigravity
- Script `estatisticas.py` com métricas quantitativas do processo
- Script `exportar.py` para XLSX e CSV
- Modo batch para processar múltiplos PDFs
- Pacote Python instalável via `pip install`
- GitHub Actions CI/CD com testes em Python 3.10-3.13
- Dockerfile para uso containerizado
- `install.sh` com auto-detecção de plataforma
- Testes unitários com pytest (4 testes)
- Logging estruturado nos scripts principais
- Referências de regras processuais (CPC, CDC, Lei 9.099/95)

### Suporte a Plataformas
- Claude Code (`.claude/skills/`)
- Codex (`.codex/skills/`)
- Antigravity/Gemini (`.gemini/config/skills/`)

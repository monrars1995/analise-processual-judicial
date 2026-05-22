#!/usr/bin/env bash
set -e

SKILL_NAME="analise-processual-judicial"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🔧 Instalando skill: $SKILL_NAME"
echo ""

# Detectar plataformas disponíveis
PLATFORMS=()

if [ -d "$HOME/.claude/skills" ]; then
    PLATFORMS+=("claude")
fi
if [ -d "$HOME/.codex/skills" ]; then
    PLATFORMS+=("codex")
fi
if [ -d "$HOME/.gemini/config/skills" ]; then
    PLATFORMS+=("antigravity")
fi

if [ ${#PLATFORMS[@]} -eq 0 ]; then
    echo "❌ Nenhuma plataforma suportada encontrada."
    echo "   Certifique-se de que Claude Code, Codex ou Antigravity (Gemini) estejam instalados."
    exit 1
fi

echo "📦 Plataformas detectadas: ${PLATFORMS[*]}"
echo ""

# Instalar em cada plataforma
for platform in "${PLATFORMS[@]}"; do
    case $platform in
        claude)
            DEST="$HOME/.claude/skills/$SKILL_NAME"
            ;;
        codex)
            DEST="$HOME/.codex/skills/$SKILL_NAME"
            ;;
        antigravity)
            DEST="$HOME/.gemini/config/skills/$SKILL_NAME"
            ;;
    esac

    echo "➡️  Instalando em: $DEST"
    mkdir -p "$DEST/scripts" "$DEST/references" "$DEST/assets"
    cp "$SCRIPT_DIR/SKILL.md" "$DEST/"
    cp "$SCRIPT_DIR/README.md" "$DEST/" 2>/dev/null || true
    cp "$SCRIPT_DIR/install.sh" "$DEST/" 2>/dev/null || true
    cp "$SCRIPT_DIR/scripts/"*.py "$DEST/scripts/"
    cp "$SCRIPT_DIR/references/"*.md "$DEST/references/"
    echo "   ✅ Instalado em $platform"
    echo ""
done

# Verificar dependências Python
echo "🐍 Verificando dependências Python..."
MISSING=()

if ! python3 -c "import pdfplumber" 2>/dev/null; then
    MISSING+=("pdfplumber")
fi
if ! python3 -c "import reportlab" 2>/dev/null; then
    MISSING+=("reportlab")
fi

if [ ${#MISSING[@]} -gt 0 ]; then
    echo "   ⚠️  Dependências faltando: ${MISSING[*]}"
    echo "   Execute: pip install ${MISSING[*]}"
else
    echo "   ✅ Todas as dependências estão instaladas"
fi

echo ""
echo "🎉 Instalação concluída!"
echo ""
echo "Comandos disponíveis:"
echo "   /processo analisar <pdf>           → Pipeline completo"
echo "   /processo extrair <pdf>            → Extrair dados"
echo "   /processo irregularidades <json>   → Identificar irregularidades"
echo "   /processo estatisticas <json>      → Gerar estatísticas"
echo "   /processo relatorio <dados> <irrs> → Gerar PDF"

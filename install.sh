#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/seu-usuario/term-dash-invest.git"
DESTINO="${HOME}/term-dash-invest"

echo "Instalando dashboard de investimentos..."

if ! command -v git >/dev/null 2>&1; then
  echo "Erro: git não encontrado. Instale o git e tente novamente."
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "Erro: python3 não encontrado. Instale o Python 3 e tente novamente."
  exit 1
fi

if [ -d "${DESTINO}/.git" ]; then
  echo "Repositório já existe em ${DESTINO}, atualizando..."
  git -C "${DESTINO}" pull --ff-only
else
  echo "Clonando repositório em ${DESTINO}..."
  git clone "${REPO_URL}" "${DESTINO}"
fi

CSV_PADRAO="${HOME}/investimentos.csv"
CSV_OCULTO="${HOME}/.investimentos.csv"

if [ -f "${CSV_PADRAO}" ] || [ -f "${CSV_OCULTO}" ]; then
  echo "CSV encontrado na pasta base do usuário."
else
  echo "Nenhum CSV encontrado em ${HOME}. Copiando exemplo para ${CSV_PADRAO}."
  cp "${DESTINO}/data/investimentos.csv" "${CSV_PADRAO}"
fi

echo "Concluído! Execute:"
echo "  python3 ${DESTINO}/main.py"

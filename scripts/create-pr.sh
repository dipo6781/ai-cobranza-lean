#!/bin/bash
if [ -z "$1" ]; then
  echo "❌ Uso: ./scripts/create-pr.sh \"Título\""
  exit 1
fi
BRANCH=$(git branch --show-current)
git push origin $BRANCH
gh pr create --title "$1" --base develop
echo "✅ PR creado"

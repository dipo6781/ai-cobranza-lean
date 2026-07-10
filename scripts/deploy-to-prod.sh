#!/bin/bash
echo "⚠️  Desplegando a producción"
read -p "¿Estás seguro? (s/n): " confirm
if [ "$confirm" != "s" ]; then
  echo "❌ Cancelado"
  exit 1
fi
git checkout main
git pull origin main
git merge develop
git push origin main
echo "✅ Deploy iniciado"

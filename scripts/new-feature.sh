#!/bin/bash
if [ -z "$1" ]; then
  echo "❌ Uso: ./scripts/new-feature.sh nombre-feature"
  exit 1
fi
git checkout develop
git pull origin develop
git checkout -b feature/$1
echo "✅ Rama feature/$1 creada"

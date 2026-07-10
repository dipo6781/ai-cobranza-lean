#!/bin/bash
echo "🔍 Verificando código..."
if grep -r "eyJhbG" app/ 2>/dev/null; then
  echo "❌ Tokens JWT hardcodeados"
  exit 1
fi
if grep -r "gsk_" app/ 2>/dev/null; then
  echo "❌ API Keys hardcodeadas"
  exit 1
fi
echo "✅ Verificación pasada"

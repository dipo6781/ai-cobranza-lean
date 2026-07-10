# 🚀 FLUJO DE TRABAJO DEL DESARROLLADOR

**Versión:** 1.0 | **Fecha:** 2026-07-09

## 🌿 ESTRATEGIA DE RAMAS

```
main (producción - PROTEGIDA)
  ├── develop (integración)
  │    ├── feature/*
  │    └── hotfix/*
```

## 🔄 FLUJO RÁPIDO

1. `./scripts/new-feature.sh nombre` - Crear rama
2. Desarrollar y commitear
3. `./scripts/create-pr.sh "Título"` - Crear PR
4. Merge en GitHub
5. `./scripts/deploy-to-prod.sh` - Deploy

## 🔐 REGLAS

- NUNCA commitear `.env`
- Usar `./scripts/pre-push-check.sh` antes de push
- Rollback: `git revert <commit> && git push`

# Veille Techno & Automatisation N8N

[![GitHub](https://img.shields.io/badge/GitHub-veille--techno--auto-blue)](https://github.com/AuraStackAI-Agency/veille-techno-auto)
[![Status](https://img.shields.io/badge/Status-DEPLOYED-success)](https://n8n.aurastackai.com)

## Description
Système automatisé de veille technologique (IA, N8N, Automatisation) agrégant des sources US, EU et CN.
Le système utilise N8N pour l'orchestration et un LLM local (Qwen 2.5 Coder 3B) sur VPS pour le résumé et la traduction.

## Fonctionnalités
- Collecte automatique de sources RSS (US, EU, CN)
- Résumés IA via Qwen 2.5 Coder 3B (local)
- Newsletter quotidienne par email (08h00)
- Orchestration avec N8N
- Filtrage intelligent par mots-clés IA

## Architecture
```
Trigger Cron (07:00)
  ↓
Collecte Sources (7 flux RSS en parallèle)
  ↓
Merge → Filter 24h → Filter Keywords
  ↓
Loop Items → Qwen 2.5 (Résumés)
  ↓
Agrégation → Qwen 2.5 (Newsletter)
  ↓
Format HTML → Email (08:00)
```

## Déploiement

### Prérequis
- N8N instance (existante sur le VPS)
- Ollama avec `qwen2.5-coder:3b-instruct`
- Credentials SMTP configurés dans N8N

### Installation
1. Importer `workflows/tech_watch_main.json` dans N8N
2. Configurer les credentials SMTP
3. Activer le workflow

**Note**: Ce projet utilise l'instance N8N existante sur `https://n8n.aurastackai.com` et Ollama sur le VPS.

## Sources Couvertes

### RSS
- **US** : OpenAI, Google AI, Anthropic, TechCrunch AI
- **EU** : Mistral AI, N8N Blog
- **N8N** : GitHub Releases (Atom Feed)

### Mots-clés de filtrage
`AI|LLM|GPT|Claude|automation|n8n|agent|workflow|machine learning|neural|transformer`

## Stack Technique

| Composant | Détail |
|-----------|--------|
| Orchestration | N8N (existant sur VPS) |
| IA | Ollama + qwen2.5-coder:3b-instruct |
| Endpoint Ollama | http://ollama:11434 |
| Timezone | Europe/Paris |

## Configuration

Le workflow utilise :
- **Cron** : `0 7 * * *` (tous les jours à 07h00)
- **Limit** : 15 articles max par newsletter
- **Timeout Ollama** : 60s (résumé), 120s (newsletter)

## Licence

MIT

## Contributeurs

AuraStackAI-Agency

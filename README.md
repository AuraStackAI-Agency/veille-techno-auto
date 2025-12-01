# Veille Techno & Automatisation N8N

## Description
Système automatisé de veille technologique (IA, N8N, Automatisation) agrégant des sources US, EU et CN.
Le système utilise N8N pour l'orchestration et un LLM local (Qwen 2.5 Coder 3B) sur VPS pour le résumé et la traduction.

## Architecture
- **Orchestrateur** : N8N
- **IA Locale** : Ollama + qwen2.5-coder:3b-instruct
- **Sources** : RSS, YouTube (Transcripts)
- **Sortie** : Newsletter Email quotidienne (08h00)

## Installation
Voir `docs/INSTALL.md` (à venir).

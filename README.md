# Veille Techno & Automatisation N8N

[![GitHub](https://img.shields.io/badge/GitHub-veille--techno--auto-blue)](https://github.com/AuraStackAI-Agency/veille-techno-auto)

## 📋 Description
Système automatisé de veille technologique (IA, N8N, Automatisation) agrégant des sources US, EU et CN.
Le système utilise N8N pour l'orchestration et un LLM local (Qwen 2.5 Coder 3B) sur VPS pour le résumé et la traduction.

## ✨ Fonctionnalités
- 📰 Collecte automatique de sources RSS (US, EU, CN)
- 🎥 Analyse de transcriptions YouTube
- 🤖 Résumés IA via Qwen 2.5 Coder 3B (local)
- 📧 Newsletter quotidienne par email (08h00)
- 🔄 Orchestration avec N8N
- 🐳 Déploiement Docker

## 🏗️ Architecture
```
Trigger Cron (07:00)
  ↓
Collecte Sources (RSS + YouTube)
  ↓
Filtrage Mots-clés
  ↓
Qwen 2.5 Coder 3B (Résumés)
  ↓
Agrégation Newsletter
  ↓
Email (08:00)
```

## 📦 Installation

Voir [docs/INSTALL.md](docs/INSTALL.md)

## 📚 Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Installation](docs/INSTALL.md)

## 🎯 Sources Couvertes

### RSS
- **US** : OpenAI, Google AI, Microsoft AI, Anthropic, TechCrunch AI
- **EU** : Mistral AI, N8N Blog, Sifted
- **CN** : TechNode, SCMP Tech
- **Concurrents** : Zapier, Make, ActivePieces, Flowise

### YouTube
- N8N Official
- Liam Ottley
- AI Explained
- Two Minute Papers

## 🛠️ Technologies

- **Orchestration** : N8N
- **IA** : Ollama + qwen2.5-coder:3b-instruct
- **Conteneurs** : Docker
- **Langages** : Python, JSON

## 📝 Licence

MIT

## 👥 Contributeurs

AuraStackAI-Agency

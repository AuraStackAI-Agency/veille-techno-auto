# Veille Techno Auto - L'Usine de Veille Intelligente

[![GitHub](https://img.shields.io/badge/GitHub-veille--techno--auto-blue)](https://github.com/AuraStackAI-Agency/veille-techno-auto)
[![Stack](https://img.shields.io/badge/Stack-N8N%20%2B%20Ollama%20%2B%20AuraCore-green)](https://github.com/AuraStackAI-Agency/VPS-debian)
[![Cost](https://img.shields.io/badge/API%20Cost-Zero-brightgreen)]()

## Description

Système autonome de veille technologique utilisant une architecture **dual-LLM avec vérification anti-hallucination**. Les LLMs (Qwen/Phi) s'appuient obligatoirement sur **AuraCore MCP** pour récupérer les règles de pertinence, vérifier les informations, et tracer les décisions.

**Philosophie** : Zéro coût API, 100% local, filtrage sémantique intelligent.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    VEILLE TECHNO AUTO - ARCHITECTURE                │
└─────────────────────────────────────────────────────────────────────┘

                         ┌─────────────────┐
                         │   N8N (Router)  │
                         │   Orchestration │
                         └────────┬────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
        ▼                         ▼                         ▼
┌───────────────┐       ┌─────────────────┐       ┌───────────────┐
│   INGESTION   │       │   AGENT LOOP    │       │  DISTRIBUTION │
├───────────────┤       ├─────────────────┤       ├───────────────┤
│ • RSS Feeds   │       │ Qwen ◄──► Tools │       │ • Telegram    │
│ • YouTube     │       │   ▼             │       │ • Notion      │
│ • HackerNews  │       │ Phi  ◄──► Tools │       │ • Email       │
│ • Reddit      │       └────────┬────────┘       └───────────────┘
└───────────────┘                │
                                 ▼
                    ┌─────────────────────────┐
                    │   AuraCore MCP + HTTP   │
                    ├─────────────────────────┤
                    │ • Règles de pertinence  │
                    │ • Web Search (SearXNG)  │
                    │ • Crawling (Jina)       │
                    │ • Anti-duplication      │
                    │ • Audit des décisions   │
                    └─────────────────────────┘
```

## Fonctionnalités

### Dual-LLM avec Vérification
- **Qwen 2.5 (3B)** : Filtrage rapide, scoring, extraction mots-clés
- **Phi-3 (3.8B)** : Validation anti-clickbait, rédaction synthèse FR

### Anti-Hallucination
- Les LLMs **doivent** appeler AuraCore pour récupérer les règles
- Vérification des claims via recherche web (SearXNG)
- Traçabilité complète des décisions (audit log)

### Sources Couvertes
| Région | Sources |
|--------|---------|
| US | OpenAI, Google AI, Anthropic, TechCrunch AI |
| EU | Mistral AI, N8N Blog, Sifted |
| CN | TechNode, SCMP Tech |
| Tech | HackerNews, Reddit LocalLLaMA, GitHub Releases |

### Distribution Multi-Canal
- **Telegram** : Alertes instantanées "Pépite trouvée!"
- **Notion** : Base de données + drafts LinkedIn
- **Email** : Newsletter hebdomadaire

## Stack Technique

| Composant | Technologie | Rôle |
|-----------|-------------|------|
| Orchestration | N8N | Workflows, Agent Loop, Cron |
| LLM Local | Ollama (Qwen + Phi) | Analyse, Scoring, Rédaction |
| Context & Tools | AuraCore MCP | Règles, Mémoire, Vérification |
| Web Search | SearXNG (self-hosted) | Recherche sans API payante |
| Scraping | Jina Reader | Extraction contenu propre |
| Base de données | SQLite (via AuraCore) | Persistance |

## Installation Rapide

```bash
# 1. Cloner le repo
git clone https://github.com/AuraStackAI-Agency/veille-techno-auto.git
cd veille-techno-auto

# 2. Configuration
cp .env.example .env
# Éditer .env avec vos paramètres

# 3. Lancer les services
docker-compose up -d

# 4. Installer les modèles Ollama
ollama pull qwen2.5-coder:3b-instruct
ollama pull phi3:mini

# 5. Importer les workflows N8N
# Voir docs/INSTALL.md
```

## Documentation

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Architecture technique détaillée |
| [AURACORE-VEILLE.md](docs/AURACORE-VEILLE.md) | Spécifications des outils MCP |
| [N8N-AGENT-LOOP.md](docs/N8N-AGENT-LOOP.md) | Workflows et Agent Loop |
| [INSTALL.md](docs/INSTALL.md) | Guide d'installation complet |

## Valeur Ajoutée AuraStack

| Avantage | Description |
|----------|-------------|
| **Zéro API Cost** | Tout tourne en local (vs outils à 50$/mois) |
| **Filtrage Sémantique** | Fini le bruit, seul le pertinent passe |
| **Anti-Hallucination** | LLMs contraints par AuraCore (vérification) |
| **Multi-Modèle** | Qwen (rapide) filtre, Phi (précis) rédige |
| **Auditabilité** | Chaque décision est tracée et justifiée |

## Prérequis

- Docker & Docker Compose
- 8 vCPU, 16GB RAM minimum (32GB recommandé)
- Ollama installé avec Qwen et Phi
- VPS Debian/Ubuntu (voir [VPS-debian](https://github.com/AuraStackAI-Agency/VPS-debian))

## Licence

MIT

## Contributeurs

AuraStackAI-Agency

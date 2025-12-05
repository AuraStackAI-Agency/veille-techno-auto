# Architecture Technique - Veille Techno Auto

## Vue d'Ensemble

L'architecture repose sur le pattern **Agent Loop** où N8N orchestre les appels aux LLMs (Qwen/Phi) qui eux-mêmes s'appuient sur AuraCore MCP pour leurs outils et leur contexte.

```
┌─────────────────────────────────────────────────────────────────────┐
│                        ARCHITECTURE GLOBALE                         │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                           COUCHE PRÉSENTATION                       │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐      │
│  │ Telegram │    │  Notion  │    │  Email   │    │ LinkedIn │      │
│  │  (Bot)   │    │   (API)  │    │  (SMTP)  │    │  (Draft) │      │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘      │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        COUCHE ORCHESTRATION                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│                         ┌─────────────────┐                         │
│                         │      N8N        │                         │
│                         │                 │                         │
│                         │  • Cron Trigger │                         │
│                         │  • Agent Loop   │                         │
│                         │  • Routing      │                         │
│                         │  • HTTP Client  │                         │
│                         └────────┬────────┘                         │
│                                  │                                  │
└──────────────────────────────────┼──────────────────────────────────┘
                                   │
          ┌────────────────────────┼────────────────────────┐
          │                        │                        │
          ▼                        ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    INGESTION    │    │   PROCESSING    │    │    SERVICES     │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│                 │    │                 │    │                 │
│  RSS Parser     │    │  Ollama API     │    │  AuraCore HTTP  │
│  YouTube API    │    │  ├─ Qwen 2.5    │    │  ├─ Rules       │
│  Reddit RSS     │    │  └─ Phi-3       │    │  ├─ Search      │
│  HN RSS         │    │                 │    │  ├─ Crawl       │
│                 │    │  Function Call  │    │  └─ Memory      │
│                 │    │  Tool Routing   │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                                                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        COUCHE PERSISTENCE                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    AuraCore MCP + SQLite                     │   │
│  ├─────────────────────────────────────────────────────────────┤   │
│  │                                                             │   │
│  │  Tables Existantes          Tables Veille (Nouvelles)       │   │
│  │  ─────────────────          ─────────────────────────       │   │
│  │  • projects                 • veille_rules                  │   │
│  │  • context                  • veille_articles               │   │
│  │  • tasks                    • veille_sources                │   │
│  │  • session_memory           • veille_decisions              │   │
│  │  • decision_log                                             │   │
│  │                                                             │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       SERVICES EXTERNES                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │
│  │   SearXNG    │    │ Jina Reader  │    │    Ollama    │          │
│  │  (Search)    │    │   (Scrape)   │    │    (LLM)     │          │
│  │              │    │              │    │              │          │
│  │ Self-hosted  │    │  API Free    │    │ Self-hosted  │          │
│  │ Port 8080    │    │ r.jina.ai    │    │ Port 11434   │          │
│  └──────────────┘    └──────────────┘    └──────────────┘          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Les 4 Phases du Workflow

### Phase 1 : Ingestion

```
┌─────────────────────────────────────────────────────────────────────┐
│                      PHASE 1 : INGESTION                            │
└─────────────────────────────────────────────────────────────────────┘

Cron Trigger (toutes les 2 heures)
         │
         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        SOURCES RSS                                  │
├──────────────────┬──────────────────┬───────────────────────────────┤
│       US         │        EU        │           TECH                │
├──────────────────┼──────────────────┼───────────────────────────────┤
│ • OpenAI Blog    │ • Mistral AI     │ • HackerNews (AI)             │
│ • Google AI      │ • N8N Blog       │ • Reddit r/LocalLLaMA         │
│ • Anthropic      │ • Sifted         │ • GitHub n8n/releases         │
│ • Microsoft AI   │                  │ • GitHub ollama/releases      │
│ • TechCrunch AI  │                  │                               │
└──────────────────┴──────────────────┴───────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        SOURCES YOUTUBE                              │
├─────────────────────────────────────────────────────────────────────┤
│ • N8N Official (tutoriels)                                          │
│ • Liam Ottley (AI automation)                                       │
│ • AI Explained (analyses techniques)                                │
│ • Two Minute Papers (recherche)                                     │
│ • Matthew Berman (reviews)                                          │
└─────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    NORMALISATION                                    │
├─────────────────────────────────────────────────────────────────────┤
│ {                                                                   │
│   "id": "uuid",                                                     │
│   "url": "https://...",                                             │
│   "title": "...",                                                   │
│   "description": "...",                                             │
│   "source": "openai_blog",                                          │
│   "source_type": "rss|youtube",                                     │
│   "published_at": "2024-...",                                       │
│   "raw_content": null  // sera rempli si score > 7                  │
│ }                                                                   │
└─────────────────────────────────────────────────────────────────────┘
```

### Phase 2 : Tri Rapide (Qwen)

```
┌─────────────────────────────────────────────────────────────────────┐
│                 PHASE 2 : TRI RAPIDE (QWEN)                         │
└─────────────────────────────────────────────────────────────────────┘

Pour chaque article normalisé :
         │
         ▼
┌─────────────────────────────────────────────────────────────────────┐
│ N8N → Ollama (Qwen 2.5 3B) avec Function Calling                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  SYSTEM PROMPT:                                                     │
│  "Tu es un analyste de veille tech. Tu DOIS utiliser les outils    │
│   disponibles. Ne jamais inventer de données."                     │
│                                                                     │
│  TOOLS DISPONIBLES:                                                 │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ get_veille_rules()     → Récupère les règles de scoring     │   │
│  │ check_article_exists() → Vérifie si déjà traité             │   │
│  │ web_search()           → Recherche complémentaire           │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    AGENT LOOP (N8N)                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. Qwen demande: get_veille_rules()                               │
│     └─► N8N appelle AuraCore HTTP → retourne règles                │
│                                                                     │
│  2. Qwen demande: check_article_exists(url)                        │
│     └─► N8N appelle AuraCore HTTP → retourne {exists: false}       │
│                                                                     │
│  3. Qwen analyse et retourne:                                       │
│     {                                                               │
│       "score": 8,                                                   │
│       "keywords": ["ollama", "performance", "local-llm"],          │
│       "reasoning": "Sujet prioritaire selon règles..."             │
│     }                                                               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
         │
         ▼
    ┌────┴────┐
    │ Score   │
    │  >= 7?  │
    └────┬────┘
    YES  │  NO
    ▼    └──► Discard (log optionnel)
Phase 3
```

### Phase 3 : Validation (Phi)

```
┌─────────────────────────────────────────────────────────────────────┐
│               PHASE 3 : VALIDATION (PHI-3)                          │
└─────────────────────────────────────────────────────────────────────┘

Articles avec score >= 7 :
         │
         ▼
┌─────────────────────────────────────────────────────────────────────┐
│ ÉTAPE 1 : Récupération contenu complet                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  N8N → AuraCore HTTP : crawl_url(article.url)                      │
│       └─► Jina Reader : https://r.jina.ai/{url}                    │
│       └─► Retourne contenu markdown propre                         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────┐
│ ÉTAPE 2 : Validation Phi-3 avec Agent Loop                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  INPUT:                                                             │
│  • Contenu complet de l'article                                    │
│  • Analyse Qwen (score, keywords, reasoning)                       │
│  • Contexte: articles récents sur le même sujet                    │
│                                                                     │
│  TOOLS DISPONIBLES:                                                 │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ verify_fact(claim)        → Vérifie une affirmation         │   │
│  │ get_recent_articles()     → Contexte historique             │   │
│  │ web_search(query)         → Recherche complémentaire        │   │
│  │ log_decision()            → Trace la décision               │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  TÂCHES PHI:                                                        │
│  1. Vérifier que ce n'est pas du clickbait                         │
│  2. Vérifier les claims factuelles                                  │
│  3. Rédiger synthèse en français (ton expert, concret)             │
│  4. Générer 3 hashtags LinkedIn                                     │
│  5. Évaluer la confiance (0-1)                                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────┐
│ OUTPUT STRUCTURÉ                                                    │
├─────────────────────────────────────────────────────────────────────┤
│ {                                                                   │
│   "validated": true,                                                │
│   "confidence": 0.92,                                               │
│   "summary_fr": "• Point 1\n• Point 2\n• Point 3",                 │
│   "impact": "Pourquoi c'est important pour AuraStack...",          │
│   "hashtags": ["#LocalLLM", "#Ollama", "#IA"],                     │
│   "linkedin_draft": "...",                                          │
│   "reasoning": "Vérifié via sources GitHub et HN..."               │
│ }                                                                   │
└─────────────────────────────────────────────────────────────────────┘
```

### Phase 4 : Distribution

```
┌─────────────────────────────────────────────────────────────────────┐
│                   PHASE 4 : DISTRIBUTION                            │
└─────────────────────────────────────────────────────────────────────┘

Articles validés par Phi :
         │
         ├──────────────────────────────────────────────────────┐
         │                                                      │
         ▼                                                      ▼
┌─────────────────────┐                            ┌─────────────────────┐
│  TELEGRAM (Instant) │                            │  NOTION (Archive)   │
├─────────────────────┤                            ├─────────────────────┤
│                     │                            │                     │
│  Si confidence >0.9 │                            │  Pour TOUS les      │
│  ET score >= 8      │                            │  articles validés   │
│                     │                            │                     │
│  Message:           │                            │  Database:          │
│  "Pépite trouvée!"  │                            │  • Titre            │
│  [Titre]            │                            │  • Résumé FR        │
│  [Résumé 1 ligne]   │                            │  • Source           │
│  [URL]              │                            │  • Score            │
│                     │                            │  • Hashtags         │
│                     │                            │  • LinkedIn Draft   │
│                     │                            │  • Date             │
└─────────────────────┘                            └─────────────────────┘
         │
         │
         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    EMAIL (Newsletter Hebdo)                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Agrégation tous les dimanches 18h :                               │
│                                                                     │
│  ## Gros Titres de la Semaine                                      │
│  [Top 3 articles score >= 9]                                        │
│                                                                     │
│  ## Nouveautés N8N                                                  │
│  [Articles source = n8n]                                            │
│                                                                     │
│  ## Veille Concurrentielle                                          │
│  [Articles source = competitors]                                    │
│                                                                     │
│  ## Vidéos à ne pas manquer                                         │
│  [Articles source_type = youtube]                                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Pattern Agent Loop Détaillé

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PATTERN AGENT LOOP (N8N)                         │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  ┌─────────┐      ┌──────────────┐      ┌─────────────────┐        │
│  │  START  │─────►│ Call Ollama  │─────►│ Parse Response  │        │
│  └─────────┘      │ (with tools) │      └────────┬────────┘        │
│                   └──────────────┘               │                  │
│                          ▲                       ▼                  │
│                          │              ┌───────────────┐           │
│                          │              │  Has tool_    │           │
│                          │              │  calls?       │           │
│                          │              └───────┬───────┘           │
│                          │                YES   │   NO              │
│                          │                ▼     │                   │
│                          │       ┌────────────┐ │                   │
│                          │       │  Execute   │ │                   │
│                          │       │  Tool via  │ │                   │
│                          │       │  AuraCore  │ │                   │
│                          │       │  HTTP API  │ │                   │
│                          │       └─────┬──────┘ │                   │
│                          │             │        │                   │
│                          │             ▼        │                   │
│                          │       ┌───────────┐  │                   │
│                          │       │  Append   │  │                   │
│                          │       │  tool     │  │                   │
│                          │       │  result   │  │                   │
│                          │       │  to msgs  │  │                   │
│                          │       └─────┬─────┘  │                   │
│                          │             │        │                   │
│                          └─────────────┘        │                   │
│                                                 ▼                   │
│                                         ┌─────────────┐             │
│                                         │   RETURN    │             │
│                                         │   Final     │             │
│                                         │   Response  │             │
│                                         └─────────────┘             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

Limite : Max 5 iterations pour éviter boucles infinies
```

## Communication Inter-Services

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ENDPOINTS HTTP (AuraCore)                        │
└─────────────────────────────────────────────────────────────────────┘

Base URL: http://auracore:3100/api

┌────────────────────┬────────┬───────────────────────────────────────┐
│     Endpoint       │ Method │            Description                │
├────────────────────┼────────┼───────────────────────────────────────┤
│ /veille/rules      │  GET   │ Récupère toutes les règles actives   │
│ /veille/rules      │  POST  │ Ajoute/modifie une règle             │
│ /veille/articles   │  GET   │ Liste articles (filtres: days, src)  │
│ /veille/articles   │  POST  │ Log un article traité                │
│ /veille/check      │  POST  │ Vérifie si article existe (par URL)  │
│ /veille/decisions  │  POST  │ Log une décision LLM                 │
│ /search            │  POST  │ Recherche web via SearXNG            │
│ /crawl             │  POST  │ Extrait contenu via Jina Reader      │
│ /health            │  GET   │ Health check                         │
└────────────────────┴────────┴───────────────────────────────────────┘
```

## Schéma Base de Données (Nouvelles Tables)

```sql
-- Table des règles de pertinence
CREATE TABLE veille_rules (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    type TEXT CHECK(type IN ('include', 'exclude', 'boost')) NOT NULL,
    keywords TEXT NOT NULL,  -- JSON array: ["ollama", "local llm"]
    score_modifier INTEGER DEFAULT 0,  -- +2, -5, etc.
    priority TEXT CHECK(priority IN ('critical', 'high', 'medium', 'low')) DEFAULT 'medium',
    active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table des articles traités
CREATE TABLE veille_articles (
    id TEXT PRIMARY KEY,
    url TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    source TEXT NOT NULL,
    source_type TEXT CHECK(source_type IN ('rss', 'youtube', 'reddit', 'hn')) NOT NULL,
    qwen_score INTEGER,
    qwen_keywords TEXT,  -- JSON array
    phi_validated BOOLEAN DEFAULT FALSE,
    phi_confidence REAL,
    summary_fr TEXT,
    impact TEXT,
    hashtags TEXT,  -- JSON array
    linkedin_draft TEXT,
    raw_content TEXT,
    published_at DATETIME,
    processed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    distributed_telegram BOOLEAN DEFAULT FALSE,
    distributed_notion BOOLEAN DEFAULT FALSE,
    distributed_email BOOLEAN DEFAULT FALSE
);

-- Table des sources configurées
CREATE TABLE veille_sources (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT CHECK(type IN ('rss', 'youtube', 'reddit', 'hn')) NOT NULL,
    url TEXT NOT NULL,
    category TEXT,  -- US, EU, CN, TECH, COMPETITORS
    active BOOLEAN DEFAULT TRUE,
    last_fetch DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table d'audit des décisions LLM
CREATE TABLE veille_decisions (
    id TEXT PRIMARY KEY,
    article_id TEXT REFERENCES veille_articles(id),
    llm TEXT CHECK(llm IN ('qwen', 'phi')) NOT NULL,
    decision_type TEXT NOT NULL,  -- 'score', 'validate', 'reject', 'verify_fact'
    decision TEXT NOT NULL,
    confidence REAL,
    reasoning TEXT,
    tools_used TEXT,  -- JSON array des outils appelés
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Index pour les requêtes fréquentes
CREATE INDEX idx_articles_url ON veille_articles(url);
CREATE INDEX idx_articles_source ON veille_articles(source);
CREATE INDEX idx_articles_processed ON veille_articles(processed_at);
CREATE INDEX idx_decisions_article ON veille_decisions(article_id);
```

## Variables d'Environnement

```bash
# AuraCore
AURACORE_PORT=3100
AURACORE_DB_PATH=/data/auracore.db

# SearXNG
SEARXNG_URL=http://searxng:8080
SEARXNG_TIMEOUT=10000

# Jina Reader
JINA_READER_URL=https://r.jina.ai

# Ollama
OLLAMA_URL=http://ollama:11434
OLLAMA_MODEL_QWEN=qwen2.5-coder:3b-instruct
OLLAMA_MODEL_PHI=phi3:mini

# N8N
N8N_HOST=localhost
N8N_PORT=5678

# Distribution
TELEGRAM_BOT_TOKEN=xxx
TELEGRAM_CHAT_ID=xxx
NOTION_API_KEY=xxx
NOTION_DATABASE_ID=xxx
SMTP_HOST=xxx
SMTP_USER=xxx
SMTP_PASS=xxx
EMAIL_TO=xxx
```

## Ressources Requises

| Service | CPU | RAM | Stockage |
|---------|-----|-----|----------|
| N8N | 1 vCPU | 1 GB | 1 GB |
| Ollama (Qwen) | 2 vCPU | 4 GB | 3 GB |
| Ollama (Phi) | 2 vCPU | 4 GB | 3 GB |
| AuraCore | 0.5 vCPU | 512 MB | 1 GB |
| SearXNG | 1 vCPU | 1 GB | 500 MB |
| **TOTAL** | **6.5 vCPU** | **10.5 GB** | **8.5 GB** |

Recommandé : VPS avec 8 vCPU, 16 GB RAM, 50 GB SSD

# AuraCore Veille - Spécifications des Outils MCP

## Vue d'Ensemble

AuraCore Veille est une extension du serveur MCP AuraCore qui ajoute des outils spécifiques pour la veille technologique. Ces outils permettent aux LLMs (Qwen/Phi) d'accéder à une source de vérité pour éviter les hallucinations.

## Architecture de l'Extension

```
┌─────────────────────────────────────────────────────────────────────┐
│                      AURACORE VEILLE EDITION                        │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                         SERVEUR MCP                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │                    OUTILS EXISTANTS (AuraCore)                 │ │
│  ├───────────────────────────────────────────────────────────────┤ │
│  │ • create_project    • store_context    • create_task          │ │
│  │ • list_projects     • query_context    • update_task          │ │
│  │ • get_project       • delete_context   • get_next_tasks       │ │
│  │ • update_project    • remember         • log_decision         │ │
│  │                     • recall           • get_decisions        │ │
│  │                     • forget                                  │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │                    OUTILS VEILLE (Nouveaux)                    │ │
│  ├───────────────────────────────────────────────────────────────┤ │
│  │ • get_veille_rules      • web_search       • log_article      │ │
│  │ • update_veille_rule    • crawl_url        • get_articles     │ │
│  │ • check_article_exists  • verify_fact      • log_veille_decision │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        API HTTP (Express)                           │
├─────────────────────────────────────────────────────────────────────┤
│  Port 3100 - Expose les outils MCP via REST pour N8N               │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      SERVICES EXTERNES                              │
├──────────────────────────┬──────────────────────────────────────────┤
│       SearXNG            │           Jina Reader                    │
│   (Web Search)           │         (URL Scraping)                   │
│   http://searxng:8080    │       https://r.jina.ai                  │
└──────────────────────────┴──────────────────────────────────────────┘
```

## Outils MCP Détaillés

### 1. get_veille_rules

Récupère les règles de pertinence actives pour le scoring des articles.

```typescript
// Définition MCP
{
  name: "get_veille_rules",
  description: "Récupère les règles de pertinence pour scorer les articles. DOIT être appelé avant toute analyse.",
  inputSchema: {
    type: "object",
    properties: {
      type: {
        type: "string",
        enum: ["include", "exclude", "boost", "all"],
        description: "Filtrer par type de règle (défaut: all)"
      },
      priority: {
        type: "string",
        enum: ["critical", "high", "medium", "low"],
        description: "Filtrer par priorité"
      }
    }
  }
}

// Exemple de réponse
{
  "rules": [
    {
      "name": "local_llm",
      "type": "include",
      "keywords": ["ollama", "llama.cpp", "local llm", "on-device ai"],
      "score_modifier": 3,
      "priority": "critical"
    },
    {
      "name": "n8n_automation",
      "type": "include",
      "keywords": ["n8n", "workflow automation", "no-code"],
      "score_modifier": 2,
      "priority": "high"
    },
    {
      "name": "crypto_spam",
      "type": "exclude",
      "keywords": ["crypto", "blockchain", "nft", "web3"],
      "score_modifier": -10,
      "priority": "critical"
    }
  ],
  "scoring_guide": {
    "base_score": 5,
    "min_valid_score": 7,
    "max_score": 10
  }
}
```

### 2. update_veille_rule

Ajoute ou modifie une règle de pertinence.

```typescript
// Définition MCP
{
  name: "update_veille_rule",
  description: "Ajoute ou modifie une règle de pertinence",
  inputSchema: {
    type: "object",
    properties: {
      name: {
        type: "string",
        description: "Identifiant unique de la règle"
      },
      type: {
        type: "string",
        enum: ["include", "exclude", "boost"],
        description: "Type de règle"
      },
      keywords: {
        type: "array",
        items: { type: "string" },
        description: "Liste de mots-clés associés"
      },
      score_modifier: {
        type: "integer",
        description: "Modificateur de score (-10 à +5)"
      },
      priority: {
        type: "string",
        enum: ["critical", "high", "medium", "low"]
      }
    },
    required: ["name", "type", "keywords"]
  }
}

// Exemple d'appel
{
  "name": "mcp_protocol",
  "type": "include",
  "keywords": ["model context protocol", "mcp server", "mcp client"],
  "score_modifier": 3,
  "priority": "high"
}
```

### 3. check_article_exists

Vérifie si un article a déjà été traité (anti-duplication).

```typescript
// Définition MCP
{
  name: "check_article_exists",
  description: "Vérifie si un article a déjà été traité. DOIT être appelé avant d'analyser un article.",
  inputSchema: {
    type: "object",
    properties: {
      url: {
        type: "string",
        description: "URL de l'article à vérifier"
      }
    },
    required: ["url"]
  }
}

// Exemple de réponse (article non traité)
{
  "exists": false,
  "message": "Article non trouvé dans la base"
}

// Exemple de réponse (article déjà traité)
{
  "exists": true,
  "article": {
    "id": "abc123",
    "title": "Ollama 0.5 Released",
    "processed_at": "2024-12-01T10:00:00Z",
    "qwen_score": 9,
    "phi_validated": true
  },
  "message": "Article déjà traité le 2024-12-01"
}
```

### 4. web_search

Effectue une recherche web via SearXNG (self-hosted).

```typescript
// Définition MCP
{
  name: "web_search",
  description: "Recherche des informations sur le web. Utiliser pour vérifier des faits ou trouver des sources complémentaires.",
  inputSchema: {
    type: "object",
    properties: {
      query: {
        type: "string",
        description: "Requête de recherche"
      },
      num_results: {
        type: "integer",
        default: 5,
        description: "Nombre de résultats (max 10)"
      },
      time_range: {
        type: "string",
        enum: ["day", "week", "month", "year"],
        description: "Filtrer par période"
      }
    },
    required: ["query"]
  }
}

// Exemple de réponse
{
  "query": "Ollama 0.5 release performance",
  "results": [
    {
      "title": "Ollama 0.5.0 Release Notes",
      "url": "https://github.com/ollama/ollama/releases/tag/v0.5.0",
      "snippet": "Performance improvements: 40-50% faster inference on Apple Silicon...",
      "source": "github.com"
    },
    {
      "title": "Ollama 0.5 benchmarks show major speedup",
      "url": "https://news.ycombinator.com/item?id=...",
      "snippet": "Real-world tests confirm the claimed performance gains...",
      "source": "news.ycombinator.com"
    }
  ],
  "total_found": 2
}
```

### 5. crawl_url

Extrait le contenu propre d'une URL via Jina Reader.

```typescript
// Définition MCP
{
  name: "crawl_url",
  description: "Extrait le contenu textuel propre d'une page web. Utiliser pour obtenir le texte complet d'un article.",
  inputSchema: {
    type: "object",
    properties: {
      url: {
        type: "string",
        description: "URL de la page à extraire"
      }
    },
    required: ["url"]
  }
}

// Exemple de réponse
{
  "url": "https://blog.ollama.com/ollama-0-5",
  "title": "Announcing Ollama 0.5",
  "content": "Today we're releasing Ollama 0.5, our biggest update yet...\n\n## Performance Improvements\n\nWe've achieved 40-50% faster inference...",
  "word_count": 1250,
  "extracted_at": "2024-12-05T14:30:00Z"
}
```

### 6. verify_fact

Vérifie une affirmation factuelle via recherche web.

```typescript
// Définition MCP
{
  name: "verify_fact",
  description: "Vérifie si une affirmation est vraie en recherchant des sources. Utiliser pour éviter de propager des informations incorrectes.",
  inputSchema: {
    type: "object",
    properties: {
      claim: {
        type: "string",
        description: "L'affirmation à vérifier"
      },
      context: {
        type: "string",
        description: "Contexte additionnel pour affiner la recherche"
      }
    },
    required: ["claim"]
  }
}

// Exemple de réponse
{
  "claim": "Ollama 0.5 is 50% faster than 0.4",
  "verified": true,
  "confidence": 0.85,
  "sources": [
    {
      "url": "https://github.com/ollama/ollama/releases",
      "excerpt": "40-50% faster inference on Apple Silicon"
    }
  ],
  "summary": "Claim partially verified. Official release notes mention 40-50% improvement, specifically on Apple Silicon. Performance may vary on other hardware."
}
```

### 7. log_article

Enregistre un article traité dans la base de données.

```typescript
// Définition MCP
{
  name: "log_article",
  description: "Enregistre un article analysé dans la base. DOIT être appelé après chaque analyse complète.",
  inputSchema: {
    type: "object",
    properties: {
      url: { type: "string" },
      title: { type: "string" },
      source: { type: "string" },
      source_type: {
        type: "string",
        enum: ["rss", "youtube", "reddit", "hn"]
      },
      qwen_score: { type: "integer" },
      qwen_keywords: {
        type: "array",
        items: { type: "string" }
      },
      phi_validated: { type: "boolean" },
      phi_confidence: { type: "number" },
      summary_fr: { type: "string" },
      impact: { type: "string" },
      hashtags: {
        type: "array",
        items: { type: "string" }
      },
      linkedin_draft: { type: "string" },
      raw_content: { type: "string" }
    },
    required: ["url", "title", "source", "source_type"]
  }
}

// Exemple d'appel
{
  "url": "https://blog.ollama.com/ollama-0-5",
  "title": "Announcing Ollama 0.5",
  "source": "ollama_blog",
  "source_type": "rss",
  "qwen_score": 9,
  "qwen_keywords": ["ollama", "performance", "local-llm"],
  "phi_validated": true,
  "phi_confidence": 0.92,
  "summary_fr": "• Ollama 0.5 améliore les performances de 40-50%\n• Optimisé pour Apple Silicon\n• Nouvelles options de quantization",
  "impact": "Rend l'inférence locale plus viable pour la production",
  "hashtags": ["#Ollama", "#LocalLLM", "#IA"],
  "linkedin_draft": "Ollama 0.5 vient de sortir avec des gains de performance impressionnants..."
}
```

### 8. get_articles

Récupère les articles traités récemment (pour contexte).

```typescript
// Définition MCP
{
  name: "get_articles",
  description: "Récupère les articles récents pour fournir du contexte. Utiliser pour éviter les répétitions et comprendre les tendances.",
  inputSchema: {
    type: "object",
    properties: {
      days: {
        type: "integer",
        default: 7,
        description: "Nombre de jours à récupérer"
      },
      source: {
        type: "string",
        description: "Filtrer par source"
      },
      validated_only: {
        type: "boolean",
        default: true,
        description: "Uniquement les articles validés par Phi"
      },
      limit: {
        type: "integer",
        default: 20,
        description: "Nombre max d'articles"
      }
    }
  }
}

// Exemple de réponse
{
  "articles": [
    {
      "title": "N8N 1.70 Released",
      "source": "n8n_blog",
      "qwen_score": 8,
      "summary_fr": "Nouvelles nodes pour...",
      "processed_at": "2024-12-04T08:00:00Z"
    }
  ],
  "total": 1,
  "period": "7 days"
}
```

### 9. log_veille_decision

Trace une décision du LLM pour l'audit.

```typescript
// Définition MCP
{
  name: "log_veille_decision",
  description: "Enregistre une décision d'analyse pour l'audit. DOIT être appelé après chaque décision importante.",
  inputSchema: {
    type: "object",
    properties: {
      article_id: {
        type: "string",
        description: "ID de l'article concerné (optionnel si décision générale)"
      },
      llm: {
        type: "string",
        enum: ["qwen", "phi"],
        description: "LLM ayant pris la décision"
      },
      decision_type: {
        type: "string",
        enum: ["score", "validate", "reject", "verify_fact"],
        description: "Type de décision"
      },
      decision: {
        type: "string",
        description: "La décision prise"
      },
      confidence: {
        type: "number",
        description: "Niveau de confiance (0-1)"
      },
      reasoning: {
        type: "string",
        description: "Justification de la décision"
      },
      tools_used: {
        type: "array",
        items: { type: "string" },
        description: "Outils appelés pour cette décision"
      }
    },
    required: ["llm", "decision_type", "decision"]
  }
}

// Exemple d'appel
{
  "article_id": "abc123",
  "llm": "phi",
  "decision_type": "validate",
  "decision": "Article validé pour distribution",
  "confidence": 0.92,
  "reasoning": "Information vérifiée via GitHub releases. Sujet prioritaire (local LLM). Pas de clickbait détecté.",
  "tools_used": ["get_veille_rules", "verify_fact", "web_search"]
}
```

## API HTTP (pour N8N)

AuraCore Veille expose également une API REST pour permettre à N8N d'appeler les outils.

### Endpoints

```
Base URL: http://auracore:3100/api
```

| Endpoint | Method | Body | Description |
|----------|--------|------|-------------|
| `/veille/rules` | GET | - | get_veille_rules |
| `/veille/rules` | POST | `{name, type, keywords, ...}` | update_veille_rule |
| `/veille/check` | POST | `{url}` | check_article_exists |
| `/veille/articles` | GET | `?days=7&source=...` | get_articles |
| `/veille/articles` | POST | `{url, title, ...}` | log_article |
| `/veille/decisions` | POST | `{llm, decision_type, ...}` | log_veille_decision |
| `/search` | POST | `{query, num_results}` | web_search |
| `/crawl` | POST | `{url}` | crawl_url |
| `/verify` | POST | `{claim, context}` | verify_fact |
| `/health` | GET | - | Health check |

### Exemple d'appel HTTP (depuis N8N)

```javascript
// HTTP Request Node - Get Rules
{
  "method": "GET",
  "url": "http://auracore:3100/api/veille/rules",
  "headers": {
    "Content-Type": "application/json"
  }
}

// HTTP Request Node - Web Search
{
  "method": "POST",
  "url": "http://auracore:3100/api/search",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "query": "{{ $json.search_query }}",
    "num_results": 5
  }
}
```

## Structure du Code Source

```
auracore-mcp/
├── src/
│   ├── index.ts              # Point d'entrée MCP + HTTP server
│   ├── database.ts           # Initialisation SQLite + migrations
│   ├── types.ts              # Interfaces TypeScript
│   ├── tools/
│   │   ├── core.ts           # Outils AuraCore existants
│   │   └── veille.ts         # Outils Veille (nouveaux)
│   ├── services/
│   │   ├── searxng.ts        # Client SearXNG
│   │   └── jina.ts           # Client Jina Reader
│   └── http/
│       ├── server.ts         # Express server
│       └── routes/
│           ├── veille.ts     # Routes /veille/*
│           └── search.ts     # Routes /search, /crawl, /verify
├── package.json
├── tsconfig.json
└── Dockerfile
```

## Dépendances

```json
{
  "dependencies": {
    "@modelcontextprotocol/sdk": "^1.0.0",
    "express": "^4.18.2",
    "sql.js": "^1.10.0",
    "uuid": "^9.0.0",
    "zod": "^3.22.0",
    "node-fetch": "^3.3.0"
  },
  "devDependencies": {
    "@types/express": "^4.17.21",
    "@types/node": "^20.10.0",
    "typescript": "^5.3.0"
  }
}
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
JINA_TIMEOUT=30000

# Logging
LOG_LEVEL=info
```

## Exemple de Session LLM

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SESSION QWEN - ANALYSE ARTICLE                   │
└─────────────────────────────────────────────────────────────────────┘

[USER] Analyse cet article: "Ollama 0.5 brings 50% faster inference"
       URL: https://blog.ollama.com/ollama-0-5

[QWEN] Je vais analyser cet article. D'abord, je récupère les règles.

       → tool_call: get_veille_rules()

[TOOL] {
         "rules": [
           {"name": "local_llm", "type": "include", "keywords": ["ollama", "local llm"], "score_modifier": 3}
         ],
         "scoring_guide": {"base_score": 5, "min_valid_score": 7}
       }

[QWEN] Règles reçues. Je vérifie si l'article existe déjà.

       → tool_call: check_article_exists(url="https://blog.ollama.com/ollama-0-5")

[TOOL] {"exists": false, "message": "Article non trouvé"}

[QWEN] Article nouveau. Le titre mentionne "50% faster", je vérifie cette claim.

       → tool_call: verify_fact(claim="Ollama 0.5 is 50% faster", context="inference performance")

[TOOL] {
         "verified": true,
         "confidence": 0.85,
         "sources": [{"url": "github.com/ollama/releases", "excerpt": "40-50% faster on Apple Silicon"}],
         "summary": "Claim verified with nuance: 40-50% on Apple Silicon specifically"
       }

[QWEN] Claim vérifiée. Je calcule le score:
       - Base: 5
       - Match "ollama" (local_llm rule): +3
       - Score final: 8/10

       {
         "score": 8,
         "keywords": ["ollama", "performance", "inference", "local-llm"],
         "reasoning": "Sujet prioritaire (local LLM), claim vérifiée via GitHub releases",
         "recommendation": "Passer à Phi pour validation complète"
       }

       → tool_call: log_veille_decision(
           llm="qwen",
           decision_type="score",
           decision="Score 8/10 - Recommandé pour validation",
           confidence=0.88,
           reasoning="Match règle local_llm, claim vérifiée",
           tools_used=["get_veille_rules", "check_article_exists", "verify_fact"]
         )

[TOOL] {"logged": true, "decision_id": "dec_123"}

[QWEN] Analyse terminée. Score: 8/10. Article recommandé pour validation Phi.
```

## Contraintes Anti-Hallucination

Les LLMs sont contraints par les règles suivantes dans leur system prompt :

```
RÈGLES OBLIGATOIRES:

1. Tu DOIS appeler get_veille_rules() avant toute analyse
2. Tu DOIS appeler check_article_exists() pour éviter les doublons
3. Tu DOIS appeler verify_fact() pour toute affirmation chiffrée ou claim technique
4. Tu DOIS appeler log_veille_decision() après chaque décision
5. Tu NE DOIS PAS inventer de données - si tu n'as pas l'info, utilise web_search()
6. Tu DOIS justifier ton score en référençant les règles récupérées
```

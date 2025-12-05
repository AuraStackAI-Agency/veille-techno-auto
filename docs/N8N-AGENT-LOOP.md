# N8N Agent Loop - Documentation des Workflows

## Vue d'Ensemble

Ce document décrit comment implémenter le pattern **Agent Loop** dans N8N pour permettre aux LLMs (Qwen/Phi) d'appeler des outils via AuraCore.

## Concept du Pattern Agent Loop

```
┌─────────────────────────────────────────────────────────────────────┐
│                      PATTERN AGENT LOOP                             │
└─────────────────────────────────────────────────────────────────────┘

Le LLM ne fait pas qu'analyser - il peut DEMANDER des outils.
N8N intercepte ces demandes, exécute les outils, et renvoie les résultats.

┌──────────┐         ┌──────────┐         ┌──────────┐
│   N8N    │◄───────►│  Ollama  │         │ AuraCore │
│ (Router) │         │  (LLM)   │         │  (Tools) │
└────┬─────┘         └──────────┘         └────┬─────┘
     │                                          │
     │  1. Envoie article + tools disponibles   │
     │────────────────────►                     │
     │                                          │
     │  2. LLM répond avec tool_call            │
     │◄────────────────────                     │
     │     {"tool": "get_veille_rules"}         │
     │                                          │
     │  3. N8N exécute l'outil sur AuraCore     │
     │──────────────────────────────────────────►
     │                                          │
     │  4. Résultat de l'outil                  │
     │◄──────────────────────────────────────────
     │                                          │
     │  5. N8N renvoie au LLM avec le résultat  │
     │────────────────────►                     │
     │                                          │
     │  6. LLM continue ou termine              │
     │◄────────────────────                     │
     │                                          │
     └── Répète jusqu'à réponse finale ─────────┘
```

## Structure des Workflows

```
workflows/
├── 01_main_scheduler.json       # Cron + orchestration
├── 02_ingest_rss.json           # Collecte RSS
├── 03_ingest_youtube.json       # Collecte YouTube
├── 04_agent_qwen.json           # Agent Loop Qwen (scoring)
├── 05_agent_phi.json            # Agent Loop Phi (validation)
├── 06_distribute.json           # Distribution multi-canal
└── 07_newsletter_weekly.json    # Agrégation newsletter
```

## Workflow Principal : Main Scheduler

```
┌─────────────────────────────────────────────────────────────────────┐
│               WORKFLOW: 01_main_scheduler.json                      │
└─────────────────────────────────────────────────────────────────────┘

┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│  Cron    │──►│ Execute  │──►│ Execute  │──►│  Merge   │
│ (2h)     │   │ Workflow │   │ Workflow │   │ Results  │
│          │   │ RSS      │   │ YouTube  │   │          │
└──────────┘   └──────────┘   └──────────┘   └────┬─────┘
                                                   │
                                                   ▼
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│  Done    │◄──│ Execute  │◄──│ Execute  │◄──│  Loop    │
│          │   │ Distrib  │   │ Phi      │   │ Articles │
└──────────┘   └──────────┘   └──────────┘   └──────────┘
                                   ▲
                                   │ (score >= 7 only)
                              ┌────┴─────┐
                              │ Execute  │
                              │ Qwen     │
                              └──────────┘
```

### Nodes du Main Scheduler

```json
{
  "nodes": [
    {
      "name": "Cron Trigger",
      "type": "n8n-nodes-base.scheduleTrigger",
      "parameters": {
        "rule": {
          "interval": [{ "field": "hours", "hoursInterval": 2 }]
        }
      }
    },
    {
      "name": "Execute RSS Ingestion",
      "type": "n8n-nodes-base.executeWorkflow",
      "parameters": {
        "workflowId": "={{ $workflow.id('02_ingest_rss') }}"
      }
    },
    {
      "name": "Execute YouTube Ingestion",
      "type": "n8n-nodes-base.executeWorkflow",
      "parameters": {
        "workflowId": "={{ $workflow.id('03_ingest_youtube') }}"
      }
    },
    {
      "name": "Merge Results",
      "type": "n8n-nodes-base.merge",
      "parameters": {
        "mode": "append"
      }
    },
    {
      "name": "Loop Articles",
      "type": "n8n-nodes-base.splitInBatches",
      "parameters": {
        "batchSize": 1
      }
    },
    {
      "name": "Execute Qwen Agent",
      "type": "n8n-nodes-base.executeWorkflow",
      "parameters": {
        "workflowId": "={{ $workflow.id('04_agent_qwen') }}",
        "workflowInputs": {
          "article": "={{ $json }}"
        }
      }
    },
    {
      "name": "Check Score",
      "type": "n8n-nodes-base.if",
      "parameters": {
        "conditions": {
          "number": [{
            "value1": "={{ $json.score }}",
            "operation": "largerEqual",
            "value2": 7
          }]
        }
      }
    },
    {
      "name": "Execute Phi Agent",
      "type": "n8n-nodes-base.executeWorkflow",
      "parameters": {
        "workflowId": "={{ $workflow.id('05_agent_phi') }}",
        "workflowInputs": {
          "article": "={{ $json.article }}",
          "qwen_analysis": "={{ $json }}"
        }
      }
    },
    {
      "name": "Execute Distribution",
      "type": "n8n-nodes-base.executeWorkflow",
      "parameters": {
        "workflowId": "={{ $workflow.id('06_distribute') }}",
        "workflowInputs": {
          "validated_article": "={{ $json }}"
        }
      }
    }
  ]
}
```

## Workflow Agent Loop : Qwen

```
┌─────────────────────────────────────────────────────────────────────┐
│                 WORKFLOW: 04_agent_qwen.json                        │
└─────────────────────────────────────────────────────────────────────┘

┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│ Workflow │──►│  Build   │──►│  Call    │──►│  Parse   │
│  Input   │   │  Prompt  │   │  Ollama  │   │ Response │
└──────────┘   └──────────┘   └──────────┘   └────┬─────┘
                                                   │
                     ┌─────────────────────────────┤
                     │                             │
                     ▼                             ▼
              ┌─────────────┐              ┌─────────────┐
              │ Has tool_   │──► YES ──►  │  Execute    │
              │ calls?      │              │  Tool       │
              └─────────────┘              └──────┬──────┘
                     │                            │
                     │ NO                         │
                     ▼                            ▼
              ┌─────────────┐              ┌─────────────┐
              │  Return     │              │  Append to  │
              │  Final      │◄─────────────│  Messages   │
              │  Response   │              │  & Loop     │
              └─────────────┘              └─────────────┘
```

### Code Node : Build Prompt with Tools

```javascript
// Code Node: Build Qwen Prompt with Tools
const article = $input.first().json.article;

const systemPrompt = `Tu es un analyste de veille technologique pour AuraStack.

RÈGLES OBLIGATOIRES:
1. Tu DOIS appeler get_veille_rules() avant toute analyse
2. Tu DOIS appeler check_article_exists() pour vérifier les doublons
3. Tu DOIS appeler verify_fact() pour toute affirmation chiffrée
4. Tu DOIS appeler log_veille_decision() après ta décision finale
5. Tu NE DOIS PAS inventer de données

FORMAT DE RÉPONSE FINALE (après avoir utilisé les outils):
{
  "score": <0-10>,
  "keywords": ["mot1", "mot2", "mot3"],
  "reasoning": "<justification basée sur les règles>",
  "recommendation": "<pass_to_phi | discard>"
}`;

const tools = [
  {
    type: "function",
    function: {
      name: "get_veille_rules",
      description: "Récupère les règles de pertinence. DOIT être appelé en premier.",
      parameters: { type: "object", properties: {} }
    }
  },
  {
    type: "function",
    function: {
      name: "check_article_exists",
      description: "Vérifie si l'article a déjà été traité",
      parameters: {
        type: "object",
        properties: {
          url: { type: "string", description: "URL de l'article" }
        },
        required: ["url"]
      }
    }
  },
  {
    type: "function",
    function: {
      name: "verify_fact",
      description: "Vérifie une affirmation via recherche web",
      parameters: {
        type: "object",
        properties: {
          claim: { type: "string", description: "L'affirmation à vérifier" },
          context: { type: "string", description: "Contexte additionnel" }
        },
        required: ["claim"]
      }
    }
  },
  {
    type: "function",
    function: {
      name: "web_search",
      description: "Recherche web pour informations complémentaires",
      parameters: {
        type: "object",
        properties: {
          query: { type: "string", description: "Requête de recherche" },
          num_results: { type: "integer", description: "Nombre de résultats (défaut: 5)" }
        },
        required: ["query"]
      }
    }
  },
  {
    type: "function",
    function: {
      name: "log_veille_decision",
      description: "Enregistre la décision pour audit. DOIT être appelé à la fin.",
      parameters: {
        type: "object",
        properties: {
          decision_type: { type: "string", enum: ["score", "validate", "reject"] },
          decision: { type: "string", description: "La décision prise" },
          confidence: { type: "number", description: "Confiance 0-1" },
          reasoning: { type: "string", description: "Justification" },
          tools_used: { type: "array", items: { type: "string" } }
        },
        required: ["decision_type", "decision"]
      }
    }
  }
];

const messages = [
  { role: "system", content: systemPrompt },
  {
    role: "user",
    content: `Analyse cet article:

Titre: ${article.title}
URL: ${article.url}
Source: ${article.source}
Description: ${article.description || 'N/A'}

Utilise les outils disponibles pour une analyse complète.`
  }
];

return {
  json: {
    messages,
    tools,
    model: "qwen2.5-coder:3b-instruct",
    article,
    iteration: 0,
    max_iterations: 5
  }
};
```

### HTTP Request Node : Call Ollama

```json
{
  "name": "Call Ollama",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "method": "POST",
    "url": "http://ollama:11434/api/chat",
    "sendBody": true,
    "bodyParameters": {
      "parameters": [
        {
          "name": "model",
          "value": "={{ $json.model }}"
        },
        {
          "name": "messages",
          "value": "={{ $json.messages }}"
        },
        {
          "name": "tools",
          "value": "={{ $json.tools }}"
        },
        {
          "name": "stream",
          "value": false
        }
      ]
    },
    "options": {
      "timeout": 120000
    }
  }
}
```

### Code Node : Parse Response & Route

```javascript
// Code Node: Parse Ollama Response
const input = $input.first().json;
const response = input.response;
const prevMessages = input.messages;
const tools = input.tools;
const article = input.article;
const iteration = input.iteration || 0;
const maxIterations = input.max_iterations || 5;

const assistantMessage = response.message;

// Vérifier s'il y a des tool_calls
if (assistantMessage.tool_calls && assistantMessage.tool_calls.length > 0) {
  // Le LLM veut appeler des outils
  return {
    json: {
      has_tool_calls: true,
      tool_calls: assistantMessage.tool_calls,
      messages: [...prevMessages, assistantMessage],
      tools,
      article,
      iteration: iteration + 1,
      max_iterations: maxIterations
    }
  };
} else {
  // Réponse finale
  let finalResponse;
  try {
    // Essayer de parser comme JSON
    const content = assistantMessage.content;
    const jsonMatch = content.match(/\{[\s\S]*\}/);
    finalResponse = jsonMatch ? JSON.parse(jsonMatch[0]) : { raw: content };
  } catch (e) {
    finalResponse = { raw: assistantMessage.content };
  }

  return {
    json: {
      has_tool_calls: false,
      final_response: finalResponse,
      article,
      score: finalResponse.score || 0,
      keywords: finalResponse.keywords || [],
      reasoning: finalResponse.reasoning || ''
    }
  };
}
```

### Switch Node : Route by Tool Calls

```json
{
  "name": "Has Tool Calls?",
  "type": "n8n-nodes-base.if",
  "parameters": {
    "conditions": {
      "boolean": [{
        "value1": "={{ $json.has_tool_calls }}",
        "value2": true
      }]
    }
  }
}
```

### Code Node : Execute Tools

```javascript
// Code Node: Execute Tool Calls
const input = $input.first().json;
const toolCalls = input.tool_calls;
const messages = input.messages;
const tools = input.tools;
const article = input.article;

// Préparer les appels HTTP vers AuraCore
const toolResults = [];

for (const toolCall of toolCalls) {
  const toolName = toolCall.function.name;
  const args = JSON.parse(toolCall.function.arguments || '{}');

  let endpoint, method, body;

  switch (toolName) {
    case 'get_veille_rules':
      endpoint = '/api/veille/rules';
      method = 'GET';
      break;
    case 'check_article_exists':
      endpoint = '/api/veille/check';
      method = 'POST';
      body = { url: args.url || article.url };
      break;
    case 'verify_fact':
      endpoint = '/api/verify';
      method = 'POST';
      body = { claim: args.claim, context: args.context };
      break;
    case 'web_search':
      endpoint = '/api/search';
      method = 'POST';
      body = { query: args.query, num_results: args.num_results || 5 };
      break;
    case 'log_veille_decision':
      endpoint = '/api/veille/decisions';
      method = 'POST';
      body = {
        llm: 'qwen',
        ...args
      };
      break;
    default:
      toolResults.push({
        tool_call_id: toolCall.id,
        result: { error: `Unknown tool: ${toolName}` }
      });
      continue;
  }

  toolResults.push({
    tool_call_id: toolCall.id,
    endpoint,
    method,
    body,
    tool_name: toolName
  });
}

return {
  json: {
    tool_executions: toolResults,
    messages,
    tools,
    article,
    iteration: input.iteration,
    max_iterations: input.max_iterations
  }
};
```

### HTTP Request Node : Call AuraCore Tools

```json
{
  "name": "Call AuraCore Tool",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "method": "={{ $json.method }}",
    "url": "=http://auracore:3100{{ $json.endpoint }}",
    "sendBody": true,
    "bodyParameters": {
      "parameters": "={{ $json.body }}"
    },
    "options": {
      "timeout": 30000
    }
  }
}
```

### Code Node : Append Tool Results & Loop

```javascript
// Code Node: Append Tool Results to Messages
const input = $input.first().json;
const toolResults = input.tool_results; // Résultats des appels HTTP
const messages = input.messages;
const tools = input.tools;
const article = input.article;

// Ajouter les résultats comme messages "tool"
for (const result of toolResults) {
  messages.push({
    role: "tool",
    tool_call_id: result.tool_call_id,
    content: JSON.stringify(result.response)
  });
}

// Vérifier la limite d'itérations
if (input.iteration >= input.max_iterations) {
  return {
    json: {
      error: "Max iterations reached",
      article,
      score: 0,
      reasoning: "Agent loop exceeded max iterations"
    }
  };
}

// Retourner pour un nouveau cycle
return {
  json: {
    messages,
    tools,
    article,
    model: "qwen2.5-coder:3b-instruct",
    iteration: input.iteration,
    max_iterations: input.max_iterations
  }
};
```

## Workflow Agent Loop : Phi

Le workflow Phi est similaire à Qwen, avec ces différences :

### System Prompt Phi

```javascript
const systemPrompt = `Tu es le rédacteur en chef de la veille technologique AuraStack.

Tu reçois un article PRÉ-FILTRÉ par Qwen avec un score >= 7.

TES TÂCHES:
1. Vérifier que ce n'est pas du clickbait (appeler verify_fact si doute)
2. Récupérer le contenu complet (crawl_url)
3. Vérifier le contexte historique (get_articles récents sur le sujet)
4. Rédiger une synthèse en français (ton expert, concret)
5. Évaluer ta confiance (0-1)
6. Générer 3 hashtags LinkedIn
7. Rédiger un draft LinkedIn

RÈGLES:
- Tu DOIS vérifier les claims importantes
- Tu DOIS consulter les articles récents pour le contexte
- Tu DOIS logger ta décision finale

FORMAT DE RÉPONSE FINALE:
{
  "validated": true|false,
  "confidence": <0-1>,
  "summary_fr": "• Point 1\\n• Point 2\\n• Point 3",
  "impact": "<pourquoi c'est important>",
  "hashtags": ["#Tag1", "#Tag2", "#Tag3"],
  "linkedin_draft": "<texte prêt à poster>",
  "reasoning": "<justification>"
}`;
```

### Tools Supplémentaires Phi

```javascript
const phiTools = [
  // ... mêmes outils que Qwen, plus:
  {
    type: "function",
    function: {
      name: "crawl_url",
      description: "Extrait le contenu complet d'une page web",
      parameters: {
        type: "object",
        properties: {
          url: { type: "string", description: "URL à crawler" }
        },
        required: ["url"]
      }
    }
  },
  {
    type: "function",
    function: {
      name: "get_articles",
      description: "Récupère les articles récents pour contexte",
      parameters: {
        type: "object",
        properties: {
          days: { type: "integer", description: "Nombre de jours (défaut: 7)" },
          source: { type: "string", description: "Filtrer par source" },
          limit: { type: "integer", description: "Max articles (défaut: 10)" }
        }
      }
    }
  },
  {
    type: "function",
    function: {
      name: "log_article",
      description: "Enregistre l'article validé dans la base",
      parameters: {
        type: "object",
        properties: {
          url: { type: "string" },
          title: { type: "string" },
          source: { type: "string" },
          source_type: { type: "string" },
          qwen_score: { type: "integer" },
          qwen_keywords: { type: "array", items: { type: "string" } },
          phi_validated: { type: "boolean" },
          phi_confidence: { type: "number" },
          summary_fr: { type: "string" },
          impact: { type: "string" },
          hashtags: { type: "array", items: { type: "string" } },
          linkedin_draft: { type: "string" }
        },
        required: ["url", "title", "source", "source_type"]
      }
    }
  }
];
```

## Workflow Distribution

```
┌─────────────────────────────────────────────────────────────────────┐
│                 WORKFLOW: 06_distribute.json                        │
└─────────────────────────────────────────────────────────────────────┘

┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│ Workflow │──►│  Check   │──►│ Telegram │──►│  Notion  │
│  Input   │   │ Criteria │   │ (if 9+)  │   │ Database │
└──────────┘   └──────────┘   └──────────┘   └──────────┘
```

### Telegram Node

```json
{
  "name": "Send Telegram Alert",
  "type": "n8n-nodes-base.telegram",
  "parameters": {
    "chatId": "={{ $env.TELEGRAM_CHAT_ID }}",
    "text": "=🔥 *Pépite trouvée!*\n\n*{{ $json.title }}*\n\n{{ $json.summary_fr }}\n\n🔗 {{ $json.url }}\n\n{{ $json.hashtags.join(' ') }}",
    "additionalFields": {
      "parse_mode": "Markdown"
    }
  },
  "credentials": {
    "telegramApi": "telegram_bot"
  }
}
```

### Notion Node

```json
{
  "name": "Add to Notion Database",
  "type": "n8n-nodes-base.notion",
  "parameters": {
    "resource": "databasePage",
    "operation": "create",
    "databaseId": "={{ $env.NOTION_DATABASE_ID }}",
    "properties": {
      "Titre": {
        "title": [{ "text": { "content": "={{ $json.title }}" } }]
      },
      "Source": {
        "select": { "name": "={{ $json.source }}" }
      },
      "Score": {
        "number": "={{ $json.qwen_score }}"
      },
      "Confiance": {
        "number": "={{ $json.phi_confidence }}"
      },
      "Résumé": {
        "rich_text": [{ "text": { "content": "={{ $json.summary_fr }}" } }]
      },
      "Impact": {
        "rich_text": [{ "text": { "content": "={{ $json.impact }}" } }]
      },
      "Hashtags": {
        "multi_select": "={{ $json.hashtags.map(h => ({name: h})) }}"
      },
      "LinkedIn Draft": {
        "rich_text": [{ "text": { "content": "={{ $json.linkedin_draft }}" } }]
      },
      "URL": {
        "url": "={{ $json.url }}"
      },
      "Date": {
        "date": { "start": "={{ new Date().toISOString() }}" }
      }
    }
  },
  "credentials": {
    "notionApi": "notion_api"
  }
}
```

## Gestion des Erreurs

### Retry Policy

```javascript
// Code Node: Retry Handler
const maxRetries = 3;
const currentRetry = $input.first().json.retry_count || 0;

if ($input.first().json.error && currentRetry < maxRetries) {
  // Attendre avant retry (backoff exponentiel)
  const delay = Math.pow(2, currentRetry) * 1000;

  return {
    json: {
      ...$input.first().json,
      retry_count: currentRetry + 1,
      retry_delay: delay
    }
  };
}

if (currentRetry >= maxRetries) {
  // Log l'échec et continuer
  console.error('Max retries reached for:', $input.first().json);
  return { json: { skip: true, reason: 'max_retries' } };
}

return $input.first();
```

### Error Notification

```json
{
  "name": "Error Notification",
  "type": "n8n-nodes-base.telegram",
  "parameters": {
    "chatId": "={{ $env.TELEGRAM_CHAT_ID }}",
    "text": "=⚠️ *Erreur Veille*\n\nWorkflow: {{ $workflow.name }}\nNode: {{ $node.name }}\nErreur: {{ $json.error.message }}"
  }
}
```

## Variables d'Environnement Requises

```bash
# Dans N8N
AURACORE_URL=http://auracore:3100
OLLAMA_URL=http://ollama:11434

# Credentials à configurer dans N8N UI
# - telegram_bot: Bot Token
# - notion_api: Integration Token
# - smtp: Email credentials
```

## Performance et Limites

| Métrique | Valeur | Notes |
|----------|--------|-------|
| Max iterations agent loop | 5 | Évite boucles infinies |
| Timeout Ollama | 120s | Qwen ~30s, Phi ~60s |
| Timeout AuraCore | 30s | Outils rapides |
| Batch size | 1 | Traitement séquentiel |
| Interval Cron | 2h | Ajustable |

## Debugging

### Activer les logs détaillés

```javascript
// Ajouter dans chaque Code Node critique
console.log('=== DEBUG ===');
console.log('Input:', JSON.stringify($input.all(), null, 2));
console.log('Output:', JSON.stringify(output, null, 2));
```

### Tester un workflow isolément

1. Aller dans le workflow
2. Cliquer sur "Execute Workflow"
3. Fournir des données de test via "Test Data"
4. Observer l'exécution node par node

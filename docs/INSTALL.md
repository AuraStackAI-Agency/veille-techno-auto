# Guide d'Installation - Veille Techno Auto

## Prérequis

### Matériel
- **CPU** : 8 vCPU minimum (12 recommandé)
- **RAM** : 16 GB minimum (32 GB recommandé)
- **Stockage** : 50 GB SSD minimum
- **OS** : Debian 11+ ou Ubuntu 22.04+

### Logiciels
- Docker & Docker Compose v2
- Git
- curl

## Architecture des Services

```
┌─────────────────────────────────────────────────────────────────────┐
│                         SERVICES DOCKER                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │   N8N    │  │  Ollama  │  │ AuraCore │  │ SearXNG  │           │
│  │  :5678   │  │  :11434  │  │  :3100   │  │  :8080   │           │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Installation Pas à Pas

### 1. Cloner le Repository

```bash
git clone https://github.com/AuraStackAI-Agency/veille-techno-auto.git
cd veille-techno-auto
```

### 2. Configuration Environnement

```bash
cp .env.example .env
```

Éditer `.env` avec vos paramètres :

```bash
# N8N
N8N_USER=admin
N8N_PASSWORD=<mot_de_passe_fort>
N8N_HOST=localhost
N8N_WEBHOOK_URL=https://votre-domaine.com

# Telegram (optionnel mais recommandé)
TELEGRAM_BOT_TOKEN=<votre_bot_token>
TELEGRAM_CHAT_ID=<votre_chat_id>

# Notion (optionnel)
NOTION_API_KEY=<votre_api_key>
NOTION_DATABASE_ID=<votre_database_id>

# Email (optionnel)
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=<votre_email>
SMTP_PASS=<votre_password>
EMAIL_TO=<destinataire>

# AuraCore
AURACORE_PORT=3100
AURACORE_DB_PATH=/data/auracore.db

# SearXNG
SEARXNG_URL=http://searxng:8080
```

### 3. Installer Ollama

```bash
# Installation Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Télécharger les modèles requis
ollama pull qwen2.5-coder:3b-instruct
ollama pull phi3:mini

# Vérifier l'installation
ollama list
```

### 4. Configurer le docker-compose

Le fichier `docker-compose.yml` complet :

```yaml
version: '3.8'

services:
  # N8N - Orchestration
  n8n:
    image: n8nio/n8n:latest
    container_name: n8n_veille
    restart: unless-stopped
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=${N8N_USER}
      - N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD}
      - N8N_HOST=${N8N_HOST}
      - N8N_PORT=5678
      - N8N_PROTOCOL=https
      - NODE_ENV=production
      - WEBHOOK_URL=${N8N_WEBHOOK_URL}
      - GENERIC_TIMEZONE=Europe/Paris
      - EXECUTIONS_DATA_PRUNE=true
      - EXECUTIONS_DATA_MAX_AGE=168
    volumes:
      - ./n8n_data:/home/node/.n8n
      - ./workflows:/workflows:ro
    networks:
      - veille_network
    depends_on:
      - auracore

  # AuraCore - MCP + HTTP API
  auracore:
    build:
      context: ./auracore
      dockerfile: Dockerfile
    container_name: auracore_veille
    restart: unless-stopped
    ports:
      - "3100:3100"
    environment:
      - AURACORE_PORT=3100
      - AURACORE_DB_PATH=/data/auracore.db
      - SEARXNG_URL=http://searxng:8080
      - JINA_READER_URL=https://r.jina.ai
      - LOG_LEVEL=info
    volumes:
      - ./auracore_data:/data
      - ./config:/config:ro
    networks:
      - veille_network
    depends_on:
      - searxng

  # SearXNG - Recherche Web Self-Hosted
  searxng:
    image: searxng/searxng:latest
    container_name: searxng_veille
    restart: unless-stopped
    ports:
      - "8080:8080"
    environment:
      - SEARXNG_BASE_URL=http://localhost:8080
    volumes:
      - ./searxng:/etc/searxng:rw
    networks:
      - veille_network
    cap_drop:
      - ALL
    cap_add:
      - CHOWN
      - SETGID
      - SETUID

networks:
  veille_network:
    driver: bridge

volumes:
  n8n_data:
  auracore_data:
  searxng:
```

### 5. Configurer SearXNG

Créer le fichier de configuration SearXNG :

```bash
mkdir -p searxng
```

Créer `searxng/settings.yml` :

```yaml
use_default_settings: true

server:
  secret_key: "<générer_une_clé_aléatoire>"
  limiter: false
  image_proxy: false

search:
  safe_search: 0
  autocomplete: ""
  default_lang: "en"
  formats:
    - html
    - json

engines:
  - name: google
    engine: google
    shortcut: g
    disabled: false

  - name: duckduckgo
    engine: duckduckgo
    shortcut: ddg
    disabled: false

  - name: bing
    engine: bing
    shortcut: bi
    disabled: false

  - name: github
    engine: github
    shortcut: gh
    disabled: false

  - name: stackoverflow
    engine: stackoverflow
    shortcut: st
    disabled: false

outgoing:
  request_timeout: 10.0
  max_request_timeout: 15.0
```

### 6. Démarrer les Services

```bash
# Démarrer tous les services
docker-compose up -d

# Vérifier que tout fonctionne
docker-compose ps

# Voir les logs
docker-compose logs -f
```

### 7. Initialiser AuraCore avec les Règles

Une fois AuraCore démarré, charger les règles de veille :

```bash
# Charger les règles depuis le fichier YAML
curl -X POST http://localhost:3100/api/veille/init \
  -H "Content-Type: application/json" \
  -d '{"config_path": "/config/veille_rules.yaml"}'

# Vérifier que les règles sont chargées
curl http://localhost:3100/api/veille/rules | jq
```

### 8. Configurer N8N

1. Accéder à N8N : http://localhost:5678
2. Se connecter avec les credentials définis dans `.env`
3. Aller dans **Settings → Credentials**
4. Configurer les credentials suivants :

#### Telegram Bot
- **Name** : `telegram_bot`
- **Access Token** : Votre bot token

#### Notion API
- **Name** : `notion_api`
- **Internal Integration Token** : Votre token Notion

#### SMTP (Email)
- **Name** : `smtp_email`
- **Host** : smtp.example.com
- **Port** : 587
- **User** : votre email
- **Password** : votre password

### 9. Importer les Workflows

1. Dans N8N, aller dans **Workflows**
2. Cliquer sur **Import from File**
3. Importer les fichiers du dossier `workflows/` :
   - `01_main_scheduler.json`
   - `02_ingest_rss.json`
   - `03_ingest_youtube.json`
   - `04_agent_qwen.json`
   - `05_agent_phi.json`
   - `06_distribute.json`
   - `07_newsletter_weekly.json`

### 10. Activer les Workflows

1. Ouvrir chaque workflow importé
2. Cliquer sur le toggle **Active** en haut à droite
3. Le workflow principal `01_main_scheduler` déclenchera les autres

## Vérification de l'Installation

### Test Ollama

```bash
# Test Qwen
curl http://localhost:11434/api/generate -d '{
  "model": "qwen2.5-coder:3b-instruct",
  "prompt": "Hello, respond with OK",
  "stream": false
}'

# Test Phi
curl http://localhost:11434/api/generate -d '{
  "model": "phi3:mini",
  "prompt": "Hello, respond with OK",
  "stream": false
}'
```

### Test AuraCore

```bash
# Health check
curl http://localhost:3100/health

# Test get rules
curl http://localhost:3100/api/veille/rules

# Test search
curl -X POST http://localhost:3100/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "ollama local llm", "num_results": 3}'

# Test crawl
curl -X POST http://localhost:3100/api/crawl \
  -H "Content-Type: application/json" \
  -d '{"url": "https://ollama.com"}'
```

### Test SearXNG

```bash
curl "http://localhost:8080/search?q=test&format=json" | jq '.results[:2]'
```

### Test N8N

1. Ouvrir le workflow `04_agent_qwen`
2. Cliquer sur **Execute Workflow**
3. Fournir un article test :
```json
{
  "article": {
    "title": "Ollama 0.5 Released with 50% Performance Improvement",
    "url": "https://example.com/ollama-0.5",
    "source": "test",
    "description": "New version brings major speed improvements"
  }
}
```
4. Observer l'exécution node par node

## Dépannage

### Ollama ne répond pas

```bash
# Vérifier le service
systemctl status ollama

# Redémarrer
systemctl restart ollama

# Vérifier les logs
journalctl -u ollama -f
```

### N8N ne peut pas atteindre AuraCore

```bash
# Vérifier le réseau Docker
docker network inspect veille_network

# Test de connectivité depuis N8N
docker exec -it n8n_veille curl http://auracore:3100/health
```

### SearXNG retourne des erreurs

```bash
# Vérifier les logs
docker logs searxng_veille

# Vérifier la configuration
docker exec -it searxng_veille cat /etc/searxng/settings.yml
```

### Manque de mémoire

```bash
# Vérifier l'utilisation
docker stats

# Si Ollama utilise trop de RAM, réduire le contexte
# Dans les appels Ollama, ajouter:
# "options": { "num_ctx": 2048 }
```

## Mise à Jour

```bash
# Arrêter les services
docker-compose down

# Mettre à jour le code
git pull origin main

# Mettre à jour les images
docker-compose pull

# Redémarrer
docker-compose up -d

# Mettre à jour les modèles Ollama
ollama pull qwen2.5-coder:3b-instruct
ollama pull phi3:mini
```

## Sauvegarde

```bash
# Sauvegarder les données
tar -czvf backup_veille_$(date +%Y%m%d).tar.gz \
  n8n_data/ \
  auracore_data/ \
  config/

# Restaurer
tar -xzvf backup_veille_YYYYMMDD.tar.gz
```

## Ressources

- [Documentation N8N](https://docs.n8n.io/)
- [Documentation Ollama](https://ollama.com/docs)
- [Documentation SearXNG](https://docs.searxng.org/)
- [VPS-debian Repository](https://github.com/AuraStackAI-Agency/VPS-debian)

# Installation Guide

## Prérequis
- Docker & Docker Compose
- Ollama avec `qwen2.5-coder:3b-instruct`
- Python 3.11+ (pour les scripts utilitaires)
- 4Go RAM minimum

## Installation

### 1. Cloner le Repository
```bash
git clone https://github.com/AuraStackAI-Agency/veille-techno-auto.git
cd veille-techno-auto
```

### 2. Configuration Environnement
```bash
cp .env.example .env
# Éditer .env avec vos paramètres
```

### 3. Installer Ollama et Qwen
```bash
# Sur le VPS
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen2.5-coder:3b-instruct
```

### 4. Installer Dépendances Python
```bash
python3 -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate sur Windows
pip install -r requirements.txt
```

### 5. Démarrer N8N
```bash
docker-compose up -d
```

### 6. Importer les Workflows
1. Accéder à N8N : http://localhost:5678
2. Aller dans Settings → Import
3. Importer `workflows/tech_watch_main.json`

### 7. Configuration des Credentials
Dans N8N, configurer :
- SMTP (pour l'envoi d'email)
- HTTP Request (Ollama endpoint)

### 8. Activer le Workflow
Dans N8N, activer le workflow "Tech Watch Main"

## Vérification
```bash
# Test Ollama
curl http://localhost:11434/api/tags

# Test YouTube Transcript
python scripts/test_youtube.py

# Logs N8N
docker logs -f n8n_techwatch
```

# Installation Guide

## Prérequis
- Instance N8N fonctionnelle
- Ollama avec `qwen2.5-coder:3b-instruct`
- Credentials SMTP configurés dans N8N

## Installation Rapide

### 1. Importer le Workflow
1. Accéder à N8N : https://n8n.aurastackai.com
2. Aller dans Settings → Import
3. Importer `workflows/tech_watch_main.json`

### 2. Configuration des Credentials
Dans N8N, configurer :
- **SMTP** : Pour l'envoi d'email (Gmail, Resend, etc.)

### 3. Vérifier Ollama
```bash
# Sur le VPS
curl http://localhost:11434/api/tags
# Doit retourner qwen2.5-coder:3b-instruct
```

### 4. Activer le Workflow
Dans N8N, activer le workflow "Veille Techno Auto - Newsletter IA"

## Vérification

### Test Manuel
1. Ouvrir le workflow dans N8N
2. Cliquer sur "Execute Workflow"
3. Vérifier que les RSS sont récupérés
4. Vérifier les résumés Qwen
5. Vérifier l'envoi email

### Logs
```bash
# Logs N8N
docker logs -f n8n-main-prod

# Logs Ollama
docker logs -f ollama
```

## Dépannage

### Erreur Ollama "connection refused"
- Vérifier que Ollama est accessible depuis le container N8N
- URL correcte : `http://ollama:11434` (réseau Docker)

### Pas d'articles filtrés
- Les sources RSS peuvent ne pas avoir de nouveaux articles
- Tester avec un filtre moins restrictif temporairement

### Email non reçu
- Vérifier les credentials SMTP
- Vérifier les logs du node "Send Email"

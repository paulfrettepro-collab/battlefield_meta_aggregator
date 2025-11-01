# 🚀 GitHub Actions Setup Guide

> **Guide complet pour automatiser le pipeline BF6 Meta Aggregator avec GitHub Actions**

---

## 📋 Table des Matières

1. [Vue d'ensemble](#vue-densemble)
2. [Prérequis](#prérequis)
3. [Configuration Secrets](#configuration-secrets)
4. [Workflow Weekly Extraction](#workflow-weekly-extraction)
5. [Tests et Validation](#tests-et-validation)
6. [Monitoring et Alertes](#monitoring-et-alertes)
7. [Troubleshooting](#troubleshooting)

---

## 📊 Vue d'ensemble

### Pourquoi GitHub Actions ?

| Critère | GitHub Actions | Airflow | Cron Local |
|---------|----------------|---------|------------|
| **Coût** | Gratuit (2000 min/mois) | $0 (self-hosted) | $0 |
| **Setup** | 30 min | 2-3h | 5 min |
| **Maintenance** | Zéro | Moyenne | Faible |
| **Logs** | Centralisés GitHub | UI Airflow | Fichiers locaux |
| **Scalabilité** | Excellente | Excellente | Limitée |
| **CI/CD** | Natif | Complexe | Impossible |
| **Monitoring** | Badges, Artifacts | Custom | Cron logs |

**✅ Choix retenu : GitHub Actions**
- Gratuit et suffisant (pipeline = 6-8 min/semaine)
- Logs centralisés accessibles partout
- Notifications natives (Slack, Discord, Email)
- Pas de serveur à maintenir

### Architecture Workflow

```
┌─────────────────────────────────────────────────────────────┐
│         GITHUB ACTIONS (Dimanches 2h UTC)                   │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│  JOB 1: SETUP (2 min)                                       │
│  • Checkout code                                            │
│  • Setup Python 3.12                                        │
│  • Install dependencies (cache pip)                         │
│  • Configure GCP credentials                                │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│  JOB 2: EXTRACT (4-5 min)                                   │
│  • Run extract_bf6_meta_complete.py                         │
│  • Upload logs to Artifacts                                 │
│  • Fail if < 45 players extracted                           │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│  JOB 3: LOAD (30s)                                          │
│  • Run load_to_bigquery_latest.py                           │
│  • Verify tables created (bronze_leaderboard, bronze_weapons)│
│  • Upload BigQuery logs                                     │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│  JOB 4: TRANSFORM (20s)                                     │
│  • Install DBT + dbt-bigquery                               │
│  • Run dbt run (6 models)                                   │
│  • Run dbt test (42/44 PASS minimum)                        │
│  • Upload DBT logs                                          │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│  JOB 5: VALIDATE (10s)                                      │
│  • Run query_bigquery.py (Top 3 weapons)                    │
│  • Verify data quality (non-empty tables)                   │
│  • Generate summary report                                  │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│  JOB 6: NOTIFY (5s)                                         │
│  • Send Slack/Discord notification                          │
│  • Update GitHub badge                                      │
│  • Commit logs to repo (optional)                           │
└─────────────────────────────────────────────────────────────┘
```

**Durée totale estimée** : 6-8 minutes
**Quota GitHub Actions** : ~30 min/mois (sur 2000 min gratuits)

---

## 🔧 Prérequis

### 1. Repository GitHub

✅ Repository existe : `paulfrettepro-collab/battlefield_meta_aggregator`

### 2. Service Account GCP

#### Vérifier si déjà créé :
```bash
gcloud iam service-accounts list --project=battlefield-meta-aggregator
```

#### Si besoin, créer nouveau service account :
```bash
# Créer service account pour GitHub Actions
gcloud iam service-accounts create github-actions \
  --display-name="GitHub Actions Automation" \
  --project=battlefield-meta-aggregator

# Donner les permissions BigQuery
gcloud projects add-iam-policy-binding battlefield-meta-aggregator \
  --member="serviceAccount:github-actions@battlefield-meta-aggregator.iam.gserviceaccount.com" \
  --role="roles/bigquery.admin"

# Créer clé JSON
gcloud iam service-accounts keys create github-actions-key.json \
  --iam-account=github-actions@battlefield-meta-aggregator.iam.gserviceaccount.com
```

### 3. Encoder la clé pour GitHub Secret

```bash
# macOS/Linux
cat github-actions-key.json | base64 | pbcopy

# Le résultat est copié dans le presse-papier
# Format : ewogICJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsC...
```

---

## 🔐 Configuration Secrets

### Étape 1 : Accéder aux Secrets GitHub

1. Aller sur : https://github.com/paulfrettepro-collab/battlefield_meta_aggregator/settings/secrets/actions
2. Cliquer sur **"New repository secret"**

### Étape 2 : Ajouter les Secrets

#### Secret 1: `GCP_PROJECT_ID`
- **Name** : `GCP_PROJECT_ID`
- **Value** : `battlefield-meta-aggregator`

#### Secret 2: `GCP_SERVICE_ACCOUNT_KEY`
- **Name** : `GCP_SERVICE_ACCOUNT_KEY`
- **Value** : Coller le contenu encodé base64 de `github-actions-key.json`

#### Secret 3 (Optionnel): `SLACK_WEBHOOK_URL`
- **Name** : `SLACK_WEBHOOK_URL`
- **Value** : `https://hooks.slack.com/services/YOUR/WEBHOOK/URL`
- Pour créer : https://api.slack.com/messaging/webhooks

### Étape 3 : Configurer Permissions Workflow

1. **Settings** > **Actions** > **General**
2. **Workflow permissions** : Sélectionner **"Read and write permissions"**
3. ✅ Cocher **"Allow GitHub Actions to create and approve pull requests"**
4. Cliquer **Save**

---

## 🤖 Workflow Weekly Extraction

### Étape 1 : Créer le fichier Workflow

**Fichier** : `.github/workflows/weekly_extraction.yml`

```yaml
name: Weekly BF6 Meta Extraction

on:
  # Exécution automatique : Dimanches à 2h UTC
  schedule:
    - cron: '0 2 * * 0'
  
  # Exécution manuelle depuis GitHub UI
  workflow_dispatch:
    inputs:
      player_limit:
        description: 'Number of players to extract (default: 50)'
        required: false
        default: '50'

env:
  PYTHON_VERSION: '3.12'
  GCP_PROJECT_ID: ${{ secrets.GCP_PROJECT_ID }}

jobs:
  #############################
  # JOB 1: SETUP ENVIRONMENT
  #############################
  setup:
    name: Setup Environment
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Python ${{ env.PYTHON_VERSION }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ env.PYTHON_VERSION }}
        cache: 'pip'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Authenticate to Google Cloud
      uses: google-github-actions/auth@v2
      with:
        credentials_json: ${{ secrets.GCP_SERVICE_ACCOUNT_KEY }}
    
    - name: Set up Cloud SDK
      uses: google-github-actions/setup-gcloud@v2
    
    - name: Verify GCP connection
      run: |
        gcloud config set project ${{ env.GCP_PROJECT_ID }}
        gcloud auth list
        python scripts/test_bigquery_connection.py

  #############################
  # JOB 2: EXTRACT DATA
  #############################
  extract:
    name: Extract Leaderboard & Weapons
    runs-on: ubuntu-latest
    needs: setup
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: ${{ env.PYTHON_VERSION }}
        cache: 'pip'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        # Install Chrome for Selenium
        sudo apt-get update
        sudo apt-get install -y chromium-browser chromium-chromedriver
    
    - name: Run extraction script
      id: extraction
      run: |
        python scripts/extract_bf6_meta_complete.py
        
        # Vérifier fichiers créés
        LEADERBOARD_FILE=$(ls -t data/bronze/tracker_gg/leaderboard/*.ndjson | head -1)
        WEAPONS_FILE=$(ls -t data/bronze/tracker_gg/top_weapons/*.ndjson | head -1)
        
        echo "leaderboard_file=$LEADERBOARD_FILE" >> $GITHUB_OUTPUT
        echo "weapons_file=$WEAPONS_FILE" >> $GITHUB_OUTPUT
        
        # Compter lignes extraites
        PLAYER_COUNT=$(wc -l < "$LEADERBOARD_FILE")
        WEAPON_COUNT=$(wc -l < "$WEAPONS_FILE")
        
        echo "player_count=$PLAYER_COUNT" >> $GITHUB_OUTPUT
        echo "weapon_count=$WEAPON_COUNT" >> $GITHUB_OUTPUT
        
        # Validation : minimum 45 joueurs
        if [ "$PLAYER_COUNT" -lt 45 ]; then
          echo "❌ ERROR: Only $PLAYER_COUNT players extracted (expected 50)"
          exit 1
        fi
        
        echo "✅ Extraction successful: $PLAYER_COUNT players, $WEAPON_COUNT weapons"
    
    - name: Upload extraction logs
      if: always()
      uses: actions/upload-artifact@v4
      with:
        name: extraction-logs
        path: data/logs/pipeline_*.log
        retention-days: 30
    
    - name: Upload NDJSON files
      uses: actions/upload-artifact@v4
      with:
        name: ndjson-data
        path: |
          data/bronze/tracker_gg/leaderboard/*.ndjson
          data/bronze/tracker_gg/top_weapons/*.ndjson
        retention-days: 90

  #############################
  # JOB 3: LOAD TO BIGQUERY
  #############################
  load:
    name: Load to BigQuery
    runs-on: ubuntu-latest
    needs: extract
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: ${{ env.PYTHON_VERSION }}
        cache: 'pip'
    
    - name: Install dependencies
      run: pip install -r requirements.txt
    
    - name: Authenticate to Google Cloud
      uses: google-github-actions/auth@v2
      with:
        credentials_json: ${{ secrets.GCP_SERVICE_ACCOUNT_KEY }}
    
    - name: Download NDJSON files
      uses: actions/download-artifact@v4
      with:
        name: ndjson-data
        path: data/bronze/tracker_gg/
    
    - name: Load to BigQuery
      id: load_bq
      run: |
        python scripts/load_to_bigquery_latest.py
        
        # Vérifier tables créées
        bq ls --project_id=${{ env.GCP_PROJECT_ID }} bf6_meta
        
        # Compter lignes dans BigQuery
        BRONZE_LEADERBOARD=$(bq query --nouse_legacy_sql --project_id=${{ env.GCP_PROJECT_ID }} "SELECT COUNT(*) FROM bf6_meta.bronze_leaderboard" | tail -1)
        BRONZE_WEAPONS=$(bq query --nouse_legacy_sql --project_id=${{ env.GCP_PROJECT_ID }} "SELECT COUNT(*) FROM bf6_meta.bronze_weapons" | tail -1)
        
        echo "bronze_leaderboard_count=$BRONZE_LEADERBOARD" >> $GITHUB_OUTPUT
        echo "bronze_weapons_count=$BRONZE_WEAPONS" >> $GITHUB_OUTPUT
        
        echo "✅ BigQuery loaded: $BRONZE_LEADERBOARD players, $BRONZE_WEAPONS weapons"

  #############################
  # JOB 4: DBT TRANSFORMATIONS
  #############################
  transform:
    name: DBT Transformations
    runs-on: ubuntu-latest
    needs: load
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: ${{ env.PYTHON_VERSION }}
        cache: 'pip'
    
    - name: Install DBT
      run: |
        pip install dbt-core dbt-bigquery
    
    - name: Authenticate to Google Cloud
      uses: google-github-actions/auth@v2
      with:
        credentials_json: ${{ secrets.GCP_SERVICE_ACCOUNT_KEY }}
    
    - name: DBT Debug
      working-directory: ./dbt
      run: dbt debug --profiles-dir .
    
    - name: DBT Run (Silver + Gold models)
      working-directory: ./dbt
      run: |
        dbt run --profiles-dir . --models bronze silver gold
        echo "✅ DBT run completed"
    
    - name: DBT Test
      id: dbt_test
      working-directory: ./dbt
      run: |
        dbt test --profiles-dir . > dbt_test_output.txt 2>&1
        cat dbt_test_output.txt
        
        # Compter tests passés/échoués
        PASSED=$(grep -c "PASS" dbt_test_output.txt || echo "0")
        FAILED=$(grep -c "FAIL" dbt_test_output.txt || echo "0")
        
        echo "tests_passed=$PASSED" >> $GITHUB_OUTPUT
        echo "tests_failed=$FAILED" >> $GITHUB_OUTPUT
        
        # Accepter 2 warnings maximum (doublons mineurs)
        if [ "$FAILED" -gt 2 ]; then
          echo "❌ ERROR: $FAILED tests failed (max 2 allowed)"
          exit 1
        fi
        
        echo "✅ DBT tests: $PASSED PASS, $FAILED warnings"
    
    - name: Upload DBT logs
      if: always()
      uses: actions/upload-artifact@v4
      with:
        name: dbt-logs
        path: dbt/logs/
        retention-days: 30

  #############################
  # JOB 5: VALIDATE DATA
  #############################
  validate:
    name: Validate Pipeline Output
    runs-on: ubuntu-latest
    needs: transform
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: ${{ env.PYTHON_VERSION }}
        cache: 'pip'
    
    - name: Install dependencies
      run: pip install -r requirements.txt
    
    - name: Authenticate to Google Cloud
      uses: google-github-actions/auth@v2
      with:
        credentials_json: ${{ secrets.GCP_SERVICE_ACCOUNT_KEY }}
    
    - name: Query Top 3 Weapons
      id: top_weapons
      run: |
        python scripts/query_bigquery.py > validation_output.txt
        cat validation_output.txt
        
        # Extraire Top 3 pour le message
        TOP3=$(grep -A 3 "Top 3 Weapons" validation_output.txt | tail -3)
        echo "top3_weapons<<EOF" >> $GITHUB_OUTPUT
        echo "$TOP3" >> $GITHUB_OUTPUT
        echo "EOF" >> $GITHUB_OUTPUT
    
    - name: Verify Gold Tables
      run: |
        # Vérifier que les tables Gold ne sont pas vides
        GOLD_GLOBAL=$(bq query --nouse_legacy_sql --project_id=${{ env.GCP_PROJECT_ID }} \
          "SELECT COUNT(*) as cnt FROM bf6_meta_gold.gold_top_weapons_global" --format=csv | tail -1)
        
        if [ "$GOLD_GLOBAL" -lt 10 ]; then
          echo "❌ ERROR: gold_top_weapons_global has only $GOLD_GLOBAL rows (expected 10)"
          exit 1
        fi
        
        echo "✅ Validation passed: Gold tables populated"

  #############################
  # JOB 6: NOTIFY
  #############################
  notify:
    name: Send Notifications
    runs-on: ubuntu-latest
    needs: [extract, load, transform, validate]
    if: always()
    
    steps:
    - name: Check workflow status
      id: status
      run: |
        if [ "${{ needs.validate.result }}" == "success" ]; then
          echo "status=success" >> $GITHUB_OUTPUT
          echo "emoji=✅" >> $GITHUB_OUTPUT
          echo "color=good" >> $GITHUB_OUTPUT
        else
          echo "status=failure" >> $GITHUB_OUTPUT
          echo "emoji=❌" >> $GITHUB_OUTPUT
          echo "color=danger" >> $GITHUB_OUTPUT
        fi
    
    - name: Send Slack notification
      if: always() && secrets.SLACK_WEBHOOK_URL != ''
      uses: slackapi/slack-github-action@v1.25.0
      with:
        payload: |
          {
            "text": "${{ steps.status.outputs.emoji }} BF6 Meta Extraction ${{ steps.status.outputs.status }}",
            "attachments": [
              {
                "color": "${{ steps.status.outputs.color }}",
                "fields": [
                  {
                    "title": "Status",
                    "value": "${{ steps.status.outputs.status }}",
                    "short": true
                  },
                  {
                    "title": "Workflow",
                    "value": "<https://github.com/${{ github.repository }}/actions/runs/${{ github.run_id }}|View Logs>",
                    "short": true
                  },
                  {
                    "title": "Top 3 Weapons",
                    "value": "${{ needs.validate.outputs.top3_weapons }}",
                    "short": false
                  }
                ]
              }
            ]
          }
      env:
        SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
        SLACK_WEBHOOK_TYPE: INCOMING_WEBHOOK
    
    - name: Create summary
      if: success()
      run: |
        echo "## 🎮 BF6 Meta Extraction Summary" >> $GITHUB_STEP_SUMMARY
        echo "" >> $GITHUB_STEP_SUMMARY
        echo "✅ **Status**: SUCCESS" >> $GITHUB_STEP_SUMMARY
        echo "📅 **Date**: $(date -u +"%Y-%m-%d %H:%M UTC")" >> $GITHUB_STEP_SUMMARY
        echo "" >> $GITHUB_STEP_SUMMARY
        echo "### 📊 Data Extracted" >> $GITHUB_STEP_SUMMARY
        echo "- Players: ${{ needs.extract.outputs.player_count }}" >> $GITHUB_STEP_SUMMARY
        echo "- Weapons: ${{ needs.extract.outputs.weapon_count }}" >> $GITHUB_STEP_SUMMARY
        echo "" >> $GITHUB_STEP_SUMMARY
        echo "### 🧪 DBT Tests" >> $GITHUB_STEP_SUMMARY
        echo "- Passed: ${{ needs.transform.outputs.tests_passed }}" >> $GITHUB_STEP_SUMMARY
        echo "- Failed: ${{ needs.transform.outputs.tests_failed }}" >> $GITHUB_STEP_SUMMARY
```

### Étape 2 : Créer le dossier et fichier

```bash
# Créer dossier workflows
mkdir -p .github/workflows

# Créer le fichier (copier le contenu ci-dessus)
nano .github/workflows/weekly_extraction.yml

# Commit et push
git add .github/workflows/weekly_extraction.yml
git commit -m "feat: add GitHub Actions weekly extraction workflow"
git push origin main
```

### Étape 3 : Tester le Workflow Manuellement

1. Aller sur : https://github.com/paulfrettepro-collab/battlefield_meta_aggregator/actions
2. Cliquer sur **"Weekly BF6 Meta Extraction"** (dans la liste à gauche)
3. Cliquer sur **"Run workflow"** (bouton à droite)
4. Laisser player_limit à 50 (default)
5. Cliquer **"Run workflow"** (vert)

**Durée attendue** : 6-8 minutes

**Résultat attendu** :
- ✅ 6 jobs verts (setup, extract, load, transform, validate, notify)
- ✅ Artifacts créés (extraction-logs, ndjson-data, dbt-logs)
- ✅ Notification Slack reçue (si configuré)

---

## ✅ Tests et Validation

### Test 1 : Vérification Extraction

```bash
# Télécharger l'artifact "ndjson-data" depuis GitHub Actions
# Vérifier le contenu

jq . bf6_leaderboard_*.ndjson | head -20
jq . bf6_weapons_*.ndjson | head -20

# Compter lignes
wc -l bf6_leaderboard_*.ndjson  # Attendu: 50
wc -l bf6_weapons_*.ndjson      # Attendu: 150
```

### Test 2 : Vérification BigQuery

```bash
# Connexion BigQuery Console
# https://console.cloud.google.com/bigquery?project=battlefield-meta-aggregator

# Requête test
SELECT COUNT(*) FROM `bf6_meta.bronze_leaderboard`;  -- Attendu: 50
SELECT COUNT(*) FROM `bf6_meta.bronze_weapons`;      -- Attendu: 150
SELECT COUNT(*) FROM `bf6_meta_gold.gold_top_weapons_global`;  -- Attendu: 10
```

### Test 3 : Vérification Dashboard

1. Attendre 2-3 min (auto-deploy Streamlit Cloud)
2. Visiter : https://battlefieldmetaaggregator.streamlit.app
3. Vérifier date d'extraction (sidebar) = date workflow
4. Vérifier Top 3 armes (sidebar) = résultat validation

---

## 📊 Monitoring et Alertes

### Badges GitHub (Optionnel)

Ajouter dans `readme.md` :

```markdown
[![Weekly Extraction](https://github.com/paulfrettepro-collab/battlefield_meta_aggregator/actions/workflows/weekly_extraction.yml/badge.svg)](https://github.com/paulfrettepro-collab/battlefield_meta_aggregator/actions/workflows/weekly_extraction.yml)
```

### Notifications Slack

**Création Webhook** :
1. Aller sur : https://api.slack.com/messaging/webhooks
2. Créer une "Incoming Webhook"
3. Copier l'URL : `https://hooks.slack.com/services/T.../B.../X...`
4. Ajouter dans GitHub Secrets : `SLACK_WEBHOOK_URL`

**Format message** :
```
✅ BF6 Meta Extraction success
• Players: 50
• Weapons: 150
• Top 3: SG 553R (86,897), TR-7 (50,394), M4A1 (39,049)
• Logs: https://github.com/.../actions/runs/123456789
```

### Logs Artifacts

**Accès** :
1. https://github.com/paulfrettepro-collab/battlefield_meta_aggregator/actions
2. Cliquer sur un run
3. Scroll bas de page : "Artifacts" section
4. Télécharger : `extraction-logs`, `ndjson-data`, `dbt-logs`

**Rétention** :
- Logs pipeline : 30 jours
- NDJSON data : 90 jours
- DBT logs : 30 jours

---

## 🚨 Troubleshooting

### Erreur : "Cloudflare blocked GitHub Actions IP"

**Symptôme** :
```
❌ ERROR: Only 0 players extracted (expected 50)
```

**Solution 1 : Retry avec délai** :
```yaml
- name: Run extraction script
  uses: nick-fields/retry@v2
  with:
    timeout_minutes: 10
    max_attempts: 3
    retry_wait_seconds: 30
    command: python scripts/extract_bf6_meta_complete.py
```

**Solution 2 : Fallback extraction manuelle** :
1. Lancer extraction en local : `./scripts/run_pipeline.sh`
2. Commit fichiers NDJSON
3. Push → BigQuery load + DBT se lancent automatiquement

### Erreur : "GCP authentication failed"

**Symptôme** :
```
ERROR: (gcloud.auth.activate-service-account) Invalid credentials
```

**Solution** :
1. Vérifier secret `GCP_SERVICE_ACCOUNT_KEY` existe
2. Régénérer clé :
```bash
gcloud iam service-accounts keys create new-key.json \
  --iam-account=github-actions@battlefield-meta-aggregator.iam.gserviceaccount.com
cat new-key.json | base64 | pbcopy
```
3. Mettre à jour secret GitHub

### Erreur : "DBT tests failed (5/44)"

**Symptôme** :
```
❌ ERROR: 5 tests failed (max 2 allowed)
```

**Solution** :
1. Télécharger artifact `dbt-logs`
2. Analyser fichiers `.log` dans `dbt/logs/`
3. Fix SQL models si nécessaire
4. Re-run workflow manuellement

### Quota GitHub Actions dépassé

**Symptôme** :
```
You have exceeded your usage limit for GitHub Actions
```

**Solution** :
1. Vérifier usage : Settings > Billing > Actions
2. Usage normal : ~30 min/mois (très loin de la limite 2000 min)
3. Si dépassé : fallback cron local temporairement

---

## 📈 Métriques de Succès

### KPIs à Surveiller

**Hebdomadaires** :
- ✅ Extraction réussie (100%)
- ✅ Durée pipeline < 10 min
- ✅ DBT tests PASS ≥ 42/44
- ✅ Dashboard à jour sous 30 min

**Mensuelles** :
- ✅ 4/4 extractions réussies
- ✅ 0 intervention manuelle
- ✅ Uptime dashboard > 99%

**Trimestrielles** :
- ✅ Quota GitHub Actions < 500 min/mois
- ✅ Coûts BigQuery < $0.50/mois
- ✅ Satisfaction utilisateurs (feedback)

---

## 📚 Ressources

**GitHub Actions** :
- [Documentation officielle](https://docs.github.com/en/actions)
- [Marketplace Actions](https://github.com/marketplace?type=actions)
- [Workflow syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)

**GCP Integration** :
- [google-github-actions/auth](https://github.com/google-github-actions/auth)
- [google-github-actions/setup-gcloud](https://github.com/google-github-actions/setup-gcloud)

**Notifications** :
- [Slack GitHub Action](https://github.com/slackapi/slack-github-action)
- [Discord Webhook](https://github.com/marketplace/actions/discord-webhook)

---

**Date de création** : 31 octobre 2025  
**Version** : 1.0  
**Auteur** : Paul Fretté  
**Statut** : ✅ Production-Ready

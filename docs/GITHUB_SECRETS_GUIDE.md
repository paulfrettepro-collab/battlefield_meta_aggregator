# 🔐 Guide Configuration GitHub Secrets

> **Instructions pour configurer les secrets GitHub Actions - Phase 7 Jour 2**

---

## ✅ Prérequis

- [x] Clé service account encodée : `/tmp/github-actions-key-base64.txt` (3237 bytes)
- [x] Workflow créé : `.github/workflows/weekly_extraction.yml`
- [x] Secrets GitHub configurés ✅ (4 nov 2025)
- [x] Permissions workflow configurées ✅ (4 nov 2025)
- [x] Premier test workflow lancé 🚀 (4 nov 2025 - EN COURS)

---

## 📝 Étape 1 : Copier la Clé Encodée

### Afficher le contenu
```bash
cat /tmp/github-actions-key-base64.txt
```

### Copier dans le presse-papier
```bash
cat /tmp/github-actions-key-base64.txt | pbcopy
```

**Résultat** : La clé base64 est maintenant dans votre clipboard ✅

---

## 🔑 Étape 2 : Configurer les Secrets GitHub

### 2.1 Accéder aux Secrets

1. Ouvrir dans le navigateur : https://github.com/paulfrettepro-collab/battlefield_meta_aggregator/settings/secrets/actions

2. Ou naviguer manuellement :
   - GitHub repo → **Settings** (en haut)
   - Sidebar gauche → **Secrets and variables** → **Actions**

### 2.2 Ajouter Secret #1 : GCP_PROJECT_ID

1. Cliquer **"New repository secret"** (bouton vert)
2. Remplir :
   - **Name** : `GCP_PROJECT_ID`
   - **Value** : `battlefield-meta-aggregator`
3. Cliquer **"Add secret"**

### 2.3 Ajouter Secret #2 : GCP_SERVICE_ACCOUNT_KEY

1. Cliquer **"New repository secret"**
2. Remplir :
   - **Name** : `GCP_SERVICE_ACCOUNT_KEY`
   - **Value** : Coller le contenu du clipboard (Cmd+V)
     - Devrait commencer par : `ewogICJ0eXBlIjogInNlcn...`
     - ~3200 caractères
3. Cliquer **"Add secret"**

### 2.4 (Optionnel) Ajouter Secret #3 : SLACK_WEBHOOK_URL

**Si tu veux des notifications Slack** :

1. Créer webhook : https://api.slack.com/messaging/webhooks
2. Copier l'URL (format : `https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX`)
3. GitHub :
   - **Name** : `SLACK_WEBHOOK_URL`
   - **Value** : Coller l'URL Slack

**Si non** : Passer cette étape (le workflow fonctionne sans)

### ✅ Vérification

Tu devrais voir 2 (ou 3) secrets listés :
- ✅ `GCP_PROJECT_ID`
- ✅ `GCP_SERVICE_ACCOUNT_KEY`
- ⏸️ `SLACK_WEBHOOK_URL` (optionnel)

---

## ⚙️ Étape 3 : Configurer Permissions Workflow

### 3.1 Accéder aux Settings Actions

1. Ouvrir : https://github.com/paulfrettepro-collab/battlefield_meta_aggregator/settings/actions

2. Ou naviguer :
   - Settings → **Actions** → **General**

### 3.2 Configurer Workflow Permissions

1. Scroll vers le bas jusqu'à **"Workflow permissions"**

2. Sélectionner : ✅ **"Read and write permissions"**
   - (décocher "Read repository contents" si coché)

3. Cocher : ✅ **"Allow GitHub Actions to create and approve pull requests"**

4. Cliquer **"Save"** (en bas)

### ✅ Vérification

- Permissions : **Read and write**
- PRs allowed : **Oui**

---

## 🧪 Étape 4 : Tester le Workflow Manuellement

### 4.1 Accéder à GitHub Actions

1. Ouvrir : https://github.com/paulfrettepro-collab/battlefield_meta_aggregator/actions

2. Dans la sidebar gauche, cliquer sur **"Weekly BF6 Meta Extraction"**

### 4.2 Lancer Manuellement

1. Cliquer **"Run workflow"** (bouton déroulant à droite)

2. Paramètres :
   - **Branch** : `main`
   - **player_limit** : `50` (ou laisser vide pour défaut)

3. Cliquer **"Run workflow"** (bouton vert)

### 4.3 Suivre l'Exécution

1. La page se rafraîchit → un nouveau run apparaît (statut jaune 🟡)

2. Cliquer sur le run pour voir les détails

3. Observer les 6 jobs :
   - ✅ **Setup Environment** (~2 min)
   - ✅ **Extract Leaderboard & Weapons** (~4-5 min)
   - ✅ **Load to BigQuery** (~30s)
   - ✅ **DBT Transformations** (~20s)
   - ✅ **Validate Pipeline Output** (~10s)
   - ✅ **Send Notifications** (~5s)

**Durée totale attendue** : 6-8 minutes

### 4.4 Vérifier Succès

**Si tous les jobs sont verts ✅** :
- Télécharger artifacts (extraction-logs, ndjson-data, dbt-logs)
- Vérifier BigQuery : https://console.cloud.google.com/bigquery?project=battlefield-meta-aggregator
- Vérifier Dashboard : https://battlefieldmetaaggregator.streamlit.app

**Si un job est rouge ❌** :
- Cliquer sur le job en erreur
- Lire les logs pour identifier le problème
- Vérifier la section Troubleshooting dans `docs/GITHUB_ACTIONS_SETUP.md`

---

## 🎯 Prochaines Étapes (Jour 3-4)

Une fois le test manuel réussi :

- [ ] Documenter résultats dans `RUNBOOK.md`
- [ ] Ajouter badge workflow dans README
- [ ] Configurer notifications Slack (si souhaité)
- [ ] Attendre dimanche prochain pour vérifier cron automatique
- [ ] Créer workflow dashboard auto-sync (Phase 7.2)

---

## 📌 Liens Rapides

| Ressource | URL |
|-----------|-----|
| **GitHub Secrets** | https://github.com/paulfrettepro-collab/battlefield_meta_aggregator/settings/secrets/actions |
| **Workflow Permissions** | https://github.com/paulfrettepro-collab/battlefield_meta_aggregator/settings/actions |
| **Actions Runs** | https://github.com/paulfrettepro-collab/battlefield_meta_aggregator/actions |
| **BigQuery Console** | https://console.cloud.google.com/bigquery?project=battlefield-meta-aggregator |
| **Dashboard** | https://battlefieldmetaaggregator.streamlit.app |

---

**Date** : 4 novembre 2025  
**Phase** : 7 - GitHub Actions CI/CD  
**Statut** : Jour 2/5 - Workflow créé, secrets à configurer

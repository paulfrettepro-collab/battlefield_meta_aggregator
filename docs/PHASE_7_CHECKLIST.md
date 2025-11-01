# ✅ Phase 7 Deployment Checklist

> **Checklist complète pour déployer GitHub Actions CI/CD**

---

## 📋 Semaine 1 : Core Automation (Must-Have)

### ✅ Jour 1 : Préparation GCP & Secrets (COMPLÉTÉ - 1 nov 2025)

- [x] **1.1 Vérifier Service Account GCP**
  ```bash
  gcloud iam service-accounts list --project=battlefield-meta-aggregator
  ```
  - [x] Service account existe : `bigquery-admin-service-882@battlefield-meta-aggregator.iam.gserviceaccount.com`
  - [x] Fichier `config/bigquery-key.json` présent (2.4 KB)
  - [x] Project ID : `battlefield-meta-aggregator`
  - [x] Configuration `.env` validée

**✅ RÉSULTAT** : Service account déjà configuré, prêt pour GitHub Actions !

---

### 🎯 Jour 2 : Configuration GitHub Actions (2 nov 2025 - 1-2h)

- [ ] **1.1 Vérifier Service Account GCP**
  ```bash
  gcloud iam service-accounts list --project=battlefield-meta-aggregator
  ```
  - [ ] Service account existe : `github-actions@battlefield-meta-aggregator.iam.gserviceaccount.com`
  - [ ] OU créer nouveau (commandes dans `GITHUB_ACTIONS_SETUP.md`)

### 🎯 Jour 2 : Configuration GitHub Actions (2 nov 2025 - 1-2h)

- [ ] **2.1 Encoder clé JSON pour GitHub Actions**
  ```bash
  cat config/bigquery-key.json | base64 | pbcopy
  ```
  - [ ] Clé encodée et copiée dans clipboard

- [ ] **2.2 Configurer GitHub Secrets**
  - [ ] Aller sur : https://github.com/paulfrettepro-collab/battlefield_meta_aggregator/settings/secrets/actions
  - [ ] Créer secret `GCP_PROJECT_ID` = `battlefield-meta-aggregator`
  - [ ] Créer secret `GCP_SERVICE_ACCOUNT_KEY` = <contenu base64>
  - [ ] (Optionnel) Créer secret `SLACK_WEBHOOK_URL` = <webhook Slack>

- [ ] **2.3 Configurer Permissions Workflow**
  - [ ] Settings > Actions > General
  - [ ] Workflow permissions : "Read and write"
  - [ ] ✅ Allow GitHub Actions to create PRs

---

### Jour 2-3 : Création Workflow Weekly Extraction (3-4h)

- [ ] **2.1 Créer dossier workflows**
  ```bash
  mkdir -p .github/workflows
  ```

- [ ] **2.2 Créer fichier `weekly_extraction.yml`**
  - [ ] Copier template depuis `docs/GITHUB_ACTIONS_SETUP.md`
  - [ ] Ajuster paramètres si nécessaire (cron, player_limit, etc.)

- [ ] **2.3 Commit et push workflow**
  ```bash
  git add .github/workflows/weekly_extraction.yml
  git commit -m "feat: add GitHub Actions weekly extraction workflow"
  git push origin main
  ```

- [ ] **2.4 Test manuel du workflow**
  - [ ] Aller sur : https://github.com/paulfrettepro-collab/battlefield_meta_aggregator/actions
  - [ ] Cliquer "Weekly BF6 Meta Extraction"
  - [ ] Cliquer "Run workflow" (bouton vert)
  - [ ] Attendre 6-8 min
  - [ ] ✅ Vérifier tous les jobs sont verts

- [ ] **2.5 Vérifier résultats**
  - [ ] Télécharger artifacts (extraction-logs, ndjson-data, dbt-logs)
  - [ ] Vérifier BigQuery tables (bronze_leaderboard, bronze_weapons)
  - [ ] Vérifier BigQuery tables Gold (gold_top_weapons_global)
  - [ ] Vérifier Dashboard Streamlit (date + top 3 armes)

- [ ] **2.6 Debugging si échec**
  - [ ] Lire logs du job échoué
  - [ ] Corriger problème (voir Troubleshooting dans GITHUB_ACTIONS_SETUP.md)
  - [ ] Re-run workflow

---

### Jour 4 : Documentation & Monitoring (2h)

- [ ] **3.1 Ajouter badge workflow dans README**
  ```markdown
  [![Weekly Extraction](https://github.com/paulfrettepro-collab/battlefield_meta_aggregator/actions/workflows/weekly_extraction.yml/badge.svg)](https://github.com/paulfrettepro-collab/battlefield_meta_aggregator/actions/workflows/weekly_extraction.yml)
  ```

- [ ] **3.2 Tester notification Slack (si configuré)**
  - [ ] Re-run workflow manuellement
  - [ ] Vérifier message Slack reçu
  - [ ] Ajuster format message si nécessaire

- [ ] **3.3 Documenter procédure run manuel**
  - [ ] Créer `docs/RUNBOOK.md` (instructions opérationnelles)
  - [ ] Section 1 : Extraction manuelle (GitHub UI)
  - [ ] Section 2 : Résolution erreurs courantes
  - [ ] Section 3 : Rollback procédure

- [ ] **3.4 Mise à jour README principal**
  - [ ] ✅ Marquer Phase 7 comme "EN COURS"
  - [ ] ✅ Ajouter lien vers `GITHUB_ACTIONS_SETUP.md`
  - [ ] ✅ Mettre à jour section "Orchestration"

---

### Jour 5 : Validation Semaine 1 (1h)

- [ ] **4.1 Tests finaux**
  - [ ] Lancer workflow manuel une dernière fois
  - [ ] ✅ Durée < 10 min
  - [ ] ✅ Tous jobs verts
  - [ ] ✅ Dashboard mis à jour

- [ ] **4.2 Vérifier schedule automatique**
  - [ ] Attendre dimanche prochain 2h UTC
  - [ ] OU modifier cron pour test rapide : `*/15 * * * *` (toutes les 15 min)
  - [ ] Vérifier workflow se lance automatiquement
  - [ ] Restaurer cron original : `0 2 * * 0`

- [ ] **4.3 Commit final**
  ```bash
  git add .
  git commit -m "docs: finalize Phase 7.1 - GitHub Actions weekly extraction"
  git push origin main
  ```

---

## 🎯 Semaine 2 : Advanced Features (Nice-to-Have)

### Jour 6-7 : Tests CI/CD sur PR (3-4h)

- [ ] **5.1 Créer workflow CI tests**
  - [ ] Fichier : `.github/workflows/ci_tests.yml`
  - [ ] Trigger : `push`, `pull_request` (branches main, dev)
  - [ ] Jobs :
    - [ ] Linting (flake8, black)
    - [ ] Type checking (mypy)
    - [ ] Unit tests (pytest)
    - [ ] DBT dry-run tests

- [ ] **5.2 Configurer pytest**
  - [ ] Créer `tests/test_extraction.py`
  - [ ] Tests : validation NDJSON, format data, error handling
  - [ ] Run local : `pytest tests/ -v`

- [ ] **5.3 Ajouter coverage**
  - [ ] Install : `pip install pytest-cov`
  - [ ] Run : `pytest --cov=scripts --cov-report=html`
  - [ ] Ajouter badge coverage dans README

---

### Jour 8 : Dashboard Auto-Sync (1h)

- [ ] **6.1 Créer workflow deploy dashboard**
  - [ ] Fichier : `.github/workflows/deploy_dashboard.yml`
  - [ ] Trigger : Succès de `weekly_extraction.yml`
  - [ ] Action : Sync `dashboard/` → root `pages/` + `streamlit_app.py`

- [ ] **6.2 Tester sync automatique**
  - [ ] Modifier fichier dans `dashboard/pages/`
  - [ ] Lancer workflow weekly_extraction
  - [ ] Vérifier auto-sync vers root
  - [ ] Vérifier Streamlit Cloud redéploie

---

### Jour 9 : Monitoring Avancé (2h)

- [ ] **7.1 Configurer Slack notifications complètes**
  - [ ] Message success avec métriques détaillées
  - [ ] Message failure avec logs direct
  - [ ] Weekly summary (4 extractions du mois)

- [ ] **7.2 Créer healthcheck endpoint**
  - [ ] Script : `scripts/healthcheck.py`
  - [ ] Vérifications :
    - [ ] BigQuery accessible
    - [ ] DBT tests pass
    - [ ] Streamlit up (ping URL)
  - [ ] Workflow : `.github/workflows/healthcheck.yml`
  - [ ] Schedule : `0 */6 * * *` (toutes les 6h)

- [ ] **7.3 Dashboard GitHub**
  - [ ] Créer `README.md` section "Status"
  - [ ] Badges :
    - [ ] Weekly Extraction (workflow status)
    - [ ] CI Tests (workflow status)
    - [ ] Uptime Streamlit (uptimerobot.com)
    - [ ] Last extraction date (custom)

---

## 📊 Validation Finale

### Critères de Succès Phase 7

**Must-Have (Semaine 1)** :
- [ ] ✅ Workflow weekly_extraction.yml créé et fonctionnel
- [ ] ✅ Extraction automatique dimanches 2h UTC
- [ ] ✅ Tous jobs passent (6/6 verts)
- [ ] ✅ Dashboard Streamlit mis à jour automatiquement
- [ ] ✅ Logs accessibles (GitHub Artifacts)
- [ ] ✅ Notifications configurées (Slack/Discord OU GitHub)
- [ ] ✅ Documentation complète (GITHUB_ACTIONS_SETUP.md + RUNBOOK.md)

**Nice-to-Have (Semaine 2)** :
- [ ] ✅ Tests CI/CD sur PR
- [ ] ✅ Coverage > 70%
- [ ] ✅ Dashboard auto-sync
- [ ] ✅ Healthcheck automatique
- [ ] ✅ Monitoring proactif

### Métriques à Surveiller (4 semaines)

**Hebdomadaires** :
- [ ] Extraction réussie : 4/4 (100%)
- [ ] Durée pipeline : < 10 min
- [ ] DBT tests PASS : ≥ 42/44
- [ ] Dashboard à jour : < 30 min

**Mensuelles** :
- [ ] 0 intervention manuelle
- [ ] Uptime dashboard : > 99%
- [ ] Quota GitHub Actions : < 500 min/mois
- [ ] Coûts BigQuery : < $0.50/mois

---

## 🚨 Rollback Plan

Si problème majeur Phase 7 :

### Option 1 : Désactiver workflow temporairement
```yaml
# Dans .github/workflows/weekly_extraction.yml
on:
  # Commenter schedule
  # schedule:
  #   - cron: '0 2 * * 0'
  
  # Garder workflow_dispatch pour run manuel
  workflow_dispatch:
```

### Option 2 : Fallback Cron local
```bash
# Activer cron local (voir scripts/crontab_setup.txt)
crontab -e
# Ajouter ligne :
0 2 * * 0 /path/to/battlefield_meta_aggregator/scripts/run_pipeline.sh
```

### Option 3 : Extraction manuelle
```bash
cd /Users/paulfrette/Github_pro_folder/battlefield_meta_aggregator
./scripts/run_pipeline.sh
```

---

## 📚 Ressources

**Documentation** :
- ✅ `docs/GITHUB_ACTIONS_SETUP.md` - Guide complet setup
- ✅ `docs/RUNBOOK.md` - Procédures opérationnelles (à créer)
- ✅ `AUTOMATION_GUIDE.md` - Comparaison solutions automation

**Workflows créés** :
- ✅ `.github/workflows/weekly_extraction.yml` - Extraction hebdomadaire
- ⏳ `.github/workflows/ci_tests.yml` - Tests CI/CD (optionnel)
- ⏳ `.github/workflows/deploy_dashboard.yml` - Auto-sync dashboard (optionnel)
- ⏳ `.github/workflows/healthcheck.yml` - Monitoring (optionnel)

**Support** :
- GitHub Actions Docs : https://docs.github.com/en/actions
- GCP GitHub Actions : https://github.com/google-github-actions
- Slack Notifications : https://github.com/slackapi/slack-github-action

---

**Date de création** : 31 octobre 2025  
**Version** : 1.0  
**Statut** : 🚀 **PRÊT POUR DÉPLOIEMENT**

---

## ✅ Prochaine Action

**🎯 COMMENCER ICI** :

1. **Lire** : `docs/GITHUB_ACTIONS_SETUP.md` (guide complet 30 min)
2. **Jour 1** : Configurer GCP + GitHub Secrets (1-2h)
3. **Jour 2-3** : Créer workflow + test manuel (3-4h)
4. **Jour 4** : Documentation + monitoring (2h)
5. **Jour 5** : Validation finale (1h)

**Total Semaine 1** : 7-9 heures réparties sur 5 jours

**🎉 Résultat** : Pipeline 100% automatisé, zéro maintenance, logs centralisés !

# 📚 Documentation - Index

Bienvenue dans la documentation du projet **Battlefield Meta Aggregator** !

---

## 🚀 Démarrage Rapide

**Nouveau sur le projet ?** Commencez ici :

1. 📖 [README principal](../readme.md) - Vue d'ensemble du projet
2. 🔐 [SECURITY.md](../SECURITY.md) - Politique de sécurité (credentials)
3. ⚙️ [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md) - Configuration CI/CD

---

## 📂 Documentation par Thème

### 🏗️ Architecture & Concepts

| Document | Description |
|----------|-------------|
| [GUIDE_TECHNIQUE_COMPLET.md](GUIDE_TECHNIQUE_COMPLET.md) | Architecture complète du pipeline ELT |
| [DBT_BIGQUERY_EXPLAINED.md](DBT_BIGQUERY_EXPLAINED.md) | Modèles DBT et transformations SQL |
| [SOLUTION_ANALYSIS.md](SOLUTION_ANALYSIS.md) | Analyse comparative des solutions (Xvfb vs Playwright) |

### ⚙️ Configuration & Setup

| Document | Description |
|----------|-------------|
| [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md) | Configurer GitHub Actions workflow |
| [GITHUB_SECRETS_GUIDE.md](GITHUB_SECRETS_GUIDE.md) | Encoder et configurer secrets GCP |
| [BIGQUERY_GUIDE.md](BIGQUERY_GUIDE.md) | Setup BigQuery, tables, permissions |
| [STREAMLIT_CLOUD_DEPLOY.md](STREAMLIT_CLOUD_DEPLOY.md) | Déployer dashboard sur Streamlit Cloud |

### 🐛 Debugging & Troubleshooting

| Document | Description |
|----------|-------------|
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Guide de dépannage (5 scénarios communs) |
| [CLOUDFLARE_BYPASS.md](CLOUDFLARE_BYPASS.md) | Contourner détection Cloudflare (Xvfb, Playwright) |
| [STREAMLIT_TROUBLESHOOTING.md](STREAMLIT_TROUBLESHOOTING.md) | Résoudre erreurs dashboard |

### 📊 Dashboard & Visualisation

| Document | Description |
|----------|-------------|
| [STREAMLIT_GUIDE.md](STREAMLIT_GUIDE.md) | Créer et structurer pages Streamlit |
| [STREAMLIT_CLOUD_DEPLOY.md](STREAMLIT_CLOUD_DEPLOY.md) | Déploiement production |

### 🛠️ Développement

| Document | Description |
|----------|-------------|
| [CLI_GIT_GUIDE.md](CLI_GIT_GUIDE.md) | Commandes Git + symboles VS Code |
| [CODEBASE_CLEANUP.md](CODEBASE_CLEANUP.md) | Refactoring et nettoyage code |
| [Prompt_engineering.md](Prompt_engineering.md) | Collaboration avec IA (historique prompts) |

### 📋 Gestion de Projet

| Document | Description |
|----------|-------------|
| [PHASE_7_CHECKLIST.md](PHASE_7_CHECKLIST.md) | Checklist Phase 7 (GitHub Actions CI/CD) |
| [../MONITORING_V4.md](../MONITORING_V4.md) | Monitoring workflow v4 (Xvfb) |
| [../ACTION_PLAN.md](../ACTION_PLAN.md) | Plan d'action validation v4 |

---

## 🔍 Trouver la Bonne Documentation

**Je veux...**

- **Comprendre l'architecture** → [GUIDE_TECHNIQUE_COMPLET.md](GUIDE_TECHNIQUE_COMPLET.md)
- **Configurer GitHub Actions** → [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md)
- **Résoudre une erreur** → [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Déployer le dashboard** → [STREAMLIT_CLOUD_DEPLOY.md](STREAMLIT_CLOUD_DEPLOY.md)
- **Comprendre DBT** → [DBT_BIGQUERY_EXPLAINED.md](DBT_BIGQUERY_EXPLAINED.md)
- **Bypass Cloudflare** → [CLOUDFLARE_BYPASS.md](CLOUDFLARE_BYPASS.md)
- **Sécuriser credentials** → [../SECURITY.md](../SECURITY.md)

---

## 📝 Fichiers Racine du Projet

| Fichier | Description |
|---------|-------------|
| [readme.md](../readme.md) | Documentation principale (architecture, démarrage rapide) |
| [SECURITY.md](../SECURITY.md) | Politique sécurité (gitignore, secrets) |
| [MONITORING_V4.md](../MONITORING_V4.md) | Checklist monitoring workflow v4 |
| [ACTION_PLAN.md](../ACTION_PLAN.md) | Plan validation extraction v4 |
| [NEXT_STEPS.md](../NEXT_STEPS.md) | Roadmap futures améliorations |
| [PROJECT_OVERVIEW.md](../PROJECT_OVERVIEW.md) | Vision et objectifs du projet |

---

## 🏷️ Tags par Technologie

- **Python** : [GUIDE_TECHNIQUE_COMPLET.md](GUIDE_TECHNIQUE_COMPLET.md), [CLOUDFLARE_BYPASS.md](CLOUDFLARE_BYPASS.md)
- **BigQuery** : [BIGQUERY_GUIDE.md](BIGQUERY_GUIDE.md), [DBT_BIGQUERY_EXPLAINED.md](DBT_BIGQUERY_EXPLAINED.md)
- **DBT** : [DBT_BIGQUERY_EXPLAINED.md](DBT_BIGQUERY_EXPLAINED.md)
- **GitHub Actions** : [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md), [GITHUB_SECRETS_GUIDE.md](GITHUB_SECRETS_GUIDE.md)
- **Streamlit** : [STREAMLIT_GUIDE.md](STREAMLIT_GUIDE.md), [STREAMLIT_CLOUD_DEPLOY.md](STREAMLIT_CLOUD_DEPLOY.md)
- **Selenium** : [CLOUDFLARE_BYPASS.md](CLOUDFLARE_BYPASS.md), [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## 🤝 Contribuer à la Documentation

La documentation suit ces principes :
- ✅ **Clarté** : Exemples concrets, pas de jargon inutile
- ✅ **Actualité** : Mise à jour avec chaque changement majeur
- ✅ **Accessibilité** : Screenshots, code snippets, liens internes
- ✅ **Pragmatisme** : Solutions réelles testées en production

**Ajouter un document** : Créer le fichier dans `docs/`, puis l'ajouter à cet index avec description.

---

**Dernière mise à jour** : 8 novembre 2025  
**Version pipeline** : v4 (Xvfb + Cleanup BigQuery)

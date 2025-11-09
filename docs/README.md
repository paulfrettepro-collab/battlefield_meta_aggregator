# 📚 Documentation - Index

Bienvenue dans la documentation du projet **Battlefield Meta Aggregator** !

---

## 🚀 Démarrage Rapide

**Nouveau sur le projet ?** Commencez ici :

1. 📖 [README principal](../readme.md) - Vue d'ensemble du projet
2. 🔐 [SECURITY.md](../SECURITY.md) - Politique de sécurité (credentials)
3. ⚙️ [Configuration GitHub Actions](setup/GITHUB_ACTIONS_SETUP.md) - Setup CI/CD

---

## 📂 Structure Documentation

```
docs/
├── README.md                    # ← Vous êtes ici (index)
├── guides/                      # 📖 Guides techniques détaillés
├── setup/                       # ⚙️ Configuration et installation
├── troubleshooting/             # 🐛 Résolution de problèmes
├── dev/                         # 🛠️ Développement et Git
├── project/                     # 📋 Gestion de projet
└── archive/                     # 📦 Fichiers historiques
```

---

## 📖 Guides Techniques

**Architecture et concepts fondamentaux**

| Document | Description |
|----------|-------------|
| [guides/GUIDE_TECHNIQUE_COMPLET.md](guides/GUIDE_TECHNIQUE_COMPLET.md) | Architecture complète du pipeline ELT |
| [guides/DBT_BIGQUERY_EXPLAINED.md](guides/DBT_BIGQUERY_EXPLAINED.md) | Modèles DBT et transformations SQL |
| [guides/BIGQUERY_GUIDE.md](guides/BIGQUERY_GUIDE.md) | Setup BigQuery, tables, permissions |
| [guides/STREAMLIT_GUIDE.md](guides/STREAMLIT_GUIDE.md) | Créer et structurer pages Streamlit |
| [guides/STREAMLIT_CLOUD_DEPLOY.md](guides/STREAMLIT_CLOUD_DEPLOY.md) | Déployer dashboard sur Streamlit Cloud |

---

## ⚙️ Configuration & Setup

**Installation et configuration initiale**

| Document | Description |
|----------|-------------|
| [setup/GITHUB_ACTIONS_SETUP.md](setup/GITHUB_ACTIONS_SETUP.md) | Configurer GitHub Actions workflow |
| [setup/GITHUB_SECRETS_GUIDE.md](setup/GITHUB_SECRETS_GUIDE.md) | Encoder et configurer secrets GCP |

---

## 🐛 Troubleshooting

**Résolution de problèmes et debugging**

| Document | Description |
|----------|-------------|
| [troubleshooting/TROUBLESHOOTING.md](troubleshooting/TROUBLESHOOTING.md) | Guide de dépannage (5 scénarios communs) |
| [troubleshooting/CLOUDFLARE_BYPASS.md](troubleshooting/CLOUDFLARE_BYPASS.md) | Contourner détection Cloudflare (Xvfb, Playwright) |
| [troubleshooting/STREAMLIT_TROUBLESHOOTING.md](troubleshooting/STREAMLIT_TROUBLESHOOTING.md) | Résoudre erreurs dashboard |
| [troubleshooting/SOLUTION_ANALYSIS.md](troubleshooting/SOLUTION_ANALYSIS.md) | Analyse comparative solutions (Xvfb vs Playwright) |

---

## 🛠️ Développement

**Outils et workflows de développement**

| Document | Description |
|----------|-------------|
| [dev/CLI_GIT_GUIDE.md](dev/CLI_GIT_GUIDE.md) | Commandes Git + symboles VS Code |
| [dev/CODEBASE_CLEANUP.md](dev/CODEBASE_CLEANUP.md) | Refactoring et nettoyage code |
| [dev/PHASE_7_CHECKLIST.md](dev/PHASE_7_CHECKLIST.md) | Checklist Phase 7 (GitHub Actions CI/CD) |
| [dev/Prompt_engineering.md](dev/Prompt_engineering.md) | Collaboration avec IA (historique prompts) |

---

## 📋 Gestion de Projet

**Suivi et planification**

| Document | Description |
|----------|-------------|
| [project/PROJECT_OVERVIEW.md](project/PROJECT_OVERVIEW.md) | Vision et objectifs du projet |
| [project/MONITORING_V4.md](project/MONITORING_V4.md) | Monitoring workflow v4 (Xvfb) |
| [project/ACTION_PLAN.md](project/ACTION_PLAN.md) | Plan d'action validation v4 |
| [project/SESSION_SUMMARY.md](project/SESSION_SUMMARY.md) | Récapitulatif des sessions de travail |
| [project/CHECKLIST_REPO_PUBLIC.md](project/CHECKLIST_REPO_PUBLIC.md) | Checklist préparation repo public |

---

## � Archive

**Fichiers historiques (référence uniquement)**

| Document | Description |
|----------|-------------|
| [archive/readme_OLD.md](archive/readme_OLD.md) | Ancienne version README |
| [archive/DASHBOARD_UPDATE_31OCT2025.md](archive/DASHBOARD_UPDATE_31OCT2025.md) | Mise à jour dashboard 31 oct |
| [archive/AUTOMATION_GUIDE.md](archive/AUTOMATION_GUIDE.md) | Guide automatisation (remplacé par GitHub Actions) |
| [archive/Idées.md](archive/Idées.md) | Brainstorming initial |

---

## 🔍 Navigation Rapide

**Je veux...**

| Besoin | Document |
|--------|----------|
| 📖 **Comprendre l'architecture** | [guides/GUIDE_TECHNIQUE_COMPLET.md](guides/GUIDE_TECHNIQUE_COMPLET.md) |
| ⚙️ **Configurer GitHub Actions** | [setup/GITHUB_ACTIONS_SETUP.md](setup/GITHUB_ACTIONS_SETUP.md) |
| 🐛 **Résoudre une erreur** | [troubleshooting/TROUBLESHOOTING.md](troubleshooting/TROUBLESHOOTING.md) |
| 🚀 **Déployer le dashboard** | [guides/STREAMLIT_CLOUD_DEPLOY.md](guides/STREAMLIT_CLOUD_DEPLOY.md) |
| 📊 **Comprendre DBT** | [guides/DBT_BIGQUERY_EXPLAINED.md](guides/DBT_BIGQUERY_EXPLAINED.md) |
| 🛡️ **Bypass Cloudflare** | [troubleshooting/CLOUDFLARE_BYPASS.md](troubleshooting/CLOUDFLARE_BYPASS.md) |
| 🔐 **Sécuriser credentials** | [../SECURITY.md](../SECURITY.md) |
| � **Suivre le projet** | [project/MONITORING_V4.md](project/MONITORING_V4.md) |

---

## 🏷️ Tags par Technologie

- **Python** : [guides/GUIDE_TECHNIQUE_COMPLET.md](guides/GUIDE_TECHNIQUE_COMPLET.md), [troubleshooting/CLOUDFLARE_BYPASS.md](troubleshooting/CLOUDFLARE_BYPASS.md)
- **BigQuery** : [guides/BIGQUERY_GUIDE.md](guides/BIGQUERY_GUIDE.md), [guides/DBT_BIGQUERY_EXPLAINED.md](guides/DBT_BIGQUERY_EXPLAINED.md)
- **DBT** : [guides/DBT_BIGQUERY_EXPLAINED.md](guides/DBT_BIGQUERY_EXPLAINED.md)
- **GitHub Actions** : [setup/GITHUB_ACTIONS_SETUP.md](setup/GITHUB_ACTIONS_SETUP.md), [setup/GITHUB_SECRETS_GUIDE.md](setup/GITHUB_SECRETS_GUIDE.md)
- **Streamlit** : [guides/STREAMLIT_GUIDE.md](guides/STREAMLIT_GUIDE.md), [guides/STREAMLIT_CLOUD_DEPLOY.md](guides/STREAMLIT_CLOUD_DEPLOY.md)
- **Selenium** : [troubleshooting/CLOUDFLARE_BYPASS.md](troubleshooting/CLOUDFLARE_BYPASS.md), [troubleshooting/TROUBLESHOOTING.md](troubleshooting/TROUBLESHOOTING.md)

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

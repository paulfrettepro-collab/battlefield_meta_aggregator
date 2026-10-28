# 📁 Structure du Projet - Guide Complet

**Dernière mise à jour** : 8 novembre 2025

---

## 🎯 Vue d'Ensemble

```
battlefield_meta_aggregator/
│
├── 📄 readme.md                    # Documentation principale (NE PAS DÉPLACER)
├── 🔐 SECURITY.md                  # Politique sécurité (standard GitHub)
│
├── 📂 docs/                        # 📚 TOUTE LA DOCUMENTATION
│   ├── README.md                   # Index complet (COMMENCER ICI)
│   │
│   ├── 📖 guides/                  # Guides techniques détaillés
│   │   ├── GUIDE_TECHNIQUE_COMPLET.md
│   │   ├── DBT_BIGQUERY_EXPLAINED.md
│   │   ├── BIGQUERY_GUIDE.md
│   │   ├── STREAMLIT_GUIDE.md
│   │   └── STREAMLIT_CLOUD_DEPLOY.md
│   │
│   ├── ⚙️ setup/                   # Configuration initiale
│   │   ├── GITHUB_ACTIONS_SETUP.md
│   │   └── GITHUB_SECRETS_GUIDE.md
│   │
│   ├── 🐛 troubleshooting/         # Résolution de problèmes
│   │   ├── TROUBLESHOOTING.md
│   │   ├── CLOUDFLARE_BYPASS.md
│   │   ├── STREAMLIT_TROUBLESHOOTING.md
│   │   └── SOLUTION_ANALYSIS.md
│   │
│   ├── 🛠️ dev/                     # Développement
│   │   ├── CLI_GIT_GUIDE.md
│   │   ├── CODEBASE_CLEANUP.md
│   │   ├── PHASE_7_CHECKLIST.md
│   │   └── Prompt_engineering.md
│   │
│   ├── 📋 project/                 # Gestion de projet
│   │   ├── PROJECT_OVERVIEW.md
│   │   ├── MONITORING_V4.md
│   │   ├── ACTION_PLAN.md
│   │   ├── SESSION_SUMMARY.md
│   │   └── CHECKLIST_REPO_PUBLIC.md
│   │
│   └── 📦 archive/                 # Fichiers historiques
│       ├── readme_OLD.md
│       ├── DASHBOARD_UPDATE_31OCT2025.md
│       ├── AUTOMATION_GUIDE.md
│       └── Idées.md
│
├── 📂 scripts/                     # 🐍 Scripts Python
│   ├── README.md
│   ├── extract_bf6_meta_complete.py
│   ├── load_to_bigquery_latest.py
│   ├── query_bigquery.py
│   └── validate_*.sh/py
│
├── 📂 dbt/                         # 📊 Transformations DBT
│   ├── README.md
│   ├── README_PROFILES.md
│   ├── models/
│   │   ├── bronze/
│   │   ├── silver/
│   │   └── gold/
│   └── dbt_project.yml
│
├── 📂 dashboard/                   # 🎨 Streamlit Dashboard
│   ├── README.md
│   ├── pages/
│   └── utils/
│
├── 📂 data/                        # 💾 Données locales
│   ├── README.md
│   ├── bronze/
│   │   └── tracker_gg/
│   │       ├── leaderboard/
│   │       └── weapons/
│   └── exploration/
│       └── README.md
│
├── 📂 .github/workflows/           # ⚙️ GitHub Actions
│   └── weekly_extraction.yml
│
└── 📂 config/                      # 🔐 Configuration (gitignored)
    └── bigquery-key.json          # ❌ NE JAMAIS COMMIT
```

---

## 🗺️ Navigation Rapide

### 📚 Documentation

**Point d'entrée** : [`docs/README.md`](docs/README.md) (index complet)

| Dossier | Contenu | Usage |
|---------|---------|-------|
| `docs/guides/` | Guides techniques | Apprendre l'architecture, DBT, BigQuery |
| `docs/setup/` | Configuration | Installer et configurer le projet |
| `docs/troubleshooting/` | Dépannage | Résoudre erreurs et bugs |
| `docs/dev/` | Développement | Git, refactoring, collaboration IA |
| `docs/project/` | Gestion projet | Suivi, monitoring, checklists |
| `docs/archive/` | Historique | Référence anciennes versions |

### 🐍 Code Python

| Dossier | Contenu | Usage |
|---------|---------|-------|
| `scripts/` | Scripts Python | Extraction, load BigQuery, validation |
| `dbt/models/` | Transformations SQL | Bronze → Silver → Gold |
| `dashboard/` | App Streamlit | Visualisation données |

### 💾 Données

| Dossier | Contenu | Gitignored |
|---------|---------|------------|
| `data/bronze/` | Fichiers NDJSON | ❌ Non (prod) |
| `data/exploration/` | HTML debug | ✅ Oui |
| `config/` | Credentials GCP | ✅ Oui |

---

## 🚀 Parcours Utilisateur

### 🆕 **Nouveau sur le projet ?**

1. Lire [`readme.md`](readme.md) (vue d'ensemble)
2. Consulter [`SECURITY.md`](SECURITY.md) (setup credentials)
3. Suivre [`docs/setup/GITHUB_ACTIONS_SETUP.md`](docs/setup/GITHUB_ACTIONS_SETUP.md)

### 🔧 **Développeur ?**

1. Lire [`docs/guides/GUIDE_TECHNIQUE_COMPLET.md`](docs/guides/GUIDE_TECHNIQUE_COMPLET.md)
2. Consulter [`scripts/README.md`](scripts/README.md)
3. Utiliser [`docs/dev/CLI_GIT_GUIDE.md`](docs/dev/CLI_GIT_GUIDE.md)

### 🐛 **Problème rencontré ?**

1. Chercher dans [`docs/troubleshooting/TROUBLESHOOTING.md`](docs/troubleshooting/TROUBLESHOOTING.md)
2. Si Cloudflare → [`docs/troubleshooting/CLOUDFLARE_BYPASS.md`](docs/troubleshooting/CLOUDFLARE_BYPASS.md)
3. Si Streamlit → [`docs/troubleshooting/STREAMLIT_TROUBLESHOOTING.md`](docs/troubleshooting/STREAMLIT_TROUBLESHOOTING.md)

### 📊 **Analyste/Data ?**

1. Lire [`docs/guides/DBT_BIGQUERY_EXPLAINED.md`](docs/guides/DBT_BIGQUERY_EXPLAINED.md)
2. Consulter [`dbt/README.md`](dbt/README.md)
3. Explorer [`dashboard/README.md`](dashboard/README.md)

---

## 📝 Règles de Documentation

### ✅ À Faire

- **Créer nouveau doc** → Ajouter dans bon dossier (`docs/guides/`, `docs/setup/`, etc.)
- **Mettre à jour index** → Éditer `docs/README.md`
- **Liens relatifs** → Utiliser chemins relatifs (ex: `../guides/GUIDE.md`)
- **Standards GitHub** → Garder `readme.md` et `SECURITY.md` à la racine

### ❌ À Éviter

- **Ne pas** déplacer `readme.md` (GitHub le cherche à la racine)
- **Ne pas** créer fichiers `.md` à la racine (sauf standards GitHub)
- **Ne pas** dupliquer documentation (1 source de vérité)
- **Ne pas** oublier d'updater `docs/README.md` (index)

---

## 🔄 Historique Réorganisation

### Version 1 (Avant 8 nov 2025)

```
battlefield_meta_aggregator/
├── readme.md
├── ACTION_PLAN.md              ❌ Racine encombrée
├── MONITORING_V4.md            ❌ Racine encombrée
├── PROJECT_OVERVIEW.md         ❌ Racine encombrée
├── SESSION_SUMMARY.md          ❌ Racine encombrée
├── CHECKLIST_REPO_PUBLIC.md    ❌ Racine encombrée
├── Idées.md                    ❌ Racine encombrée
├── readme_OLD.md               ❌ Racine encombrée
└── docs/
    ├── GUIDE_TECHNIQUE_COMPLET.md   ❌ Plat, pas organisé
    ├── DBT_BIGQUERY_EXPLAINED.md    ❌ Plat, pas organisé
    ├── TROUBLESHOOTING.md           ❌ Plat, pas organisé
    └── ... (15 fichiers en vrac)    ❌ Difficile à naviguer
```

### Version 2 (Après 8 nov 2025) ✅

```
battlefield_meta_aggregator/
├── readme.md                   ✅ Racine propre
├── SECURITY.md                 ✅ Standard GitHub
└── docs/
    ├── README.md               ✅ Index complet
    ├── guides/                 ✅ Organisé par thème
    ├── setup/                  ✅ Organisé par thème
    ├── troubleshooting/        ✅ Organisé par thème
    ├── dev/                    ✅ Organisé par thème
    ├── project/                ✅ Organisé par thème
    └── archive/                ✅ Historique séparé
```

**Bénéfices** :
- 📂 Structure claire et hiérarchique
- 🔍 Navigation facilitée (index complet)
- 🧹 Racine propre (2 fichiers au lieu de 10)
- 📚 Documentation organisée par thème
- 🎯 Onboarding simplifié

---

## 📊 Statistiques

- **Total fichiers .md** : 33
- **Racine** : 2 (readme.md, SECURITY.md)
- **Documentation** : 25 (dans `docs/`)
- **Code** : 6 (README.md dans `scripts/`, `dbt/`, `dashboard/`, `data/`)
- **Dossiers docs/** : 6 (guides, setup, troubleshooting, dev, project, archive)

---

## 🤝 Contribution

Pour ajouter de la documentation :

1. **Identifier le type** : Guide ? Setup ? Troubleshooting ?
2. **Créer dans bon dossier** : `docs/guides/`, `docs/setup/`, etc.
3. **Mettre à jour index** : Éditer `docs/README.md`
4. **Commit avec message clair** : `docs(guides): Add XYZ guide`

---

**Structure validée** ✅  
**Navigation optimisée** ✅  
**Prêt pour repo public** ✅

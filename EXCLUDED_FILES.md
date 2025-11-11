# 🔒 Fichiers Exclus du Repository Public

Ce document liste les fichiers qui ont été **retirés du repository GitHub public** pour des raisons de sécurité et de confidentialité, mais qui restent **disponibles localement** pour le développement.

## 📋 Fichiers Exclus

### 1. **SECURITY.md** *(Exclu le 11 novembre 2025)*
**Raison** : Contient des instructions détaillées sur la configuration des credentials BigQuery (chemins, noms de fichiers, structure des secrets).

**Contenu** : 
- Instructions de création de `config/bigquery-key.json`
- Configuration des variables d'environnement `.env`
- Setup GitHub Actions secrets
- Configuration Streamlit Cloud secrets

**Disponibilité** :
- ✅ Disponible localement pour les contributeurs
- ❌ Non visible sur GitHub public
- 📝 Les informations générales de sécurité sont documentées dans `readme.md`

---

### 2. **PROJECT_STRUCTURE.md** *(Exclu le 11 novembre 2025)*
**Raison** : Documentation interne détaillée de la structure du projet.

**Contenu** :
- Arborescence complète du projet avec descriptions
- Organisation interne des fichiers
- Conventions de nommage privées

**Disponibilité** :
- ✅ Disponible localement pour les contributeurs
- ❌ Non visible sur GitHub public
- 📝 La structure publique est décrite dans `readme.md`

---

### 3. **artifacts_git_hub_action/** *(Dossier exclu)*
**Raison** : Artifacts téléchargés depuis GitHub Actions à des fins de debug local uniquement.

**Contenu** :
- Fichiers NDJSON de tests
- Logs de debug
- Snapshots HTML temporaires

---

## 🔄 Impact sur le Workflow GitHub Actions

### ✅ Aucun Impact
L'exclusion de ces fichiers **n'affecte PAS** le workflow GitHub Actions car :

1. **SECURITY.md** : Documentation uniquement, non utilisée par le code
2. **PROJECT_STRUCTURE.md** : Documentation uniquement
3. **artifacts_git_hub_action/** : Fichiers locaux, non utilisés par CI/CD

### ✅ Workflow Reste Fonctionnel
Le workflow utilise :
- **Secrets GitHub** : `GCP_SERVICE_ACCOUNT_KEY`, `GCP_PROJECT_ID`
- **Scripts** : `scripts/*.py`
- **DBT Models** : `dbt/models/**/*.sql`

Tous ces fichiers **restent versionnés**.

---

## 📝 Pour les Contributeurs

Si vous avez besoin de ces fichiers :
- **Contact** : paul.frette.pro@gmail.com
- **Documentation** : Voir `readme.md` (section Setup)

---

*Créé le 11 novembre 2025*

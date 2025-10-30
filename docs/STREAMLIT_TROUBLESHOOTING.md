# 🔧 Streamlit Dashboard - Troubleshooting Guide

**Date**: 30 octobre 2025  
**Status**: Dashboard structure working, data loading needs secrets configuration

---

## 🐛 Problème : Les données ne s'affichent pas sur Streamlit Cloud

### Symptômes
- ✅ La structure du site s'affiche (header, sidebar, sections)
- ✅ La navigation entre les pages fonctionne
- ❌ Les graphiques et tableaux sont vides
- ❌ Erreur BigQuery dans les logs

### Cause Racine
Les secrets BigQuery (`gcp_service_account`) ne sont pas configurés dans Streamlit Cloud.

---

## ✅ Solution : Configuration des Secrets Streamlit Cloud

### Étape 1 : Accéder aux paramètres de l'app

1. Aller sur https://share.streamlit.io
2. Se connecter avec votre compte GitHub
3. Trouver l'app **battlefieldmetaaggregator**
4. Cliquer sur **⚙️ Settings** (roue dentée)

### Étape 2 : Ajouter les secrets

1. Dans le menu latéral, cliquer sur **Secrets**
2. Coller le contenu suivant dans l'éditeur :

```toml
# .streamlit/secrets.toml pour Streamlit Cloud

[gcp_service_account]
type = "service_account"
project_id = "battlefield-meta-aggregator"
private_key_id = "VOTRE_PRIVATE_KEY_ID"
private_key = "-----BEGIN PRIVATE KEY-----\nVOTRE_PRIVATE_KEY\n-----END PRIVATE KEY-----\n"
client_email = "streamlit-dashboard@battlefield-meta-aggregator.iam.gserviceaccount.com"
client_id = "VOTRE_CLIENT_ID"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/streamlit-dashboard%40battlefield-meta-aggregator.iam.gserviceaccount.com"
universe_domain = "googleapis.com"
```

### Étape 3 : Obtenir les valeurs réelles

Les valeurs se trouvent dans votre fichier local `config/bigquery-key.json` :

```bash
# Sur votre Mac, afficher le fichier
cat ~/Github_pro_folder/battlefield_meta_aggregator/config/bigquery-key.json
```

**🔐 IMPORTANT** :
- Copier **EXACTEMENT** la valeur de `private_key` (avec les `\n`)
- Ne **JAMAIS** committer ce fichier dans Git
- Les secrets Streamlit Cloud sont chiffrés et sécurisés

### Étape 4 : Sauvegarder et Redéployer

1. Cliquer sur **Save** en bas de la page
2. L'app va automatiquement redémarrer
3. Attendre 1-2 minutes pour le redéploiement
4. Rafraîchir la page : https://battlefieldmetaaggregator.streamlit.app

---

## 🧪 Tests de Validation

### Test 1 : Page Principale (Home)
- ✅ **Métriques** : Total Kills, Total Players, Avg Accuracy s'affichent
- ✅ **Graphique** : Bar chart TOP 10 armes visible
- ✅ **Cartes armes** : Top 3 weapon profiles avec stats

**Données attendues (30 oct 2025)** :
- Total Kills (Top 10) : ~220,000+
- Total Players : ~50
- Avg Accuracy : ~23%
- Top 3 : SG 553R, TR-7, M4A1

### Test 2 : Page All Weapons
- ✅ **Tableau** : 20 armes affichées avec kills, accuracy, players
- ✅ **Recherche** : Filtrage par nom d'arme fonctionne
- ✅ **Export** : Bouton CSV download disponible

### Test 3 : Page All Players
- ✅ **Tableau** : 50 joueurs affichés avec rank, kills, location
- ✅ **Recherche** : Filtrage par handle fonctionne
- ✅ **Cartes** : Top 10 players avec armes principales

---

## 🐞 Autres Problèmes Possibles

### Problème : "403 Permission Denied"

**Cause** : Le service account n'a pas les permissions BigQuery

**Solution** :
```bash
# Dans Google Cloud Console
# IAM & Admin > Service Accounts > streamlit-dashboard@...
# Vérifier les rôles :
✅ BigQuery Data Viewer
✅ BigQuery Job User
```

### Problème : "Module not found: google.cloud.bigquery"

**Cause** : Dépendance manquante dans `requirements.txt`

**Solution** :
```bash
# Vérifier requirements.txt contient :
google-cloud-bigquery==3.28.0
pandas-gbq==0.24.0
```

### Problème : Cache ne se rafraîchit pas

**Cause** : TTL de 600s (10 min) actif

**Solution** :
1. Cliquer sur **🔄 Refresh Data** dans la sidebar
2. Ou attendre 10 minutes
3. Ou redémarrer l'app dans Streamlit Cloud

### Problème : "No data available"

**Cause** : Tables BigQuery vides ou dataset incorrect

**Solution** :
```bash
# Vérifier que DBT a bien créé les tables Gold
cd ~/Github_pro_folder/battlefield_meta_aggregator/dbt
dbt run
dbt test

# Vérifier les tables existent
python3 test_dashboard_queries.py
```

---

## 📊 Architecture BigQuery

### Datasets utilisés

```
battlefield-meta-aggregator
├── bf6_meta (Bronze - Raw data)
│   ├── bronze_leaderboard (50 rows)
│   └── bronze_weapons (150 rows)
├── bf6_meta_silver (Cleaned data)
│   ├── silver_players (50 rows)
│   ├── silver_weapons (150 rows)
│   └── silver_player_weapons (150 rows)
└── bf6_meta_gold (Analytics-ready)
    ├── gold_top_weapons_global (10 rows) ← Dashboard Home
    ├── gold_top_weapons_by_type (20 rows) ← All Weapons page
    └── gold_player_rankings (50 rows) ← All Players page
```

### Requêtes du Dashboard

**Page Home** (`dashboard/app.py`) :
```sql
SELECT global_rank, weapon_name, total_kills, nb_players_using, avg_accuracy
FROM `battlefield-meta-aggregator.bf6_meta_gold.gold_top_weapons_global`
ORDER BY global_rank
```

**Page All Weapons** (`pages/1_🔫_All_Weapons.py`) :
```sql
SELECT weapon_rank, weapon_name, total_kills, nb_players_using, avg_accuracy
FROM `battlefield-meta-aggregator.bf6_meta_gold.gold_top_weapons_by_type`
ORDER BY weapon_rank
```

**Page All Players** (`pages/2_👥_All_Players.py`) :
```sql
SELECT player_handle, player_rank, player_total_kills, main_weapon, player_location
FROM `battlefield-meta-aggregator.bf6_meta_gold.gold_player_rankings`
ORDER BY player_rank
```

---

## 🔍 Debugging en Local

### Test rapide des requêtes

```bash
cd ~/Github_pro_folder/battlefield_meta_aggregator
python3 test_dashboard_queries.py
```

**Résultat attendu** :
```
✅ SUCCESS: gold_top_weapons_global - 10 rows
✅ SUCCESS: gold_top_weapons_by_type - 20 rows
✅ SUCCESS: gold_player_rankings - 50 rows
✅ SUCCESS: Last extraction = 2025-10-30 16:03:08
```

### Lancer le dashboard localement

```bash
# Option 1: Port par défaut (8501)
streamlit run dashboard/app.py

# Option 2: Port personnalisé
streamlit run dashboard/app.py --server.port 8502
```

**URL** : http://localhost:8501

### Logs du dashboard

```bash
# Streamlit affiche les erreurs dans le terminal
# Chercher :
❌ "No data available"
❌ "BigQuery credentials not found"
❌ "403 Permission Denied"
```

---

## 📝 Checklist de Déploiement

Avant de déployer sur Streamlit Cloud, vérifier :

- [ ] `config/bigquery-key.json` existe en local (ne PAS committer)
- [ ] `requirements.txt` contient `google-cloud-bigquery` et `pandas-gbq`
- [ ] `dashboard/utils/bigquery.py` détecte correctement `st.secrets`
- [ ] DBT a bien créé les 3 tables Gold (`dbt run` succès)
- [ ] Test local fonctionne (`streamlit run dashboard/app.py`)
- [ ] GitHub repo est à jour (`git push origin main`)
- [ ] Streamlit Cloud secrets sont configurés (`.streamlit/secrets.toml`)
- [ ] URL publique fonctionne (https://battlefieldmetaaggregator.streamlit.app)

---

## 🆘 Support

### Logs Streamlit Cloud

1. Aller sur https://share.streamlit.io
2. Cliquer sur l'app **battlefieldmetaaggregator**
3. Cliquer sur **⚙️ Settings** > **Logs**
4. Chercher les erreurs `ERROR` ou `CRITICAL`

### Fichiers à vérifier

```bash
# Configuration BigQuery
dashboard/utils/bigquery.py    # Gestion des credentials

# Requêtes principales
dashboard/app.py                # Page Home
dashboard/pages/1_🔫_All_Weapons.py
dashboard/pages/2_👥_All_Players.py

# Dépendances
requirements.txt                # Packages Python

# Secrets (local uniquement, ne PAS committer)
config/bigquery-key.json        # Credentials Google Cloud
.streamlit/secrets.toml         # Secrets locaux (template)
```

### Contacts

- **GitHub Issues** : https://github.com/paulfrettepro-collab/battlefield_meta_aggregator/issues
- **Documentation** : `docs/STREAMLIT_CLOUD_DEPLOY.md`
- **Projet** : `readme.md`

---

**Dernière mise à jour** : 30 octobre 2025  
**Version Dashboard** : 1.2.0 (Gold Layer Integration)

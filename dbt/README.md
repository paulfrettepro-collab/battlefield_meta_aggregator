# 🏗️ DBT Transformations - Battlefield Meta Aggregator

## 📊 Vue d'ensemble

Ce dossier contient tous les modèles DBT (Data Build Tool) pour transformer les données brutes (Bronze) en données analytiques (Silver → Gold).

## 🎯 Objectif MVP

**Top 3 des armes qui font le plus de kills** parmi les joueurs du top 100 leaderboard.

---

## 📁 Structure des Modèles

```
dbt/
├── dbt_project.yml          # Configuration du projet DBT
├── profiles.yml              # Configuration de connexion BigQuery
└── models/
    ├── bronze/
    │   └── sources.yml       # Définition des tables sources
    ├── silver/               # Données nettoyées et normalisées
    │   ├── silver_players.sql
    │   ├── silver_weapons.sql
    │   ├── silver_player_weapons.sql
    │   └── schema.yml
    └── gold/                 # Données analytiques (dashboard-ready)
        ├── gold_top_weapons_global.sql
        ├── gold_top_weapons_by_type.sql
        ├── gold_player_rankings.sql
        └── schema.yml
```

---

## 🥉 BRONZE - Tables Sources

### `bf6_leaderboard_raw`
- **97 joueurs** (rangs 4-100)
- Colonnes : handle, player_id, rank, kills, extraction_date, url_source

### `bf6_top_weapons_raw`
- **288 armes** (97 joueurs × 3 armes)
- Colonnes : handle, weapon_name, weapon_rank, kills, weapon_type, accuracy, headshot_pct, time_played, damage, extraction_date

---

## 🥈 SILVER - Données Nettoyées

### `silver_players` (1 row)
**Transformations** :
- ✅ TRIM des espaces sur handle et player_id
- ✅ CAST explicite des types numériques
- ✅ Extraction de la date pour partitionnement
- ✅ Flag de validation (is_valid_data)
- ✅ Catégorisation en tiers (Top 10/50/100)
- ✅ Filtre sur la dernière extraction uniquement

### `silver_weapons` (3 rows)
**Transformations** :
- ✅ UPPER et TRIM sur les noms d'armes (normalisation)
- ✅ Conversion accuracy et headshot_pct : `"23.5%"` → `0.235`
- ✅ COALESCE sur weapon_type (gérer les nulls)
- ✅ Flag de validation par arme (is_valid_weapon)
- ✅ Filtre sur extraction réussie uniquement

### `silver_player_weapons` (3 rows)
**Transformations** :
- ✅ INNER JOIN entre joueurs et armes
- ✅ Calcul du % de kills par arme vs total joueur
- ✅ Préservation des métadonnées de fraîcheur

---

## 🥇 GOLD - Analytics & Dashboard

### `gold_top_weapons_global` (3 rows) - **MVP**
**Top 3 armes qui font le PLUS de kills (toutes catégories)**

Colonnes :
- `global_rank` : Rang global (1-3)
- `weapon_name` : Nom de l'arme
- `weapon_type` : Type (SMG, AR, LMG, etc.)
- `total_kills` : Total de kills avec cette arme
- `nb_players_using` : Nombre de joueurs utilisant cette arme
- `avg_kills_per_player` : Moyenne de kills par joueur
- `avg_accuracy` : Précision moyenne (0.0-1.0)
- `avg_headshot_pct` : % headshots moyen (0.0-1.0)
- `total_damage_dealt` : Total de dégâts infligés

**Résultat actuel** :
```
1. B36A4 (ASSAULT RIFLES) - 2,800 kills (1 joueur)
2. SCW-10 (SMG) - 2,670 kills (1 joueur)
3. L110 (LMG) - 1,840 kills (1 joueur)
```

### `gold_top_weapons_by_type` (3 rows)
**Top 3 armes par TYPE** (SMG, AR, LMG, etc.)

### `gold_player_rankings` (1 row)
**Classement des joueurs avec leurs armes préférées**
- Arme principale, secondaire, tertiaire
- Stats moyennes (accuracy, headshot%)

---

## 🧪 Tests de Qualité

**47 tests exécutés** - **100% réussite** ✅

### Tests génériques
- ✅ `not_null` : Aucune valeur NULL dans les colonnes critiques
- ✅ `unique` : Unicité des identifiants (player_handle, player_id)
- ✅ `relationships` : Intégrité référentielle (weapons → players)
- ✅ `accepted_values` : Valeurs valides (tiers, types d'armes)

### Tables créées dans BigQuery
```
bf6_meta.bf6_leaderboard_raw           (Bronze)
bf6_meta.bf6_top_weapons_raw           (Bronze)
bf6_meta_silver.silver_players         (Silver)
bf6_meta_silver.silver_weapons         (Silver)
bf6_meta_silver.silver_player_weapons  (Silver)
bf6_meta_gold.gold_top_weapons_global  (Gold) ← MVP
bf6_meta_gold.gold_top_weapons_by_type (Gold)
bf6_meta_gold.gold_player_rankings     (Gold)
```

---

## 🚀 Commandes DBT

### Setup initial
```bash
cd dbt
source ../.venv/bin/activate
pip install dbt-bigquery
```

### Vérifier la configuration
```bash
dbt debug
```

### Exécuter les transformations
```bash
dbt run
```
**Résultat** : 6 modèles créés (3 Silver + 3 Gold)

### Exécuter les tests
```bash
dbt test
```
**Résultat** : 47 tests réussis

### Exécuter un modèle spécifique
```bash
dbt run --select gold_top_weapons_global
```

### Documenter le projet
```bash
dbt docs generate
dbt docs serve
```

---

## 📋 Convention de Nommage

### Format général
- **snake_case** : Toutes les colonnes en minuscules avec underscores
- **Préfixes par entité** :
  - `player_*` : Colonnes liées aux joueurs
  - `weapon_*` : Colonnes liées aux armes
  - `extraction_*` : Métadonnées d'extraction

### Suffixes standards
- `_id` : Identifiant unique
- `_name` : Nom/Label
- `_type` : Catégorie/Type
- `_pct` : Pourcentage (0-1)
- `_rank` : Classement
- `_date` : Date seule
- `_at` : Timestamp complet

### Agrégations
- `total_*` : Somme
- `avg_*` : Moyenne
- `nb_*` : Compteur
- `pct_*` : Pourcentage calculé

---

## 📈 Roadmap Phase 3

### ✅ Complété
- [x] Installation dbt-bigquery
- [x] Configuration profiles.yml (service-account)
- [x] Modèles Silver (3 modèles)
- [x] Modèles Gold MVP (3 modèles)
- [x] Tests de qualité (47 tests)
- [x] Validation des résultats
- [x] Documentation

### 🔜 Prochaines Étapes
- [ ] Phase 4 : Dashboard Streamlit
  - Visualisation du top 3 armes
  - Graphiques par type d'arme
  - Profils des joueurs top 10
- [ ] Phase 5 : Automation Airflow
  - Extraction quotidienne
  - Transformations DBT automatiques
  - Rafraîchissement du dashboard

---

## 🔧 Configuration BigQuery

**Projet** : `battlefield-meta-aggregator`  
**Dataset Bronze** : `bf6_meta`  
**Dataset Silver** : `bf6_meta_silver`  
**Dataset Gold** : `bf6_meta_gold`  
**Méthode d'authentification** : Service Account (keyfile)  
**Location** : `US`  
**Threads** : 4  
**Timeout** : 300s

---

## 📊 Métriques de Performance

**Temps d'exécution** :
- `dbt run` : ~12 secondes (6 modèles)
- `dbt test` : ~17 secondes (47 tests)

**Volume de données** :
- Bronze : 97 joueurs + 288 armes
- Silver : 1 joueur + 3 armes + 3 jointures
- Gold : 3 top armes + 3 par type + 1 ranking

**Coût BigQuery estimé** : < $0.01 par exécution (volumes de test)

---

## 🎓 Ressources DBT

- [Documentation officielle DBT](https://docs.getdbt.com/)
- [dbt-bigquery adapter](https://docs.getdbt.com/reference/warehouse-setups/bigquery-setup)
- [Best practices DBT](https://docs.getdbt.com/best-practices)
- [DBT Transformation Design](../docs/DBT_TRANSFORMATION_DESIGN.md) (design complet)

---

**Dernière mise à jour** : 24 octobre 2025  
**Status** : ✅ Phase 3 complétée - Prêt pour Phase 4 (Streamlit)

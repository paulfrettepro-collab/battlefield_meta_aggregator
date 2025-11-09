# 🎓 DBT & BigQuery Expliqué - Guide Complet pour Débutants

**Date** : 24 octobre 2025  
**Contexte** : Battlefield Meta Aggregator - Phase 3  
**Objectif** : Comprendre comment DBT et BigQuery fonctionnent ensemble

---

## 🤔 Qu'est-ce que DBT (Data Build Tool) ?

### Analogie Simple

Imagine que tu as une **usine de transformation** :
- **Entrée** : Matières premières brutes (données sales, désorganisées)
- **Processus** : Machines de transformation (modèles SQL)
- **Sortie** : Produits finis (données propres, agrégées)

**DBT est cette usine** : il transforme tes données brutes en données analytiques en exécutant des requêtes SQL dans BigQuery.

### Concept Clé : DBT = SQL + Automatisation

```
AVANT DBT :
1. Tu écris du SQL dans BigQuery Console
2. Tu exécutes manuellement
3. Tu crées des tables à la main
4. Tu testes manuellement si les données sont bonnes
5. Tu documentes dans un fichier séparé

AVEC DBT :
1. Tu écris du SQL dans un fichier .sql
2. DBT exécute automatiquement dans le bon ordre
3. DBT crée les tables automatiquement
4. DBT teste automatiquement la qualité des données
5. DBT génère la documentation automatiquement
```

---

## 🏗️ Qu'est-ce que BigQuery ?

### Analogie Simple

BigQuery est comme un **entrepôt géant** avec :
- **Tables** : Étagères où tu stockes tes données
- **Datasets** : Salles différentes (Bronze, Silver, Gold)
- **SQL** : Langage pour trouver/transformer ce que tu cherches
- **Cloud** : L'entrepôt est en ligne, pas sur ton ordinateur

### Caractéristiques Clés

| Caractéristique | Explication | Analogie |
|----------------|-------------|----------|
| **Serverless** | Pas besoin d'installer un serveur | Comme Netflix : tu regardes, tu payes pas le serveur |
| **Scalable** | Peut gérer des milliards de lignes | L'entrepôt s'agrandit automatiquement |
| **SQL** | Langage standard pour requêter | Comme parler français pour commander |
| **Pay-per-query** | Tu payes seulement ce que tu utilises | Comme l'électricité : consommation à la demande |

---

## 🔗 Comment DBT et BigQuery Travaillent Ensemble

### Le Workflow Complet

```
┌─────────────────────────────────────────────────────────┐
│  1. TU ÉCRIS DU SQL (dans ton éditeur local)            │
│     Fichier: dbt/models/silver/silver_players.sql       │
│     Contenu: SELECT TRIM(handle), CAST(rank AS INT64)   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  2. TU LANCES `dbt run` (dans ton terminal)             │
│     DBT lit tous les fichiers .sql                      │
│     DBT détermine l'ordre d'exécution                   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  3. DBT SE CONNECTE À BIGQUERY                          │
│     Utilise config/bigquery-key.json                    │
│     Ouvre une connexion au projet battlefield-meta...   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  4. DBT COMPILE LE SQL                                  │
│     Remplace {{ source('bronze', 'table') }}            │
│     Par `battlefield-meta-aggregator.bf6_meta.table`    │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  5. DBT EXÉCUTE LE SQL DANS BIGQUERY                    │
│     CREATE TABLE bf6_meta_silver.silver_players AS      │
│     SELECT ... FROM bf6_meta.bf6_leaderboard_raw        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  6. BIGQUERY CRÉE LA TABLE                              │
│     Table: bf6_meta_silver.silver_players               │
│     Rows: 97 (résultat de ton SQL)                      │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  7. DBT RETOURNE LE RÉSULTAT                            │
│     ✅ OK created sql table model silver_players        │
│     (97.0 rows, 11.3 KiB processed) in 3.12s            │
└─────────────────────────────────────────────────────────┘
```

---

## 📂 Architecture Bronze → Silver → Gold

### Concept des Médaillons (Medallion Architecture)

C'est une **organisation par niveaux de qualité** des données :

```
┌──────────────────────────────────────────────────────────────┐
│  🥉 BRONZE - Données Brutes (Raw Data)                       │
│  ─────────────────────────────────────────────────────       │
│  • Données telles qu'extraites de Tracker.gg                 │
│  • Aucune transformation                                     │
│  • Format NDJSON uploadé depuis MinIO                        │
│  • Exemples :                                                │
│    - bf6_leaderboard_raw : 97 rows (handle, rank, kills)    │
│    - bf6_top_weapons_raw : 288 rows (weapon_name, kills)    │
│                                                              │
│  📍 Dataset BigQuery : bf6_meta                              │
└──────────────────────────────────────────────────────────────┘
                            ▼
                    DBT Transformations
                   (silver_players.sql)
                            ▼
┌──────────────────────────────────────────────────────────────┐
│  🥈 SILVER - Données Nettoyées (Cleaned Data)                │
│  ─────────────────────────────────────────────────────────   │
│  • Nettoyage : TRIM, UPPER, CAST                             │
│  • Normalisation : Conversion "23.5%" → 0.235                │
│  • Validation : Filtrage is_valid_data = TRUE                │
│  • Enrichissement : Calculs basiques (pct_kills_with_weapon) │
│  • Exemples :                                                │
│    - silver_players : 97 rows (player_handle, total_kills)  │
│    - silver_weapons : 288 rows (weapon_name, weapon_kills)  │
│                                                              │
│  📍 Dataset BigQuery : bf6_meta_silver                       │
└──────────────────────────────────────────────────────────────┘
                            ▼
                    DBT Transformations
                (gold_top_weapons_global.sql)
                            ▼
┌──────────────────────────────────────────────────────────────┐
│  🥇 GOLD - Données Analytiques (Business Logic)              │
│  ─────────────────────────────────────────────────────────   │
│  • Agrégations : SUM, AVG, COUNT                             │
│  • Rankings : ROW_NUMBER(), PARTITION BY                     │
│  • KPIs métier : Top 3 armes, popularité, tendances          │
│  • Exemples :                                                │
│    - gold_top_weapons_global : 3 rows (Top 3 MVP)           │
│    - gold_top_weapons_by_type : 19 rows (Top 3 par type)    │
│                                                              │
│  📍 Dataset BigQuery : bf6_meta_gold                         │
│  🎯 Utilisé directement par le dashboard Streamlit           │
└──────────────────────────────────────────────────────────────┘
```

---

## 🔍 Exemple Concret : silver_players

### 1. Fichier DBT Local

```sql
-- dbt/models/silver/silver_players.sql

{{ config(
    materialized='table',
    description='Joueurs du top 100 avec données nettoyées'
) }}

WITH latest_extraction AS (
    SELECT MAX(DATE(extraction_date)) AS max_date
    FROM {{ source('bronze', 'bf6_leaderboard_raw') }}
),

cleaned_players AS (
    SELECT
        -- Nettoyage
        TRIM(handle) AS player_handle,
        TRIM(player_id) AS player_id,
        
        -- Typage
        CAST(rank AS INT64) AS player_rank,
        CAST(kills AS INT64) AS total_kills,
        
        -- Enrichissement
        CASE
            WHEN rank <= 10 THEN 'Top 10'
            WHEN rank <= 50 THEN 'Top 50'
            ELSE 'Top 100'
        END AS tier
        
    FROM {{ source('bronze', 'bf6_leaderboard_raw') }}
    WHERE DATE(extraction_date) = (SELECT max_date FROM latest_extraction)
)

SELECT * FROM cleaned_players
ORDER BY player_rank
```

### 2. DBT Compile le SQL

Quand tu lances `dbt compile`, DBT remplace les **placeholders** :

```sql
-- target/compiled/bf6_meta_aggregator/models/silver/silver_players.sql

WITH latest_extraction AS (
    SELECT MAX(DATE(extraction_date)) AS max_date
    FROM `battlefield-meta-aggregator`.`bf6_meta`.`bf6_leaderboard_raw`
    --    ^^^^^^^^^^^^^^^^^^^^^^^^^   ^^^^^^^  ^^^^^^^^^^^^^^^^^^^^
    --    Projet GCP                  Dataset  Table
),

cleaned_players AS (
    SELECT
        TRIM(handle) AS player_handle,
        TRIM(player_id) AS player_id,
        CAST(rank AS INT64) AS player_rank,
        CAST(kills AS INT64) AS total_kills,
        CASE
            WHEN rank <= 10 THEN 'Top 10'
            WHEN rank <= 50 THEN 'Top 50'
            ELSE 'Top 100'
        END AS tier
        
    FROM `battlefield-meta-aggregator`.`bf6_meta`.`bf6_leaderboard_raw`
    WHERE DATE(extraction_date) = (SELECT max_date FROM latest_extraction)
)

SELECT * FROM cleaned_players
ORDER BY player_rank
```

### 3. BigQuery Exécute le SQL

BigQuery reçoit ce SQL et :

1. **Lit la table source** : `bf6_meta.bf6_leaderboard_raw` (97 rows)
2. **Exécute la CTE** `latest_extraction` → Trouve la date max : `2025-10-24`
3. **Exécute la CTE** `cleaned_players` → Filtre sur cette date + transformations
4. **Crée la table** : `bf6_meta_silver.silver_players` avec le résultat (97 rows)

### 4. Résultat Visible dans BigQuery Console

Tu peux maintenant aller dans BigQuery Console et voir :

```sql
SELECT * FROM bf6_meta_silver.silver_players LIMIT 5
```

| player_handle | player_id | player_rank | total_kills | tier |
|---------------|-----------|-------------|-------------|------|
| MaxiqYT | 1007029259228 | 4 | 26456 | Top 10 |
| Elxvr | 1006818318336 | 5 | 26182 | Top 10 |
| Cpt_feiyang | 1011325974814 | 6 | 25351 | Top 10 |
| Yuuri(￣﹃￣) | 1014863551490 | 7 | 25303 | Top 10 |
| Rogue | 1014904125952 | 8 | 25273 | Top 10 |

---

## 🧪 Tests DBT : Garantir la Qualité

### Pourquoi Tester ?

Imagine que tu fabriques des pizzas :
- **Sans tests** : Tu ne goûtes jamais, tu espères que c'est bon
- **Avec tests** : Tu vérifies la température, le temps de cuisson, les ingrédients

**DBT tests = Contrôle qualité automatique des données**

### Types de Tests

#### 1. `not_null` : Pas de valeurs vides

```yaml
# schema.yml
- name: player_handle
  tests:
    - not_null  # ❌ Échoue si une ligne a handle = NULL
```

**SQL généré par DBT** :
```sql
SELECT COUNT(*) 
FROM bf6_meta_silver.silver_players
WHERE player_handle IS NULL
-- Si COUNT > 0 → Test échoue
```

#### 2. `unique` : Pas de doublons

```yaml
- name: player_handle
  tests:
    - unique  # ❌ Échoue si 2 joueurs ont le même handle
```

**SQL généré** :
```sql
SELECT player_handle, COUNT(*) as nb
FROM bf6_meta_silver.silver_players
GROUP BY player_handle
HAVING COUNT(*) > 1
-- Si résultat non vide → Test échoue
```

#### 3. `relationships` : Intégrité référentielle

```yaml
- name: player_handle
  tests:
    - relationships:
        to: ref('silver_players')
        field: player_handle
```

**SQL généré** :
```sql
SELECT w.player_handle
FROM bf6_meta_silver.silver_weapons w
LEFT JOIN bf6_meta_silver.silver_players p
  ON w.player_handle = p.player_handle
WHERE p.player_handle IS NULL
-- Si résultat non vide → Il y a des armes sans joueur → Test échoue
```

### Exemple Concret

```bash
$ dbt test

# DBT exécute automatiquement 47 tests :
✅ not_null_silver_players_player_handle ......... [PASS in 1.39s]
✅ unique_silver_players_player_handle ........... [PASS in 1.28s]
✅ relationships_silver_weapons_player_handle ... [PASS in 1.49s]
```

**Traduction** :
- ✅ Aucun joueur n'a un handle NULL
- ✅ Tous les handles sont uniques (pas de doublons)
- ✅ Toutes les armes appartiennent à un joueur existant

---

## 🔄 Dépendances entre Modèles : Le DAG

### C'est quoi un DAG ?

**DAG** = Directed Acyclic Graph (Graphe Orienté Acyclique)

**En français** : Un schéma qui montre **dans quel ordre** exécuter les transformations.

### Visualisation de Tes Modèles

```
bronze (BigQuery sources)
    │
    ├─── bf6_leaderboard_raw ────┐
    │                             ▼
    │                      silver_players ────┐
    │                                         │
    │                                         ▼
    └─── bf6_top_weapons_raw ─── silver_weapons ──── silver_player_weapons
                                        │                      │
                                        ▼                      │
                              gold_top_weapons_global          │
                              gold_top_weapons_by_type         │
                                                               ▼
                                                     gold_player_rankings
```

### Comment DBT Détermine l'Ordre ?

**Grâce aux `ref()` et `source()` dans ton SQL** :

```sql
-- silver_player_weapons.sql
SELECT ...
FROM {{ ref('silver_players') }} p  -- ❶ Dépend de silver_players
INNER JOIN {{ ref('silver_weapons') }} w  -- ❷ Dépend de silver_weapons
```

**DBT sait automatiquement** :
1. Exécuter d'abord `silver_players`
2. Exécuter ensuite `silver_weapons`
3. Exécuter enfin `silver_player_weapons` (car il dépend des 2 autres)

**Résultat `dbt run`** :
```
1 of 6 START silver_players ................. [RUN]
2 of 6 START silver_weapons ................. [RUN]  (parallèle à 1)
1 of 6 OK silver_players .................... [OK in 3.12s]
2 of 6 OK silver_weapons .................... [OK in 3.28s]
3 of 6 START silver_player_weapons .......... [RUN]  (attend 1 et 2)
```

---

## 🎯 Agrégations Gold : Exemple Top 3 Armes

### Requête Complète

```sql
-- dbt/models/gold/gold_top_weapons_global.sql

{{ config(
    materialized='table',
    description='Top 3 armes qui font le plus de kills (MVP Dashboard)'
) }}

WITH weapon_aggregates AS (
    SELECT
        weapon_name,
        weapon_type,
        
        -- Agrégations
        SUM(weapon_kills) AS total_kills,           -- Additionne tous les kills
        COUNT(DISTINCT player_handle) AS nb_players_using,  -- Compte joueurs uniques
        ROUND(AVG(weapon_kills), 0) AS avg_kills_per_player,  -- Moyenne kills/joueur
        
        -- Ranking
        ROW_NUMBER() OVER (ORDER BY SUM(weapon_kills) DESC) AS global_rank
        
    FROM {{ ref('silver_weapons') }}
    GROUP BY weapon_name, weapon_type
)

SELECT *
FROM weapon_aggregates
WHERE global_rank <= 3  -- Garde seulement le top 3
ORDER BY global_rank
```

### Étapes d'Exécution dans BigQuery

#### Étape 1 : Lire la table Silver

```
silver_weapons (288 rows)
┌─────────────┬──────────┬──────────────┬──────────────┐
│ player_handle│weapon_name│weapon_kills  │ weapon_type  │
├─────────────┼──────────┼──────────────┼──────────────┤
│ MaxiqYT     │ M4A1     │ 2,739        │ CARBINES     │
│ Elxvr       │ M4A1     │ 3,126        │ CARBINES     │
│ MaxiqYT     │ SG 553R  │ 2,887        │ CARBINES     │
│ ...         │ ...      │ ...          │ ...          │
└─────────────┴──────────┴──────────────┴──────────────┘
```

#### Étape 2 : GROUP BY weapon_name

```sql
GROUP BY weapon_name, weapon_type
```

BigQuery **regroupe** toutes les lignes avec le même `weapon_name` :

```
┌──────────┬──────────────┬─────────────────────────────────┐
│weapon_name│weapon_type   │ Lignes regroupées               │
├──────────┼──────────────┼─────────────────────────────────┤
│ M4A1     │ CARBINES     │ [2739, 3126, 1842, ...] (35x)   │
│ SG 553R  │ CARBINES     │ [2887, 1564, 3241, ...] (23x)   │
│ M433     │ ASSAULT RIFLES│ [2241, 1893, ...] (24x)        │
│ ...      │ ...          │ ...                             │
└──────────┴──────────────┴─────────────────────────────────┘
```

#### Étape 3 : Calculer les Agrégations

```sql
SUM(weapon_kills) AS total_kills
COUNT(DISTINCT player_handle) AS nb_players_using
ROUND(AVG(weapon_kills), 0) AS avg_kills_per_player
```

**Pour M4A1** :
- `SUM(weapon_kills)` : 2739 + 3126 + 1842 + ... = **95,881 kills**
- `COUNT(DISTINCT player_handle)` : MaxiqYT, Elxvr, ... = **35 joueurs**
- `AVG(weapon_kills)` : 95881 / 35 = **2,739 kills/joueur**

#### Étape 4 : Appliquer le ROW_NUMBER()

```sql
ROW_NUMBER() OVER (ORDER BY SUM(weapon_kills) DESC) AS global_rank
```

BigQuery **trie par total_kills descendant** et assigne un rang :

```
┌──────────┬──────────────┬────────────┬───────────────┬──────────┐
│weapon_name│weapon_type   │total_kills │nb_players_using│global_rank│
├──────────┼──────────────┼────────────┼───────────────┼──────────┤
│ M4A1     │ CARBINES     │ 95,881     │ 35            │ 1        │
│ SG 553R  │ CARBINES     │ 66,392     │ 23            │ 2        │
│ M433     │ ASSAULT RIFLES│ 53,780    │ 24            │ 3        │
│ KORD 6P67│ ASSAULT RIFLES│ 48,235    │ 19            │ 4        │
│ ...      │ ...          │ ...        │ ...           │ ...      │
└──────────┴──────────────┴────────────┴───────────────┴──────────┘
```

#### Étape 5 : Filtrer TOP 3

```sql
WHERE global_rank <= 3
```

Résultat final (3 rows) :

```
┌──────────┬──────────────┬────────────┬───────────────┬──────────┐
│weapon_name│weapon_type   │total_kills │nb_players_using│global_rank│
├──────────┼──────────────┼────────────┼───────────────┼──────────┤
│ M4A1     │ CARBINES     │ 95,881     │ 35            │ 1        │
│ SG 553R  │ CARBINES     │ 66,392     │ 23            │ 2        │
│ M433     │ ASSAULT RIFLES│ 53,780    │ 24            │ 3        │
└──────────┴──────────────┴────────────┴───────────────┴──────────┘
```

---

## 💰 Coûts BigQuery : Pourquoi c'est Gratuit ?

### Tarification BigQuery

BigQuery facture selon **2 critères** :

1. **Stockage** : $0.02 / GB / mois
2. **Requêtes (processing)** : $5 / TB de données scannées

### Ton Cas

| Métrique | Valeur | Coût |
|----------|--------|------|
| **Stockage** | ~50 KB (toutes tables) | 0.000050 GB × $0.02 = **$0.000001/mois** |
| **Queries** | ~200 KB scannés/jour | 0.0002 GB × $5 = **$0.001/jour** |
| **Total mensuel** | 30 jours | **~$0.03/mois** |

**Free Tier BigQuery** :
- ✅ 10 GB stockage gratuit/mois (tu utilises 0.00005 GB)
- ✅ 1 TB queries gratuites/mois (tu utilises ~6 MB)

**Conclusion** : Tant que tu restes sous 1 million de lignes, **c'est 100% gratuit** ✅

---

## 🐛 Le Bug Corrigé : TIMESTAMP vs DATE

### Problème Rencontré

```sql
-- CODE BUGUÉ (retournait 1 row au lieu de 97)
WHERE extraction_date = (SELECT MAX(extraction_date) FROM ...)
```

### Pourquoi Ça Ne Marchait Pas ?

**Les timestamps étaient tous différents** :

```
Joueur 1: 2025-10-24 21:31:34.295407
Joueur 2: 2025-10-24 21:31:34.295480  ← Différence de 73 microsecondes
Joueur 3: 2025-10-24 21:31:34.295539
...
```

`MAX(extraction_date)` retournait : `2025-10-24 21:31:34.301332`

**Résultat** : Un seul joueur avait exactement ce timestamp → 1 row ❌

### Solution

```sql
-- CODE CORRIGÉ
WHERE DATE(extraction_date) = (SELECT MAX(DATE(extraction_date)) FROM ...)
```

`DATE()` convertit le timestamp en date seule :

```
Joueur 1: 2025-10-24
Joueur 2: 2025-10-24  ← Tous identiques
Joueur 3: 2025-10-24
...
```

`MAX(DATE(extraction_date))` retourne : `2025-10-24`

**Résultat** : Tous les 97 joueurs ont cette date → 97 rows ✅

---

## 🎓 Récapitulatif : Ton Pipeline Complet

```
┌─────────────────────────────────────────────────────────────┐
│  1. EXTRACTION (Python + Selenium)                          │
│     scripts/extract_bf6_leaderboard.py                      │
│     scripts/extract_bf6_top_weapons_final.py                │
│     ↓ Résultat : NDJSON files                               │
└─────────────────────────────────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  2. UPLOAD MINIO (Data Lake)                                │
│     scripts/upload_to_minio.py                              │
│     ↓ Stockage : bronze/bf6/leaderboard/*.ndjson            │
└─────────────────────────────────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  3. LOAD BIGQUERY (Data Warehouse)                          │
│     scripts/upload_to_bigquery_v2.py                        │
│     ↓ Tables Bronze : bf6_meta.bf6_leaderboard_raw (97)     │
│                       bf6_meta.bf6_top_weapons_raw (288)    │
└─────────────────────────────────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  4. DBT TRANSFORMATIONS                                     │
│     dbt run --select silver_players                         │
│     ↓ Tables Silver : bf6_meta_silver.silver_players (97)   │
│                       bf6_meta_silver.silver_weapons (288)  │
│                       bf6_meta_silver.silver_player_weapons │
└─────────────────────────────────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  5. DBT AGGREGATIONS                                        │
│     dbt run --select gold_top_weapons_global                │
│     ↓ Tables Gold : bf6_meta_gold.gold_top_weapons_global(3)│
│                     bf6_meta_gold.gold_top_weapons_by_type  │
│                     bf6_meta_gold.gold_player_rankings (96) │
└─────────────────────────────────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  6. DBT TESTS                                               │
│     dbt test                                                │
│     ✅ 47/47 tests validés                                  │
└─────────────────────────────────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  7. DASHBOARD STREAMLIT (prochaine phase)                   │
│     streamlit run dashboard/app.py                          │
│     ↓ Visualisation : Top 3 armes avec graphiques           │
└─────────────────────────────────────────────────────────────┘
```

---

## 🤔 Questions/Réponses

### Q1 : Pourquoi pas faire tout en SQL direct dans BigQuery ?

**Réponse** : Tu pourrais, mais :
- ❌ Pas de versionning (historique des changements)
- ❌ Pas de tests automatiques
- ❌ Pas de documentation auto-générée
- ❌ Difficile de réorganiser/refactorer
- ❌ Ordre d'exécution manuel

**DBT apporte** :
- ✅ Git versioning (chaque changement tracé)
- ✅ Tests automatiques (47 validations)
- ✅ Doc auto (`dbt docs generate`)
- ✅ Refactoring facile (change un modèle, tout se propage)
- ✅ DAG automatique (ordre intelligent)

### Q2 : Les agrégations sont-elles correctes ?

**Oui ! Voici la preuve** :

```sql
-- Vérification manuelle dans BigQuery Console
SELECT 
    weapon_name,
    COUNT(DISTINCT player_handle) as nb_joueurs,
    SUM(weapon_kills) as total_kills
FROM bf6_meta_silver.silver_weapons
WHERE weapon_name = 'M4A1'
GROUP BY weapon_name
```

**Résultat** :
- M4A1 : 35 joueurs, 95,881 kills ✅

**Correspond exactement** au résultat Gold table :
- M4A1 : 35 players, 95,881 kills ✅

### Q3 : Pourquoi 96 rows dans gold_player_rankings au lieu de 97 ?

**Réponse** : Un joueur n'a probablement pas 3 armes extraites (seulement 1 ou 2). La requête Gold utilise un `GROUP BY` qui compte les joueurs ayant au moins une arme.

**Vérification** :
```sql
SELECT COUNT(DISTINCT player_handle) 
FROM bf6_meta_silver.silver_weapons
-- Résultat : 96 (un joueur manque dans weapons)
```

---

## 📚 Ressources pour Approfondir

### DBT
- [DBT Documentation Officielle](https://docs.getdbt.com/)
- [DBT Best Practices](https://docs.getdbt.com/best-practices)
- [DBT BigQuery Adapter](https://docs.getdbt.com/reference/warehouse-setups/bigquery-setup)

### BigQuery
- [BigQuery Documentation](https://cloud.google.com/bigquery/docs)
- [BigQuery SQL Reference](https://cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax)
- [BigQuery Pricing](https://cloud.google.com/bigquery/pricing)

### Ton Projet
- `dbt/README.md` : Documentation DBT locale
- `docs/BIGQUERY_GUIDE.md` : Guide BigQuery complet
- `docs/PHASE_3_COMPLETE.md` : Récap Phase 3
- `docs/DBT_TRANSFORMATION_DESIGN.md` : Design des modèles

---

**Date de création** : 24 octobre 2025  
**Auteur** : Documentation générée pour le projet Battlefield Meta Aggregator  
**Statut** : ✅ Complet et validé

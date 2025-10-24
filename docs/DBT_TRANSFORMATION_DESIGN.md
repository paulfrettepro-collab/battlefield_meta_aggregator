# 🏗️ Design des Transformations DBT - Battlefield Meta Aggregator

**Date de création** : 24 octobre 2025  
**Objectif MVP** : Top 3 des armes qui font le plus de kills  
**Évolution future** : Métriques avancées (accuracy, headshot%, damage, etc.)

---

## 📊 Architecture des Données

```
BRONZE (Raw Data)           SILVER (Cleaned)              GOLD (Analytics)
─────────────────           ─────────────────             ─────────────────
bf6_leaderboard_raw    →    silver_players          →    gold_top_weapons_global
bf6_top_weapons_raw    →    silver_weapons          →    gold_top_weapons_by_type
                            silver_player_weapons   →    gold_player_rankings
                                                    →    gold_weapon_meta_trends
```

---

## 🥉 COUCHE BRONZE (Raw Data)

### Données actuelles extraites

#### Table : `bf6_leaderboard_raw`
```json
{
  "handle": "MaxiqYT",
  "player_id": "1007029259228",
  "rank": 4,
  "kills": 26456,
  "extraction_date": "2025-10-24T21:31:34.295407",
  "url_source": "https://tracker.gg/bf6/leaderboards?platform=all&board=Kills&page=1"
}
```

**Colonnes** :
- `handle` (STRING) - Pseudo du joueur (PRIMARY KEY pour jointures)
- `player_id` (STRING) - ID unique tracker.gg
- `rank` (INTEGER) - Rang dans le leaderboard
- `kills` (INTEGER) - Total de kills
- `extraction_date` (TIMESTAMP) - Date d'extraction
- `url_source` (STRING) - URL source

#### Table : `bf6_top_weapons_raw`
```json
{
  "handle": "MaxiqYT",
  "player_id": "1007029259228",
  "top_weapons": [
    {
      "weapon_name": "KV9",
      "kills": 8535,
      "rank": 1,
      "weapon_type": "SMG",
      "time_played": "12h 30m",
      "damage": 450000,
      "accuracy": "23.5%",
      "headshot_pct": "18.2%"
    }
  ],
  "total_weapons_found": 44,
  "status": "success",
  "extraction_date": "2025-10-24T22:00:00.000000"
}
```

**Colonnes** :
- `handle` (STRING) - Pseudo du joueur (FK → leaderboard)
- `player_id` (STRING) - ID unique
- `top_weapons` (ARRAY<STRUCT>) - Top 3 armes (structure nested)
- `total_weapons_found` (INTEGER) - Total d'armes trouvées
- `status` (STRING) - Statut extraction (success/error)
- `extraction_date` (TIMESTAMP) - Date d'extraction

---

## 🥈 COUCHE SILVER (Cleaned & Normalized)

### Objectifs de la couche Silver
1. **Nettoyage** : Gérer les valeurs nulles, formater correctement
2. **Normalisation** : Convertir les types, standardiser les formats
3. **Dénormalisation** : Aplatir les structures ARRAY pour faciliter les analyses
4. **Enrichissement** : Ajouter des métriques calculées de base
5. **Qualité** : Tests DBT pour garantir l'intégrité

---

### 📋 Modèle 1 : `silver_players`

**Objectif** : Table propre des joueurs avec leurs statistiques de base

```sql
-- models/silver/silver_players.sql

{{ config(
    materialized='table',
    description='Joueurs du top 100 leaderboard avec données nettoyées'
) }}

WITH latest_extraction AS (
    SELECT MAX(extraction_date) AS max_date
    FROM {{ source('bronze', 'bf6_leaderboard_raw') }}
),

cleaned_players AS (
    SELECT
        -- Identifiants
        TRIM(handle) AS player_handle,
        TRIM(player_id) AS player_id,
        
        -- Métriques
        CAST(rank AS INT64) AS player_rank,
        CAST(kills AS INT64) AS total_kills,
        
        -- Métadonnées
        CAST(extraction_date AS TIMESTAMP) AS extracted_at,
        DATE(extraction_date) AS extraction_date,
        url_source,
        
        -- Flags de qualité
        CASE 
            WHEN kills > 0 THEN TRUE 
            ELSE FALSE 
        END AS is_valid_data,
        
        -- Catégorisation
        CASE
            WHEN rank <= 10 THEN 'Top 10'
            WHEN rank <= 50 THEN 'Top 50'
            WHEN rank <= 100 THEN 'Top 100'
            ELSE 'Other'
        END AS tier
        
    FROM {{ source('bronze', 'bf6_leaderboard_raw') }}
    WHERE extraction_date = (SELECT max_date FROM latest_extraction)
)

SELECT * FROM cleaned_players
WHERE is_valid_data = TRUE
ORDER BY player_rank
```

**Règles de transformation** :
- ✅ TRIM des espaces sur `handle` et `player_id`
- ✅ CAST explicite des types numériques
- ✅ Extraction de la date seule pour partitionnement
- ✅ Flag de validation (`is_valid_data`)
- ✅ Catégorisation en tiers (Top 10/50/100)
- ✅ Filtre sur la dernière extraction uniquement

**Tests DBT** :
```yaml
# models/silver/silver_players.yml
version: 2

models:
  - name: silver_players
    description: "Joueurs top 100 avec données nettoyées"
    columns:
      - name: player_handle
        description: "Pseudo unique du joueur"
        tests:
          - not_null
          - unique
      
      - name: player_id
        description: "ID tracker.gg unique"
        tests:
          - not_null
          - unique
      
      - name: player_rank
        description: "Rang dans le leaderboard (4-100)"
        tests:
          - not_null
          - accepted_values:
              values: [4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100]
      
      - name: total_kills
        description: "Total de kills du joueur"
        tests:
          - not_null
          - dbt_utils.accepted_range:
              min_value: 1000
              max_value: 50000
      
      - name: is_valid_data
        description: "Flag de qualité des données"
        tests:
          - not_null
          - accepted_values:
              values: [true]
```

---

### 🔫 Modèle 2 : `silver_weapons`

**Objectif** : Table dénormalisée des armes avec toutes les métriques

```sql
-- models/silver/silver_weapons.sql

{{ config(
    materialized='table',
    description='Top 3 armes par joueur avec métriques nettoyées et normalisées'
) }}

WITH latest_extraction AS (
    SELECT MAX(extraction_date) AS max_date
    FROM {{ source('bronze', 'bf6_top_weapons_raw') }}
),

unnested_weapons AS (
    SELECT
        -- Identifiants joueur
        TRIM(handle) AS player_handle,
        TRIM(player_id) AS player_id,
        
        -- Dénormalisation de l'ARRAY top_weapons
        weapon.weapon_name AS weapon_name,
        weapon.kills AS weapon_kills,
        weapon.rank AS weapon_rank_for_player,
        weapon.weapon_type AS weapon_type,
        weapon.time_played AS time_played_raw,
        weapon.damage AS total_damage,
        weapon.accuracy AS accuracy_raw,
        weapon.headshot_pct AS headshot_pct_raw,
        
        -- Métadonnées
        total_weapons_found,
        status AS extraction_status,
        CAST(extraction_date AS TIMESTAMP) AS extracted_at,
        DATE(extraction_date) AS extraction_date
        
    FROM {{ source('bronze', 'bf6_top_weapons_raw') }},
    UNNEST(top_weapons) AS weapon
    WHERE extraction_date = (SELECT max_date FROM latest_extraction)
      AND status = 'success'
),

cleaned_weapons AS (
    SELECT
        -- Identifiants
        player_handle,
        player_id,
        
        -- Arme
        UPPER(TRIM(weapon_name)) AS weapon_name,
        UPPER(TRIM(COALESCE(weapon_type, 'Unknown'))) AS weapon_type,
        
        -- Métriques principales (MVP)
        CAST(weapon_kills AS INT64) AS weapon_kills,
        CAST(weapon_rank_for_player AS INT64) AS weapon_rank_for_player,
        
        -- Métriques secondaires (Phase 2)
        CAST(total_damage AS INT64) AS total_damage,
        
        -- Conversion accuracy "23.5%" → 0.235 (FLOAT64)
        CASE 
            WHEN accuracy_raw IS NOT NULL 
            THEN CAST(REPLACE(accuracy_raw, '%', '') AS FLOAT64) / 100
            ELSE NULL
        END AS accuracy,
        
        -- Conversion headshot_pct "18.2%" → 0.182 (FLOAT64)
        CASE 
            WHEN headshot_pct_raw IS NOT NULL 
            THEN CAST(REPLACE(headshot_pct_raw, '%', '') AS FLOAT64) / 100
            ELSE NULL
        END AS headshot_pct,
        
        -- Time played (garder string pour l'instant, parser en Phase 2)
        time_played_raw AS time_played,
        
        -- Métadonnées
        total_weapons_found,
        extraction_status,
        extracted_at,
        extraction_date,
        
        -- Flags de qualité
        CASE 
            WHEN weapon_kills > 0 THEN TRUE 
            ELSE FALSE 
        END AS is_valid_weapon
        
    FROM unnested_weapons
)

SELECT * FROM cleaned_weapons
WHERE is_valid_weapon = TRUE
ORDER BY player_handle, weapon_rank_for_player
```

**Règles de transformation** :
- ✅ UNNEST de l'ARRAY `top_weapons` → 1 ligne par arme
- ✅ UPPER et TRIM sur les noms d'armes (normalisation)
- ✅ Conversion accuracy et headshot_pct : `"23.5%"` → `0.235`
- ✅ COALESCE sur weapon_type (gérer les nulls)
- ✅ Flag de validation par arme
- ✅ Filtre sur extraction réussie uniquement

**Tests DBT** :
```yaml
# models/silver/silver_weapons.yml
version: 2

models:
  - name: silver_weapons
    description: "Top 3 armes par joueur avec métriques nettoyées"
    columns:
      - name: player_handle
        description: "Pseudo du joueur"
        tests:
          - not_null
          - relationships:
              to: ref('silver_players')
              field: player_handle
      
      - name: weapon_name
        description: "Nom de l'arme (normalisé UPPER)"
        tests:
          - not_null
      
      - name: weapon_type
        description: "Type d'arme (SMG, AR, LMG, etc.)"
        tests:
          - not_null
          - accepted_values:
              values: ['SMG', 'ASSAULT RIFLES', 'LMG', 'SNIPER RIFLES', 
                       'CARBINES', 'SHOTGUNS', 'PISTOLS', 'UNKNOWN']
      
      - name: weapon_kills
        description: "Kills avec cette arme"
        tests:
          - not_null
          - dbt_utils.accepted_range:
              min_value: 1
              max_value: 20000
      
      - name: weapon_rank_for_player
        description: "Rang de l'arme pour ce joueur (1-3)"
        tests:
          - not_null
          - accepted_values:
              values: [1, 2, 3]
      
      - name: accuracy
        description: "Précision (0.0-1.0)"
        tests:
          - dbt_utils.accepted_range:
              min_value: 0
              max_value: 1
              inclusive: true
      
      - name: headshot_pct
        description: "% headshots (0.0-1.0)"
        tests:
          - dbt_utils.accepted_range:
              min_value: 0
              max_value: 1
              inclusive: true
```

---

### 🎯 Modèle 3 : `silver_player_weapons`

**Objectif** : Vue complète joueur + armes (jointure facilitée)

```sql
-- models/silver/silver_player_weapons.sql

{{ config(
    materialized='table',
    description='Vue enrichie combinant joueurs et leurs top 3 armes'
) }}

SELECT
    -- Joueur
    p.player_handle,
    p.player_id,
    p.player_rank,
    p.total_kills AS player_total_kills,
    p.tier AS player_tier,
    
    -- Arme
    w.weapon_name,
    w.weapon_type,
    w.weapon_kills,
    w.weapon_rank_for_player,
    w.total_damage,
    w.accuracy,
    w.headshot_pct,
    w.time_played,
    
    -- Métriques calculées
    ROUND(w.weapon_kills * 100.0 / p.total_kills, 2) AS pct_kills_with_weapon,
    
    -- Métadonnées
    p.extraction_date,
    p.extracted_at

FROM {{ ref('silver_players') }} p
INNER JOIN {{ ref('silver_weapons') }} w
    ON p.player_handle = w.player_handle
    AND p.extraction_date = w.extraction_date

ORDER BY p.player_rank, w.weapon_rank_for_player
```

**Règles de transformation** :
- ✅ INNER JOIN (seulement les joueurs avec armes extraites)
- ✅ Calcul du % de kills par arme vs total joueur
- ✅ Préservation des métadonnées de fraîcheur

**Tests DBT** :
```yaml
# models/silver/silver_player_weapons.yml
version: 2

models:
  - name: silver_player_weapons
    description: "Vue complète joueurs + top 3 armes"
    tests:
      - dbt_utils.unique_combination_of_columns:
          combination_of_columns:
            - player_handle
            - weapon_name
    
    columns:
      - name: pct_kills_with_weapon
        description: "% des kills du joueur avec cette arme"
        tests:
          - not_null
          - dbt_utils.accepted_range:
              min_value: 0
              max_value: 100
```

---

## 🥇 COUCHE GOLD (Analytics & Business Logic)

### Objectifs de la couche Gold
1. **Agrégations** : Top armes globales, par type, par tier
2. **Tendances** : Évolution du méta dans le temps
3. **Rankings** : Classements multi-critères
4. **Dashboard-ready** : Tables optimisées pour Streamlit

---

### 🏆 Modèle 1 : `gold_top_weapons_global` (MVP)

**Objectif** : Top 3 des armes qui font le PLUS de kills (toutes catégories)

```sql
-- models/gold/gold_top_weapons_global.sql

{{ config(
    materialized='table',
    description='Top 3 armes qui font le plus de kills (MVP Dashboard)'
) }}

WITH weapon_aggregates AS (
    SELECT
        weapon_name,
        weapon_type,
        
        -- Métriques principales (MVP)
        SUM(weapon_kills) AS total_kills,
        COUNT(DISTINCT player_handle) AS nb_players_using,
        ROUND(AVG(weapon_kills), 0) AS avg_kills_per_player,
        
        -- Métriques secondaires (Phase 2)
        ROUND(AVG(accuracy), 3) AS avg_accuracy,
        ROUND(AVG(headshot_pct), 3) AS avg_headshot_pct,
        SUM(total_damage) AS total_damage_dealt,
        
        -- Ranking
        ROW_NUMBER() OVER (ORDER BY SUM(weapon_kills) DESC) AS global_rank
        
    FROM {{ ref('silver_weapons') }}
    GROUP BY weapon_name, weapon_type
)

SELECT
    global_rank,
    weapon_name,
    weapon_type,
    total_kills,
    nb_players_using,
    avg_kills_per_player,
    avg_accuracy,
    avg_headshot_pct,
    total_damage_dealt,
    
    -- Métadonnées
    CURRENT_TIMESTAMP() AS generated_at

FROM weapon_aggregates
WHERE global_rank <= 3  -- TOP 3 ONLY (MVP)
ORDER BY global_rank
```

**Résultat attendu** :
| global_rank | weapon_name | weapon_type | total_kills | nb_players_using | avg_kills_per_player |
|-------------|-------------|-------------|-------------|------------------|----------------------|
| 1           | KV9         | SMG         | 150,000     | 35               | 4,286                |
| 2           | M4A1        | CARBINES    | 120,000     | 40               | 3,000                |
| 3           | KORD 6P67   | ASSAULT RIFLES | 110,000  | 38               | 2,895                |

---

### 📊 Modèle 2 : `gold_top_weapons_by_type`

**Objectif** : Top 3 armes par TYPE (SMG, AR, LMG, etc.)

```sql
-- models/gold/gold_top_weapons_by_type.sql

{{ config(
    materialized='table',
    description='Top 3 armes par catégorie de weapon_type'
) }}

WITH weapon_aggregates AS (
    SELECT
        weapon_type,
        weapon_name,
        
        SUM(weapon_kills) AS total_kills,
        COUNT(DISTINCT player_handle) AS nb_players_using,
        ROUND(AVG(weapon_kills), 0) AS avg_kills_per_player,
        ROUND(AVG(accuracy), 3) AS avg_accuracy,
        ROUND(AVG(headshot_pct), 3) AS avg_headshot_pct,
        
        ROW_NUMBER() OVER (
            PARTITION BY weapon_type 
            ORDER BY SUM(weapon_kills) DESC
        ) AS rank_in_type
        
    FROM {{ ref('silver_weapons') }}
    GROUP BY weapon_type, weapon_name
)

SELECT * FROM weapon_aggregates
WHERE rank_in_type <= 3
ORDER BY weapon_type, rank_in_type
```

**Résultat attendu** :
| weapon_type    | weapon_name | rank_in_type | total_kills | nb_players_using |
|----------------|-------------|--------------|-------------|------------------|
| SMG            | KV9         | 1            | 150,000     | 35               |
| SMG            | PW5A3       | 2            | 80,000      | 25               |
| SMG            | SCW-10      | 3            | 75,000      | 30               |
| ASSAULT RIFLES | KORD 6P67   | 1            | 110,000     | 38               |
| ASSAULT RIFLES | NVO-228E    | 2            | 95,000      | 28               |

---

### 👑 Modèle 3 : `gold_player_rankings`

**Objectif** : Classement des joueurs avec leurs armes préférées

```sql
-- models/gold/gold_player_rankings.sql

{{ config(
    materialized='table',
    description='Classement des joueurs avec leurs armes principales'
) }}

WITH player_main_weapon AS (
    SELECT
        player_handle,
        player_rank,
        player_total_kills,
        player_tier,
        
        -- Arme #1 du joueur
        MAX(CASE WHEN weapon_rank_for_player = 1 THEN weapon_name END) AS main_weapon,
        MAX(CASE WHEN weapon_rank_for_player = 1 THEN weapon_type END) AS main_weapon_type,
        MAX(CASE WHEN weapon_rank_for_player = 1 THEN weapon_kills END) AS main_weapon_kills,
        
        -- Arme #2 du joueur
        MAX(CASE WHEN weapon_rank_for_player = 2 THEN weapon_name END) AS secondary_weapon,
        MAX(CASE WHEN weapon_rank_for_player = 2 THEN weapon_kills END) AS secondary_weapon_kills,
        
        -- Arme #3 du joueur
        MAX(CASE WHEN weapon_rank_for_player = 3 THEN weapon_name END) AS tertiary_weapon,
        MAX(CASE WHEN weapon_rank_for_player = 3 THEN weapon_kills END) AS tertiary_weapon_kills,
        
        -- Stats globales
        ROUND(AVG(accuracy), 3) AS avg_accuracy_top3,
        ROUND(AVG(headshot_pct), 3) AS avg_headshot_pct_top3
        
    FROM {{ ref('silver_player_weapons') }}
    GROUP BY player_handle, player_rank, player_total_kills, player_tier
)

SELECT * FROM player_main_weapon
ORDER BY player_rank
```

---

### 📈 Modèle 4 : `gold_weapon_meta_trends` (Phase 2)

**Objectif** : Évolution du méta dans le temps (extraction journalière)

```sql
-- models/gold/gold_weapon_meta_trends.sql

{{ config(
    materialized='incremental',
    unique_key='snapshot_key',
    description='Évolution du top armes dans le temps'
) }}

WITH daily_snapshot AS (
    SELECT
        extraction_date,
        weapon_name,
        weapon_type,
        
        SUM(weapon_kills) AS total_kills,
        COUNT(DISTINCT player_handle) AS nb_players_using,
        
        CONCAT(
            CAST(extraction_date AS STRING), 
            '_', 
            weapon_name
        ) AS snapshot_key
        
    FROM {{ ref('silver_weapons') }}
    
    {% if is_incremental() %}
        WHERE extraction_date > (SELECT MAX(extraction_date) FROM {{ this }})
    {% endif %}
    
    GROUP BY extraction_date, weapon_name, weapon_type
)

SELECT * FROM daily_snapshot
ORDER BY extraction_date DESC, total_kills DESC
```

---

## 🧪 Plan de Tests DBT

### Tests génériques (schema.yml)
```yaml
tests:
  - unique
  - not_null
  - relationships
  - accepted_values
  - dbt_utils.accepted_range
  - dbt_utils.unique_combination_of_columns
```

### Tests personnalisés

#### Test 1 : Cohérence des kills
```sql
-- tests/assert_total_kills_coherence.sql
-- Vérifie que la somme des kills par arme ≤ total kills joueur

SELECT
    player_handle,
    player_total_kills,
    SUM(weapon_kills) AS sum_weapon_kills
FROM {{ ref('silver_player_weapons') }}
GROUP BY player_handle, player_total_kills
HAVING SUM(weapon_kills) > player_total_kills
```

#### Test 2 : Pas de doublons
```sql
-- tests/assert_no_duplicate_weapons_per_player.sql

SELECT
    player_handle,
    weapon_name,
    COUNT(*) AS cnt
FROM {{ ref('silver_weapons') }}
GROUP BY player_handle, weapon_name
HAVING COUNT(*) > 1
```

---

## 📋 Roadmap d'Implémentation

### Phase 1 : MVP (Aujourd'hui)
- [x] Extraction leaderboard (97 joueurs)
- [ ] Extraction weapons (en cours ~23/97)
- [ ] Upload Bronze → BigQuery
- [ ] Créer modèles Silver (3 modèles)
- [ ] Créer modèle Gold MVP (`gold_top_weapons_global`)
- [ ] Tests DBT basiques
- [ ] Dashboard Streamlit : Top 3 armes

### Phase 2 : Métriques Avancées
- [ ] Intégrer accuracy, headshot%, damage
- [ ] Parser `time_played` (conversion en minutes)
- [ ] Modèle `gold_top_weapons_by_type`
- [ ] Modèle `gold_player_rankings`
- [ ] Dashboard : Filtres par type d'arme

### Phase 3 : Historique
- [ ] Extraction quotidienne (Airflow)
- [ ] Modèle incrémental `gold_weapon_meta_trends`
- [ ] Dashboard : Graphiques d'évolution temporelle

---

## 📝 Convention de Nommage des Colonnes

### Règles Générales

Pour garantir la cohérence et la lisibilité à travers toutes les couches, nous suivons ces conventions :

#### 1. **Format Snake_Case**
- Toutes les colonnes en **minuscules** avec **underscores** (`_`)
- ✅ `player_handle`, `weapon_kills`, `extraction_date`
- ❌ `PlayerHandle`, `weaponKills`, `ExtractionDate`

#### 2. **Préfixes par Entité**

| Entité | Préfixe | Exemples |
|--------|---------|----------|
| **Joueur** | `player_` | `player_handle`, `player_rank`, `player_id` |
| **Arme** | `weapon_` | `weapon_name`, `weapon_kills`, `weapon_type` |
| **Extraction** | `extraction_` | `extraction_date`, `extraction_status` |
| **Métriques calculées** | Aucun préfixe | `total_kills`, `avg_accuracy`, `nb_players_using` |
| **Métadonnées** | Suffixe `_at` | `extracted_at`, `generated_at`, `updated_at` |

#### 3. **Suffixes Standards**

| Suffixe | Signification | Exemples |
|---------|---------------|----------|
| `_id` | Identifiant unique | `player_id`, `weapon_id` |
| `_name` | Nom/Label | `weapon_name`, `player_handle` |
| `_type` | Catégorie/Type | `weapon_type`, `player_tier` |
| `_pct` | Pourcentage (0-1) | `headshot_pct`, `accuracy_pct` |
| `_count` | Compteur | `weapon_count`, `player_count` |
| `_rank` | Classement | `player_rank`, `weapon_rank_for_player`, `global_rank` |
| `_date` | Date seule | `extraction_date`, `snapshot_date` |
| `_at` | Timestamp complet | `extracted_at`, `created_at` |
| `_raw` | Valeur brute non transformée | `accuracy_raw`, `time_played_raw` |

#### 4. **Noms Interdits**

❌ Éviter les noms ambigus ou réservés SQL :
- `rank` seul → Utiliser `player_rank` ou `weapon_rank`
- `type` seul → Utiliser `weapon_type` ou `entity_type`
- `date` seul → Utiliser `extraction_date` ou `snapshot_date`
- `handle` seul → Utiliser `player_handle`
- `kills` seul → Utiliser `total_kills`, `weapon_kills`, ou `player_total_kills`

#### 5. **Agrégations et Statistiques**

| Type | Format | Exemples |
|------|--------|----------|
| **Total** | `total_*` | `total_kills`, `total_damage`, `total_weapons_found` |
| **Moyenne** | `avg_*` | `avg_accuracy`, `avg_kills_per_player`, `avg_headshot_pct` |
| **Maximum** | `max_*` | `max_kills`, `max_damage` |
| **Minimum** | `min_*` | `min_accuracy`, `min_kills` |
| **Compteur** | `nb_*` ou `count_*` | `nb_players_using`, `count_extractions` |
| **Pourcentage** | `pct_*` | `pct_kills_with_weapon`, `pct_of_total` |

#### 6. **Booléens et Flags**

Format : `is_*` ou `has_*`
- ✅ `is_valid_data`, `is_top_weapon`, `has_accuracy_data`
- ❌ `valid`, `top_weapon`, `accuracy_available`

---

## 🗂️ Mapping des Colonnes par Couche

### Bronze → Silver

| Bronze (Raw) | Silver (Cleaned) | Transformation |
|--------------|------------------|----------------|
| `handle` | `player_handle` | TRIM() + Préfixe ajouté |
| `player_id` | `player_id` | TRIM() uniquement |
| `rank` | `player_rank` | CAST(INT64) + Préfixe |
| `kills` | `total_kills` | CAST(INT64) + Renommage |
| `extraction_date` | `extraction_date` | DATE(extraction_date) |
| `extraction_date` | `extracted_at` | CAST(TIMESTAMP) |
| `weapon.weapon_name` | `weapon_name` | UPPER(TRIM()) |
| `weapon.kills` | `weapon_kills` | CAST(INT64) + Préfixe |
| `weapon.rank` | `weapon_rank_for_player` | CAST(INT64) + Renommage explicite |
| `weapon.weapon_type` | `weapon_type` | UPPER(TRIM()) |
| `weapon.accuracy` | `accuracy` | Conversion "23.5%" → 0.235 |
| `weapon.headshot_pct` | `headshot_pct` | Conversion "18.2%" → 0.182 |

### Silver → Gold

| Silver | Gold | Transformation |
|--------|------|----------------|
| `player_handle` | `player_handle` | Inchangé |
| `player_rank` | `player_rank` | Inchangé |
| `weapon_name` | `weapon_name` | Inchangé |
| `weapon_kills` | `total_kills` | SUM() → Renommage pour clarté |
| `weapon_kills` | `avg_kills_per_player` | AVG() → Nouveau nom explicite |
| `player_handle` | `nb_players_using` | COUNT(DISTINCT) → Nouveau |
| `accuracy` | `avg_accuracy` | AVG() → Préfixe ajouté |
| N/A | `global_rank` | ROW_NUMBER() → Nouveau |
| N/A | `rank_in_type` | ROW_NUMBER() PARTITION BY → Nouveau |

---

## 🎯 Résumé des Règles de Transformation

### Silver Layer
| Règle | Description |
|-------|-------------|
| **Normalisation des noms** | UPPER() + TRIM() sur weapon_name et weapon_type |
| **Convention snake_case** | Toutes colonnes en minuscules avec underscores |
| **Préfixes par entité** | `player_*`, `weapon_*`, `extraction_*` |
| **Conversion types** | STRING → INT64/FLOAT64 avec CAST explicite |
| **Gestion des nulls** | COALESCE avec valeurs par défaut ('Unknown', 0) |
| **Dénormalisation** | UNNEST des ARRAY → 1 ligne par arme |
| **Conversion pourcentages** | "23.5%" → 0.235 (division par 100) |
| **Flags de qualité** | is_valid_data, is_valid_weapon (booléens) |
| **Dernière extraction** | Filtre sur MAX(extraction_date) |

### Gold Layer
| Règle | Description |
|-------|-------------|
| **Préfixes d'agrégation** | `total_*`, `avg_*`, `nb_*`, `pct_*` |
| **Suffixes de ranking** | `*_rank`, `rank_in_*` |
| **Agrégations** | SUM, AVG, COUNT sur groupes logiques |
| **Window Functions** | ROW_NUMBER() pour rankings globaux et par partition |
| **TOP N** | WHERE rank <= 3 pour MVP, configurable ensuite |
| **Arrondis** | ROUND(value, 0) pour kills, ROUND(value, 3) pour % |
| **Snapshot** | CONCAT(date, '_', weapon_name) pour clé unique historique |
| **Incrémental** | Materialized='incremental' pour trends temporels |

---

## 📊 Exemples de Nommage par Cas d'Usage

### Cas 1 : Statistiques d'une arme
```sql
SELECT
    weapon_name,                    -- Nom de l'arme
    weapon_type,                    -- Catégorie (SMG, AR...)
    total_kills,                    -- Somme des kills
    avg_kills_per_player,           -- Moyenne par joueur
    nb_players_using,               -- Nombre d'utilisateurs
    avg_accuracy,                   -- Précision moyenne
    global_rank                     -- Rang global
FROM gold_top_weapons_global
```

### Cas 2 : Profil d'un joueur
```sql
SELECT
    player_handle,                  -- Pseudo
    player_id,                      -- ID unique
    player_rank,                    -- Rang leaderboard
    player_total_kills,             -- Total kills
    player_tier,                    -- Top 10/50/100
    main_weapon,                    -- Arme principale
    main_weapon_kills,              -- Kills avec arme principale
    pct_kills_with_weapon,          -- % kills avec cette arme
    avg_accuracy_top3               -- Précision moyenne top 3
FROM gold_player_rankings
```

### Cas 3 : Métadonnées et traçabilité
```sql
SELECT
    extraction_date,                -- Date d'extraction (DATE)
    extracted_at,                   -- Timestamp complet (TIMESTAMP)
    extraction_status,              -- success/error
    total_weapons_found,            -- Nombre d'armes trouvées
    is_valid_data,                  -- Flag de qualité
    generated_at                    -- Timestamp génération table Gold
FROM silver_weapons
```

---

## ✅ Checklist de Validation

Avant de déployer en production :

- [ ] Les 3 modèles Silver compilent sans erreur (`dbt compile`)
- [ ] Les 4 modèles Gold compilent sans erreur
- [ ] Tous les tests génériques passent (`dbt test`)
- [ ] Les tests personnalisés ne retournent pas de lignes
- [ ] La documentation est générée (`dbt docs generate`)
- [ ] Le top 3 dans `gold_top_weapons_global` est cohérent
- [ ] Les pourcentages (accuracy, headshot) sont entre 0 et 1
- [ ] Aucune valeur NULL dans les colonnes critiques
- [ ] Les jointures Silver ↔ Gold ne perdent pas de données

---

**Prochaine étape** : Attendre la fin de l'extraction (40 min), valider les données Bronze, puis créer les premiers modèles Silver ! 🚀

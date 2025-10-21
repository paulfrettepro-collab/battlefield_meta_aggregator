# 🔗 Problème de Jointure entre Fichiers

## 🚨 Problème Identifié

**Nous avons 2 fichiers distincts SANS clé commune** :

### Fichier 1 : `bf6_leaderboard_2025-10-18_174621.ndjson`
```json
{
  "rank": 1,
  "username_original": "Happy_3201",
  "username_hash": "player_b97fd6bc",
  "stats": {"kills": 95150},
  ...
}
```
**Clés disponibles** : `username_original`, `username_hash`, `rank`

### Fichier 2 : `bf6_top_weapons_2025-10-20_200220.ndjson`
```json
{
  "player_id": "2649085103",
  "handle": "SKTelecomT1_Nova",
  "top_weapons": [...],
  ...
}
```
**Clés disponibles** : `player_id`, `handle`

---

## ❌ Pourquoi Aucune Clé Commune ?

### 1. **Extractions Différentes**
- **Leaderboard** : Extrait le 18 octobre (ancien test)
- **Top Weapons** : Extrait le 20 octobre (production)

### 2. **Sources Différentes**
- **Leaderboard** : Page HTML du classement (pas de player_id)
- **Top Weapons** : Pages profil individuelles (avec player_id)

### 3. **Méthodes Différentes**
- **Leaderboard** : Extraction simple du tableau HTML
- **Top Weapons** : Navigation vers chaque profil (récupère player_id depuis l'URL)

---

## 💡 Solutions Possibles

### ✅ Solution 1 : REJOINDRE PAR PSEUDO (Risqué)
```sql
-- Dans BigQuery
SELECT 
  l.rank,
  l.username_original,
  w.player_id,
  w.top_weapons
FROM leaderboard l
LEFT JOIN weapons w
  ON l.username_original = w.handle
```

**⚠️ PROBLÈME** :
- Les pseudos peuvent changer
- Casse différente possible (Happy_3201 vs happy_3201)
- Caractères spéciaux

---

### ✅ Solution 2 : EXTRAIRE LE LEADERBOARD AVEC player_id (RECOMMANDÉ)

**Modifier le script d'extraction du leaderboard** pour récupérer le `player_id` depuis l'URL du profil :

```python
# Ancien code (leaderboard seulement)
for row in table:
    rank = row.find('td', class_='rank').text
    username = row.find('td', class_='player').text
    # ❌ Pas de player_id

# Nouveau code (leaderboard + player_id)
for row in table:
    rank = row.find('td', class_='rank').text
    player_link = row.find('a', class_='player-link')
    
    # Extraire player_id depuis l'URL
    # Exemple: https://tracker.gg/bf6/profile/origin/SKTelecomT1_Nova/overview
    #          → player_id dans l'URL ou requête API
    player_id = extract_player_id_from_url(player_link['href'])
    username = player_link.text
```

---

### ✅ Solution 3 : FUSIONNER LES 2 EXTRACTIONS (IDÉAL)

**Créer UN SEUL script qui extrait tout en même temps** :

```python
def extract_leaderboard_with_weapons():
    """
    1. Extrait le leaderboard (rank, username, player_id)
    2. Pour chaque joueur, extrait ses top 3 armes
    3. Tout dans 1 fichier avec clé commune
    """
    
    # Résultat final (1 fichier unifié)
    {
      "rank": 1,
      "player_id": "2649085103",      # ✅ CLÉ COMMUNE
      "handle": "SKTelecomT1_Nova",
      "stats": {"kills": 95150},
      "top_weapons": [
        {"name": "L85A3", "kills": 31519},
        {"name": "NVO-228E", "kills": 17710},
        {"name": "AK-205", "kills": 17212}
      ]
    }
```

---

## ✅ Solution 3 : IMPLÉMENTÉE !

### Pourquoi c'est la meilleure ?
1. **Une seule extraction** = Cohérence des données
2. **Clé naturelle** = `player_id` présent partout
3. **Moins de complexité** = Pas de jointure nécessaire
4. **Plus fiable** = Pas de risque de désynchronisation

### ✅ Modification effectuée
Le script `extract_bf6_top_weapons.py` a été modifié pour inclure le **rank** :
- Extraction du rang depuis le leaderboard
- Ajout du champ `rank` dans chaque ligne NDJSON
- Format unifié final : `rank` + `player_id` + `handle` + `top_weapons`

### Architecture Cible

```
┌─────────────────────────────────────────────┐
│   SCRIPT: extract_bf6_top_players.py        │
│                                             │
│   1. Récupère Top 100 du leaderboard       │
│   2. Pour chaque joueur :                   │
│      • Rank                                 │
│      • player_id (depuis URL profil)       │
│      • Handle                               │
│      • Total kills                          │
│      • Top 3 armes + kills                  │
│                                             │
│   Résultat : 1 fichier NDJSON unifié       │
└─────────────────────────────────────────────┘
                  ▼
┌─────────────────────────────────────────────┐
│   FICHIER: bf6_unified_2025-10-21.ndjson    │
│                                             │
│   • 100 lignes                              │
│   • Chaque ligne = 1 joueur complet         │
│   • Pas besoin de jointure                  │
└─────────────────────────────────────────────┘
                  ▼
┌─────────────────────────────────────────────┐
│   BIGQUERY: Table bronze_players            │
│                                             │
│   • rank (INT)                              │
│   • player_id (STRING) ← CLÉ PRIMAIRE       │
│   • handle (STRING)                         │
│   • total_kills (INT)                       │
│   • top_weapons (ARRAY<STRUCT>)             │
└─────────────────────────────────────────────┘
```

---

## 🔍 État Actuel du Projet

### ✅ Ce qui fonctionne
- Extraction des top weapons (100 joueurs) : `bf6_top_weapons_2025-10-20_200220.ndjson`
- Contient : `player_id`, `handle`, `top_weapons`

### ❌ Ce qui manque
- Le fichier leaderboard (`bf6_leaderboard_2025-10-18_174621.ndjson`) est un **ancien test**
- Il ne contient PAS de `player_id`
- Il n'est PAS synchronisé avec l'extraction des armes

---

## 📝 Plan d'Action Recommandé

### Option A : Continuer avec le fichier actuel (Phase 2)
**Si on veut avancer rapidement vers BigQuery** :
- Utiliser SEULEMENT `bf6_top_weapons_2025-10-20_200220.ndjson`
- Ignorer le fichier leaderboard (c'était juste un test)
- Avantage : Données cohérentes, pas de jointure

### Option B : Créer un fichier unifié (Amélioration Phase 0.5)
**Si on veut les données de rank** :
- Modifier `extract_bf6_top_weapons.py` pour ajouter le `rank`
- Ré-extraire 100 joueurs avec rank + armes
- Avantage : Données complètes

---

## 🎯 Décision Proposée

**OPTION A** : Utiliser le fichier actuel pour continuer

**Raison** :
1. Le fichier `bf6_top_weapons_2025-10-20_200220.ndjson` est complet :
   - 100 joueurs ✅
   - player_id ✅
   - handle ✅
   - top 3 armes ✅
   
2. Le rank n'est pas critique pour l'analyse des armes meta

3. On peut toujours ajouter le rank plus tard (amélioration)

**Prochaine étape** : Charger ce fichier dans BigQuery (Phase 2)

---

## 📊 Exemple Requête BigQuery (Sans Jointure)

```sql
-- Top 10 armes les plus populaires
WITH weapons_exploded AS (
  SELECT 
    player_id,
    handle,
    weapon.name AS weapon_name,
    weapon.kills AS weapon_kills
  FROM `bf6_meta.bronze_top_weapons`,
  UNNEST(top_weapons) AS weapon
)

SELECT 
  weapon_name,
  COUNT(DISTINCT player_id) AS players_using,
  SUM(weapon_kills) AS total_kills,
  AVG(weapon_kills) AS avg_kills_per_player
FROM weapons_exploded
GROUP BY weapon_name
ORDER BY players_using DESC, total_kills DESC
LIMIT 10;
```

**Résultat attendu** :
```
weapon_name | players_using | total_kills | avg_kills_per_player
------------|---------------|-------------|---------------------
L85A3       | 15            | 245,000     | 16,333
TR-7        | 12            | 198,000     | 16,500
M417 A2     | 11            | 175,000     | 15,909
...
```

---

## 💡 Résumé pour Ton Projet

### Fichiers Actuels
| Fichier | Date | Lignes | Clé | Statut |
|---------|------|--------|-----|--------|
| `bf6_leaderboard_2025-10-18_174621.ndjson` | 18 oct | 100 | ❌ Pas de player_id | ⚠️ Test ancien |
| `bf6_top_weapons_2025-10-20_200220.ndjson` | 20 oct | 100 | ✅ player_id | ✅ Production |

### Recommandation
✅ **Utiliser le fichier weapons (20 oct) pour la Phase 2**

### ✅ Amélioration Effectuée (21 oct)
- `rank` ajouté dans l'extraction ✅
- Format final atteint :
```json
{
  "rank": 1,                    # ✅ Position leaderboard
  "player_id": "2649085103",    # ✅ Clé unique
  "handle": "SKTelecomT1_Nova", # ✅ Pseudo
  "top_weapons": [              # ✅ Top 3 armes
    {"name": "L85A3", "kills": 31519},
    {"name": "NVO-228E", "kills": 17710},
    {"name": "AK-205", "kills": 17212}
  ]
}
```

**Prochaine extraction produira le format unifié complet !**

---

**🎯 Prochaine étape** : Charger `bf6_top_weapons_2025-10-20_200220.ndjson` dans BigQuery

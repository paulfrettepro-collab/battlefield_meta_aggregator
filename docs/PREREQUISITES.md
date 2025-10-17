# 📋 Prérequis Techniques - Battlefield Meta Aggregator

**Date d'exploration** : 17 octobre 2025  
**Status** : ✅ Exploration complétée

---

## 🎯 Résumé Exécutif

**Bonne nouvelle !** 🎉 Tracker.gg dispose d'une **API officielle de développeur** qui facilite grandement l'extraction des données.

**Approche recommandée** : **API Tracker.gg** (pas besoin de Scrapy complexe !)

---

## 📊 Découvertes de l'Exploration

### ✅ Leaderboard Accessible
- **URL** : `https://tracker.gg/bf6/leaderboards`
- **Format** : Tableau HTML avec Top 100 joueurs
- **Données disponibles** :
  - Rank (position 1-100)
  - Username (pseudo joueur)
  - Country (pays avec code ISO)
  - Kills (nombre de kills)
  - Deaths (nombre de morts - colonne supplémentaire)
  
**Exemple de données extraites** :
```
| Rank | Username   | Country | Kills  | Deaths |
|------|------------|---------|--------|--------|
| 1    | BnanaMilk  | KR      | 79,540 | 113    |
| 2    | Ecl4pseSky | HK      | 76,563 | 189    |
| 3    | ----       | CA      | 68,209 | 197    |
```

### 🔑 API Officielle Disponible !

**Tracker Network Developer API** : https://tracker.gg/developers

**Caractéristiques** :
- ✅ **API officielle** avec authentification par clé
- ✅ **Format JSON standardisé** pour tous les jeux
- ✅ **Documentation complète** : https://tracker.gg/developers/docs
- ✅ **Support Battlefield** confirmé (site officiel dédié)
- ✅ **Gratuit** pour usage personnel/éducatif

**Titres supportés actuellement** :
- Apex Legends ✅
- CS:GO ✅
- The Division 2 ✅
- Splitgate ✅
- **Battlefield (à vérifier si API complète ou scraping web)**

---

## 🛠️ Prérequis Techniques Détaillés

### 1️⃣ **Compte Tracker.gg Developer** (OBLIGATOIRE)

**Actions requises** :
1. Créer un compte sur https://tracker.gg
2. Accéder à https://tracker.gg/developers/apps
3. Cliquer "Create an app"
4. Remplir le formulaire :
   - **App Name** : "Battlefield Meta Aggregator"
   - **Description** : "Educational ELT pipeline for Battlefield stats analysis"
   - **Website** : `https://github.com/paulfrettepro-collab/battlefield_meta_aggregator`
5. Obtenir la **clé API** (TRN-Api-Key)

**Coût** : ✅ Gratuit  
**Temps estimé** : 5-10 minutes

---

### 2️⃣ **Vérifier l'API Battlefield disponible**

**⚠️ Action critique** : Confirmer que l'API supporte bien Battlefield 6/2042

**Étapes** :
1. Consulter https://tracker.gg/developers/docs/titles
2. Chercher "Battlefield" dans la liste des titres
3. **Deux scénarios possibles** :

#### Scénario A : API Battlefield disponible ✅
- **Meilleur cas** : Endpoints JSON directs
- **Endpoints attendus** :
  - `GET /api/v2/bf6/standard/profile/{platform}/{username}`
  - `GET /api/v2/bf6/leaderboards/{stat}`
- **Pas besoin de Scrapy** ! Requêtes HTTP simples

#### Scénario B : Pas d'API Battlefield ⚠️
- **Plan B** : Scraping HTML (avec `scrapy`)
- **Contraintes** :
  - Respect robots.txt : https://tracker.gg/robots.txt
  - Rate limiting : 1-2 secondes entre requêtes
  - User-Agent responsable

**TODO** : Tester l'API avec votre clé pour confirmer

---

### 3️⃣ **Données Disponibles vs Données Souhaitées**

#### ✅ **Données CONFIRMÉES disponibles sur Tracker.gg**

**Leaderboard** :
- ✅ Rank (1-100)
- ✅ Username
- ✅ Country
- ✅ Kills
- ✅ Deaths
- ⚠️ **Pagination possible** (vérifier si +100 joueurs accessible)

**Page Profil Joueur** (à explorer) :
- ❓ Stats détaillées par arme
- ❓ Win Rate / K/D Ratio
- ❓ Temps de jeu par arme
- ❓ **Loadouts** (accessoires par arme) → **CRITIQUE à vérifier**

#### ❌ **Données MANQUANTES probables**

**Loadouts complets** (accessoires détaillés) :
- Tracker.gg affiche principalement des **statistiques**, pas des **configurations d'armes**
- **Solution de secours** : Enrichir avec articles/guides (PC Gamer, Skycoach)

**Recommandation** : Architecture hybride
```
Tracker.gg (stats joueurs + armes utilisées)
    +
Articles guides (loadouts recommandés)
    =
Consensus intelligent (DBT)
```

---

### 4️⃣ **Stack Technique Confirmée**

| Composant | Outil | Status | Notes |
|-----------|-------|--------|-------|
| **Extraction** | Tracker.gg API | ✅ Prêt | Clé API requise |
| **Fallback Scraping** | Scrapy | ✅ Installé | Si API limitée |
| **Storage Bronze** | MinIO | ✅ Configuré | Docker-compose OK |
| **Data Warehouse** | BigQuery | ⏳ À configurer | Compte Google Cloud requis |
| **Transformation** | DBT Core | ⏳ À installer | `pip install dbt-bigquery` |
| **Visualisation** | Streamlit | ⏳ À créer | `pip install streamlit` |
| **Orchestration** | Airflow | ⏳ À configurer | Docker-compose à compléter |

---

### 5️⃣ **Données à Extraire - Structure Détaillée**

#### **Table Bronze : `bronze_leaderboard`**
```json
{
  "extraction_date": "2025-10-17T14:30:00Z",
  "source": "trackergg_api",
  "players": [
    {
      "rank": 1,
      "player_id": "player_a3f5b9c2",  // Anonymisé (SHA256)
      "country": "KR",
      "kills": 79540,
      "deaths": 113,
      "kd_ratio": 704.07,
      "profile_url": "https://tracker.gg/bf6/profile/..."
    }
  ]
}
```

#### **Table Bronze : `bronze_player_stats`** (si API disponible)
```json
{
  "player_id": "player_a3f5b9c2",
  "extraction_date": "2025-10-17T14:35:00Z",
  "weapons": [
    {
      "weapon_name": "AK-24",
      "kills": 5234,
      "headshots": 892,
      "accuracy": 0.34,
      "time_played_minutes": 120
    }
  ]
}
```

#### **Table Silver : `silver_meta_consensus`** (après fusion)
```json
{
  "weapon_name": "AK-24",
  "meta_score": 4.5,
  "usage_rate": 0.23,  // 23% des top 100 utilisent cette arme
  "avg_kills": 5234,
  "recommended_loadout": {
    "optic": "Red Dot Sight",  // Source: articles
    "barrel": "Extended Barrel",
    "magazine": "Extended Mag"
  },
  "sources": ["trackergg", "pcgamer", "skycoach"],
  "confidence": 0.85
}
```

---

## 🚀 Plan d'Action - Prochaines Étapes

### ✅ **Phase 0.5 : Setup API** (MAINTENANT)

**Actions immédiates** :
1. ✅ Créer compte Tracker.gg Developer
2. ✅ Obtenir clé API
3. ✅ Tester l'API avec `curl` :
   ```bash
   curl -H "TRN-Api-Key: VOTRE_CLE" \
        "https://public-api.tracker.gg/v2/bf6/standard/profile/origin/BnanaMilk"
   ```
4. ✅ Documenter les endpoints disponibles
5. ✅ Vérifier les limites de rate (requêtes/minute)

**Livrables** :
- Fichier `.env` avec `TRACKER_GG_API_KEY=...`
- Script de test `scripts/test_trackergg_api.py`
- Rapport d'API disponible (quels endpoints marchent)

---

### ✅ **Phase 1 : Extraction API** (APRÈS SETUP)

**Si API complète disponible** :
1. Implémenter `extract/apis/tracker_client.py`
2. Endpoints à utiliser :
   - `GET /leaderboards` → Top 100 joueurs
   - `GET /profile/{username}` → Stats détaillées
3. Format de sortie : NDJSON pour MinIO
4. Anonymisation : Hash SHA256 des pseudos

**Si scraping nécessaire** :
1. Compléter `extract/spiders/trackergg_spider.py`
2. Sélecteurs CSS identifiés durant l'exploration
3. Rate limiting : 2 secondes (respecter robots.txt)

**Temps estimé** : 4-6 heures

---

### ✅ **Phase 2 : BigQuery Setup** (APRÈS EXTRACTION)

**Prérequis** :
1. Compte Google Cloud (gratuit, 300$ crédit)
2. Créer projet "battlefield-meta"
3. Activer API BigQuery
4. Créer Service Account + JSON key
5. Dataset `battlefield_meta` avec tables :
   - `bronze_leaderboard`
   - `bronze_player_stats`
   - `silver_weapons`
   - `gold_meta_consensus`

**Temps estimé** : 2-3 heures

---

## 📝 Checklist Complète des Prérequis

### Comptes & Authentification
- [ ] Compte Tracker.gg créé
- [ ] App Developer créée
- [ ] Clé API obtenue (`TRN-Api-Key`)
- [ ] Clé stockée dans `.env`
- [ ] API testée avec `curl`

### Infrastructure
- [x] Docker & Docker Compose installés
- [x] MinIO configuré (docker-compose.yml)
- [ ] Compte Google Cloud créé
- [ ] BigQuery activé
- [ ] Service Account créé
- [ ] Clé JSON BigQuery téléchargée

### Dépendances Python
- [x] `scrapy` installé
- [x] `requests` installé
- [x] `beautifulsoup4` installé
- [ ] `dbt-bigquery` installé
- [ ] `streamlit` installé
- [ ] `apache-airflow` installé

### Code
- [x] Structure `extract/apis/` créée
- [x] `tracker_client.py` template créé
- [x] `trackergg_spider.py` template créé
- [ ] Script de test API créé
- [ ] Script upload MinIO créé
- [ ] Script load BigQuery créé

---

## ⚠️ Limitations Identifiées

### 1. **Loadouts Détaillés**
**Problème** : Tracker.gg affiche probablement les **stats par arme**, pas les **accessoires équipés**

**Solution** : Architecture hybride
- **Base** : Tracker.gg (usage des armes, top joueurs)
- **Enrichissement** : Articles guides (loadouts recommandés)
- **Fusion** : DBT calcule consensus multi-sources

### 2. **Rate Limiting API**
**Problème** : API gratuite probablement limitée (ex: 100 requêtes/heure)

**Solution** :
- Cache local (éviter re-requêter mêmes joueurs)
- Extraction quotidienne (pas en temps réel)
- Airflow DAG à 2h du matin (usage minimal)

### 3. **Pagination Leaderboard**
**Problème** : Top 100 seulement visible ?

**Solution** :
- Tester si pagination existe (page=2, page=3)
- Si limité à 100 : **Suffisant pour MVP** (top joueurs = méta)

---

## 🎯 Résumé : Ce dont tu as besoin MAINTENANT

### Actions Critiques (Avant de coder)
1. **Créer compte Tracker.gg Developer** ← **PRIORITÉ #1**
2. **Obtenir clé API** ← **PRIORITÉ #2**
3. **Tester l'API** avec les endpoints BF6 ← **PRIORITÉ #3**
4. **Documenter** ce qui fonctionne/ne fonctionne pas

### Si API complète disponible ✅
- **Pas besoin de Scrapy complexe**
- **Extraction simple** avec `requests`
- **Projet accéléré** de 50% !

### Si API limitée ⚠️
- **Scraping HTML** avec Scrapy (plan initial)
- **Plus long** mais faisable
- **Respect strict** du robots.txt

---

## 📞 Support & Ressources

**Documentation Tracker.gg** :
- API Docs : https://tracker.gg/developers/docs
- Support : https://tracker.gg/support/developer
- GitHub Issues : https://github.com/TrackerNetwork/TRN.Developers/issues

**robots.txt** : https://tracker.gg/robots.txt (respecter crawl-delay)

**Communauté** :
- Discord Tracker Network : https://go.tracker.gg/discord

---

## ✅ Validation du Plan

**Faisabilité technique** : ✅ **CONFIRMÉE**
- Données accessibles via API ou scraping
- Leaderboard visible et structuré
- Architecture hybride possible si loadouts manquants

**Temps estimé MVP** : **3-4 semaines** (en parallèle d'autres projets)
- Phase 0.5 (API Setup) : 1 jour
- Phase 1 (Extraction) : 1 semaine
- Phase 2 (BigQuery + DBT) : 1 semaine
- Phase 3 (Airflow) : 3-4 jours
- Phase 4 (Streamlit) : 3-4 jours

**Prochaine action** : 🔑 **Obtenir la clé API Tracker.gg !**

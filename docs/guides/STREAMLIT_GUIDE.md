# Guide Streamlit Dashboard - BF6 Meta Aggregator

## 📖 Table des Matières
1. [Introduction](#introduction)
2. [Architecture du Dashboard](#architecture-du-dashboard)
3. [Installation et Lancement](#installation-et-lancement)
4. [Structure du Code](#structure-du-code)
5. [Fonctionnalités MVP](#fonctionnalités-mvp)
6. [Connexion BigQuery](#connexion-bigquery)
7. [Système de Cache](#système-de-cache)
8. [Visualisations Plotly](#visualisations-plotly)
9. [Troubleshooting](#troubleshooting)
10. [Prochaines Étapes](#prochaines-étapes)

---

## Introduction

Le **BF6 Meta Dashboard** est une application web interactive construite avec **Streamlit** qui affiche les statistiques des armes de Battlefield 6 en temps réel.

### Pourquoi Streamlit ?

✅ **Rapide** : Dashboard fonctionnel en quelques heures  
✅ **Python pur** : Pas de HTML/CSS/JavaScript à écrire  
✅ **Interactif** : Boutons, filtres, graphiques natifs  
✅ **Gratuit** : Déployable gratuitement sur Streamlit Cloud  
✅ **Intégration BigQuery** : Cache intelligent des requêtes  

---

## Architecture du Dashboard

```
┌─────────────────────────────────────────────────────────┐
│                   STREAMLIT APP                          │
│  ┌───────────────────────────────────────────────────┐  │
│  │              app.py (Main Entry)                  │  │
│  │  - Header & Layout                                │  │
│  │  - Sidebar Controls                               │  │
│  │  - Key Metrics                                    │  │
│  │  - Charts & Tables                                │  │
│  └───────────────────────────────────────────────────┘  │
│                         │                                │
│         ┌───────────────┴───────────────┐                │
│         │                               │                │
│  ┌──────▼──────┐                ┌──────▼──────┐         │
│  │  bigquery.py │                │  charts.py  │         │
│  │  - Cached    │                │  - Plotly   │         │
│  │    queries   │                │    charts   │         │
│  │  - Data load │                │  - Formatters│        │
│  └──────┬──────┘                └─────────────┘         │
│         │                                                │
└─────────┼────────────────────────────────────────────────┘
          │
          ▼
   ┌──────────────┐
   │   BigQuery   │
   │  Gold Tables │
   └──────────────┘
```

---

## Installation et Lancement

### 1. Installer les dépendances

```bash
# Option A : Depuis le fichier dashboard/requirements.txt
pip install -r dashboard/requirements.txt

# Option B : Installation manuelle
pip install streamlit plotly pandas-gbq google-cloud-bigquery
```

### 2. Vérifier la configuration

**Prérequis** :
- ✅ BigQuery credentials : `config/bigquery-key.json`
- ✅ Tables Gold créées (via `dbt run`)
- ✅ Python 3.8+

### 3. Lancer le dashboard

```bash
# Depuis la racine du projet
streamlit run dashboard/app.py

# Ou avec le chemin complet
cd /Users/paulfrette/Github_pro_folder/battlefield_meta_aggregator
streamlit run dashboard/app.py
```

### 4. Ouvrir dans le navigateur

Streamlit ouvre automatiquement :
- **Local URL** : http://localhost:8501
- **Network URL** : http://192.168.X.X:8501 (partage sur le réseau)

---

## Structure du Code

```
dashboard/
├── app.py                     # 🏠 Application principale (300+ lignes)
├── utils/
│   ├── __init__.py           # Package initialization
│   ├── bigquery.py           # 🗄️ Connexion BigQuery + queries (150 lignes)
│   └── charts.py             # 📊 Visualisations Plotly (200 lignes)
├── requirements.txt           # Dépendances Python
└── README.md                  # Documentation technique
```

### Fichiers Créés (Phase 4)

| Fichier | Lignes | Rôle |
|---------|--------|------|
| `app.py` | 300+ | Interface utilisateur Streamlit |
| `utils/bigquery.py` | 150+ | Requêtes BigQuery cachées |
| `utils/charts.py` | 200+ | Graphiques Plotly réutilisables |
| `utils/__init__.py` | 40 | Imports du package |
| `requirements.txt` | 10 | Dépendances dashboard |
| `README.md` | 150+ | Documentation technique |

**Total** : ~850 lignes de code + documentation

---

## Fonctionnalités MVP

### ✅ Implémentées (Version 1.0)

#### 1. Header & Branding
- Titre principal avec emoji
- Sous-titre explicatif
- CSS custom pour le styling

#### 2. Sidebar
- **Bouton Refresh** : Force la mise à jour des données
- **Data Status** : Date de la dernière extraction
- **About** : Description du projet + lien GitHub

#### 3. Key Metrics (4 Cards)
- 🔫 Total Kills (Top 3 armes)
- 👥 Total Players
- 🎯 Avg Accuracy
- 💀 Avg Headshot %

#### 4. Top 3 Weapons Chart
- **Bar chart horizontal** (Plotly)
- Couleurs personnalisées par type d'arme
- Hover data : Accuracy, Player count

#### 5. Detailed Breakdown (2 Tabs)
- **Tab 1 : Table View**
  - Tableau formaté avec toutes les stats
  - Bouton "Download as CSV"
- **Tab 2 : Accuracy Analysis**
  - Scatter plot Accuracy vs Kills
  - Taille des bulles = nombre de joueurs
  - Insights textuels

#### 6. Weapon Cards (Top 3)
- 🥇🥈🥉 Badges de rang
- Métriques individuelles :
  - Total Kills
  - Players Using
  - Avg Accuracy
  - Avg Headshot %
  - Avg Damage

#### 7. Footer
- Crédits (Streamlit, DBT, BigQuery)
- Lien vers Tracker.gg

---

## Connexion BigQuery

### Fichier : `utils/bigquery.py`

#### Fonction 1 : `get_bigquery_client()`

**Rôle** : Créer un client BigQuery avec authentification

```python
@st.cache_resource
def get_bigquery_client():
    """Singleton cached BigQuery client"""
    credentials_path = Path(__file__).parent.parent.parent / "config" / "bigquery-key.json"
    return bigquery.Client.from_service_account_json(str(credentials_path))
```

**Cache** : `@st.cache_resource` 
- Cache **une seule fois** par session
- Ne recharge pas le client à chaque page refresh
- Économise les appels API

#### Fonction 2 : `load_top_weapons()`

**Rôle** : Charger les top 3 armes depuis Gold

```python
@st.cache_data(ttl=600)  # Cache 10 minutes
def load_top_weapons() -> pd.DataFrame:
    client = get_bigquery_client()
    
    query = """
        SELECT weapon_name, weapon_type, total_kills, avg_accuracy, 
               avg_headshot_pct, player_count
        FROM `battlefield-meta-aggregator.bf6_meta_gold.gold_top_weapons_global`
        ORDER BY total_kills DESC
    """
    
    return client.query(query).to_dataframe()
```

**Cache** : `@st.cache_data(ttl=600)`
- Cache pendant **10 minutes**
- Après 10 min → nouvelle requête BigQuery
- Paramètre `ttl` ajustable

#### Autres Fonctions

| Fonction | Requête | Table Source |
|----------|---------|--------------|
| `load_weapon_types_stats()` | Stats par type d'arme | `gold_weapon_type_rankings` |
| `load_player_rankings()` | Classement joueurs | `gold_player_rankings` |
| `load_player_weapons(handle)` | Armes d'un joueur | `silver_player_weapons` |
| `get_last_extraction_date()` | Date dernière extraction | `bf6_leaderboard_raw` |
| `clear_cache()` | Vide tous les caches | - |

---

## Système de Cache

### Pourquoi le cache ?

**Sans cache** :
- Chaque refresh = nouvelle requête BigQuery
- Temps de chargement : 2-3 secondes
- Coût : Requêtes BigQuery comptées dans le quota

**Avec cache** :
- Première requête : 2-3 secondes
- Requêtes suivantes : **instantané** (< 50ms)
- Coût : Une seule requête toutes les 10 minutes

### Types de Cache Streamlit

#### 1. `@st.cache_resource` (Singleton)
**Usage** : Connexions, clients, objets lourds

```python
@st.cache_resource
def get_database_connection():
    return create_connection()  # Appelé 1 seule fois
```

**Exemple** : BigQuery client, modèles ML, connexions Redis

#### 2. `@st.cache_data(ttl=600)` (Données)
**Usage** : Résultats de requêtes, DataFrames

```python
@st.cache_data(ttl=600)  # 10 minutes
def load_data():
    return pd.read_sql(query)  # Cache pendant 10 min
```

**Exemple** : Requêtes SQL, API calls, fichiers CSV

### Refresh Manuel

**Bouton dans la sidebar** :
```python
if st.button("🔄 Refresh Data"):
    clear_cache()  # Vide tous les caches
    st.rerun()     # Redémarre l'app
```

**Résultat** : Force une nouvelle requête BigQuery

---

## Visualisations Plotly

### Fichier : `utils/charts.py`

#### Chart 1 : `plot_top_weapons_bar()`

**Type** : Horizontal Bar Chart

```python
fig = px.bar(
    df,
    x='total_kills',
    y='weapon_name',
    orientation='h',
    color='weapon_type',
    color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1']
)
```

**Customisations** :
- Couleurs personnalisées (rouge, cyan, bleu)
- Hover data : Accuracy, Player count
- Grid vertical uniquement
- Background transparent

#### Chart 2 : `plot_accuracy_scatter()`

**Type** : Scatter Plot (Bulles)

```python
fig = px.scatter(
    df,
    x='avg_accuracy',
    y='total_kills',
    size='player_count',  # Taille des bulles
    color='weapon_type'
)
```

**Insights** :
- Position X = Accuracy
- Position Y = Kills
- Taille = Nombre de joueurs
- Couleur = Type d'arme

#### Formatters

```python
format_number(95881)           # → "95,881"
format_number(12345.67, 2)     # → "12,345.67"
format_percentage(0.235)       # → "23.5%"
format_percentage(0.1423, 2)   # → "14.23%"
```

---

## Troubleshooting

### Problème 1 : "BigQuery credentials not found"

**Symptôme** :
```
❌ BigQuery credentials not found at: /path/to/config/bigquery-key.json
```

**Solution** :
1. Vérifier que `config/bigquery-key.json` existe
2. Vérifier le chemin relatif dans `bigquery.py`
3. Tester : `ls config/bigquery-key.json`

### Problème 2 : "No data available"

**Symptôme** :
```
❌ No data available. Please check BigQuery connection.
```

**Causes possibles** :
1. Tables Gold vides → Lancer `dbt run`
2. Projet BigQuery incorrect → Vérifier le nom du projet
3. Credentials invalides → Re-générer le service account

**Debug** :
```bash
# Vérifier les tables dans BigQuery
bq ls bf6_meta_gold

# Compter les rows
bq query "SELECT COUNT(*) FROM bf6_meta_gold.gold_top_weapons_global"
```

### Problème 3 : Charts ne s'affichent pas

**Symptôme** : Page blanche ou erreur JavaScript

**Solutions** :
1. Vider cache navigateur : `Cmd+Shift+R` (Mac) / `Ctrl+Shift+R` (Windows)
2. Tester dans un autre navigateur (Chrome recommandé)
3. Vérifier la console JavaScript (F12) pour les erreurs

### Problème 4 : Lenteur au chargement

**Symptôme** : Plus de 5 secondes pour charger

**Optimisations** :
1. Augmenter le TTL du cache : `ttl=1800` (30 min)
2. Limiter les requêtes BigQuery (moins de colonnes)
3. Installer BigQuery Storage API :
   ```bash
   pip install google-cloud-bigquery-storage
   ```

### Problème 5 : Warning "use_container_width deprecated"

**Warning** :
```
Please replace `use_container_width` with `width`.
```

**Solution** : Remplacer dans `app.py`
```python
# AVANT
st.plotly_chart(fig, use_container_width=True)

# APRÈS
st.plotly_chart(fig, width="stretch")
```

---

## Prochaines Étapes

### Phase 4.1 : Pages Additionnelles

#### Page 2 : Weapon Types Comparison
**Fichier** : `dashboard/pages/1_📊_By_Type.py`

**Fonctionnalités** :
- Grouped bar chart : Kills/Damage/Accuracy par type
- Pie chart : Distribution des types
- Table agrégée par catégorie
- Filtre : Top N types

**Durée** : 1-2 heures

#### Page 3 : Player Profiles
**Fichier** : `dashboard/pages/2_👤_Players.py`

**Fonctionnalités** :
- Dropdown : Sélection du joueur (97 joueurs)
- Stats globales : Rank, Total Kills
- Top 3 armes du joueur
- Pie chart : Distribution des armes
- Comparaison vs moyenne mondiale

**Durée** : 2-3 heures

### Phase 4.2 : Fonctionnalités Avancées

- [ ] **Filtres** : Date range, Weapon type, Player tier
- [ ] **Historical Trends** : Week-over-week changes
- [ ] **Export** : PDF reports
- [ ] **Alertes** : Email si nouvelle arme dans top 3
- [ ] **Dark Mode** : Toggle theme

### Phase 4.3 : Déploiement

#### Option A : Streamlit Cloud (Gratuit)

**Étapes** :
1. Push code vers GitHub
2. Aller sur [streamlit.io](https://streamlit.io)
3. Connecter le repo
4. Ajouter `bigquery-key.json` dans **Secrets**
5. Deploy → URL publique

**Coût** : $0/mois (free tier)

#### Option B : Docker + Serveur Perso

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install -r dashboard/requirements.txt
CMD ["streamlit", "run", "dashboard/app.py"]
```

**Lancement** :
```bash
docker build -t bf6-dashboard .
docker run -p 8501:8501 bf6-dashboard
```

---

## Ressources

### Documentation Officielle
- [Streamlit Docs](https://docs.streamlit.io)
- [Plotly Python](https://plotly.com/python/)
- [BigQuery Client](https://cloud.google.com/python/docs/reference/bigquery/latest)

### Tutoriels
- [Streamlit Gallery](https://streamlit.io/gallery) : Exemples d'apps
- [Plotly Examples](https://plotly.com/python/) : Tous les types de charts
- [Streamlit Caching](https://docs.streamlit.io/develop/concepts/architecture/caching) : Guide complet

### Nos Guides
- `docs/BIGQUERY_GUIDE.md` : BigQuery setup
- `docs/DBT_BIGQUERY_EXPLAINED.md` : DBT + BigQuery workflow
- `dashboard/README.md` : Documentation technique dashboard

---

## Résumé des Commandes

```bash
# Installation
pip install streamlit plotly pandas-gbq google-cloud-bigquery

# Lancement local
streamlit run dashboard/app.py

# Tests
pytest dashboard/tests/  # (à créer)

# Déploiement
streamlit cloud deploy  # Après setup Streamlit Cloud

# Debug
streamlit cache clear  # Vider le cache
```

---

**Créé le** : 25 octobre 2025  
**Auteur** : AI Assistant  
**Version** : 1.0 (MVP)  
**Dernière mise à jour** : 25 octobre 2025

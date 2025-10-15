# 📊 Dashboard - Streamlit

**Rôle** : Visualiser les analyses du méta Battlefield

## 🎯 Qu'est-ce que c'est ?

Application web Streamlit qui affiche :
- 🏆 **Top 10 armes** par score méta
- 📈 **Évolution du méta** dans le temps
- 🔫 **Meilleurs loadouts** par arme
- 📊 **Statistiques par source** (PC Gamer, Reddit, etc.)

## 📁 Structure

```
dashboard/
├── app.py                 # Application principale
├── pages/
│   ├── 1_Top_Weapons.py   # Page Top armes
│   ├── 2_Evolution.py     # Page Évolution méta
│   └── 3_Loadouts.py      # Page Loadouts détaillés
└── .streamlit/
    └── config.toml        # Configuration Streamlit
```

## 🚀 Lancement local

```bash
# Installer Streamlit
pip install streamlit

# Lancer l'application
streamlit run dashboard/app.py

# Ouvrir dans le navigateur
# Automatiquement : http://localhost:8501
```

## 📊 Pages prévues

### Page 1 : Top Weapons
```python
# Affiche un tableau interactif
# avec filtres par date et source
st.dataframe(top_weapons)
st.bar_chart(weapon_scores)
```

### Page 2 : Meta Evolution
```python
# Graphique ligne de l'évolution
# des scores dans le temps
st.line_chart(meta_evolution)
```

### Page 3 : Loadouts
```python
# Détails des loadouts recommandés
# par arme avec vote communauté
st.selectbox("Choisir une arme", weapons)
st.write(f"Meilleur loadout : {loadout}")
```

## 🔌 Connexion BigQuery

**Dans `app.py`** :
```python
from google.cloud import bigquery

# Connexion BigQuery
client = bigquery.Client()

# Query des données Gold
query = """
SELECT * FROM battlefield_meta.gold_top_weapons
ORDER BY avg_score DESC
LIMIT 10
"""

# Affichage dans Streamlit
df = client.query(query).to_dataframe()
st.dataframe(df)
```

## 🎨 Features

- ✅ **Rafraîchissement automatique** (toutes les heures)
- ✅ **Filtres interactifs** (date, source, arme)
- ✅ **Graphiques dynamiques** (plotly, altair)
- ✅ **Export PDF** (des rapports)
- ✅ **Mode sombre** (pour les gamers 😎)

## 🚀 Déploiement gratuit

**Streamlit Cloud** (hébergement gratuit) :

1. Push ton code sur GitHub
2. Va sur https://streamlit.io/cloud
3. Connecte ton repo
4. Deploy en 1 clic
5. ✅ Ton dashboard est en ligne !

**URL publique** : `https://battlefield-meta.streamlit.app`

## 🔗 Workflow

```
BigQuery (Gold)  →  Streamlit  →  Utilisateur
─────────────       ─────────      ──────────
Top armes           Graphiques     Dashboard web
Évolution méta      Tableaux       Analyse visuelle
Statistiques        Filtres        Insights
```

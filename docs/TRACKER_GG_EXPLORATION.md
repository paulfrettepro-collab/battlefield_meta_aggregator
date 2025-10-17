# 🔍 Guide d'Exploration Tracker.gg Battlefield 2042

**Objectif** : Identifier précisément comment extraire les données du leaderboard et des loadouts

---

## 📋 Checklist d'Exploration

### ✅ Étape 1 : Analyser le Leaderboard

**URL cible** : https://tracker.gg/battlefield-2042/leaderboards/stats/all/default

1. **Ouvrir la page dans le navigateur**
2. **Ouvrir DevTools** (F12 ou Cmd+Option+I sur Mac)
3. **Onglet Network > XHR** : Vérifier si un endpoint JSON charge les données
   - ✅ **Si JSON trouvé** : Copier l'URL, analyser la structure → API directe possible !
   - ❌ **Si pas de JSON** : Utiliser Scrapy avec sélecteurs CSS/XPath
4. **Onglet Elements** : Inspecter le tableau HTML
   - Identifier la classe CSS du conteneur (ex: `div.leaderboard-table`)
   - Identifier les lignes du tableau (ex: `tr.player-row`)
   - Identifier les colonnes :
     - **Rank** : sélecteur ? (ex: `td.rank span::text`)
     - **Username** : sélecteur ? (ex: `td.username a::text`)
     - **Profile URL** : sélecteur ? (ex: `td.username a::attr(href)`)
     - **Platform** : PC/Xbox/PlayStation (badge ou attribut ?)
     - **Stats** : Kills, Deaths, Win Rate, etc.

**Résultat attendu** :
```python
# Exemple de sélecteurs à documenter ici après exploration
LEADERBOARD_SELECTORS = {
    'player_row': 'div.trn-table__row',  # À ADAPTER
    'rank': '.rank::text',  # À ADAPTER
    'username': '.player-name::text',  # À ADAPTER
    'profile_url': 'a.player-link::attr(href)',  # À ADAPTER
}
```

---

### ✅ Étape 2 : Analyser une Page Profil Joueur

**URL cible** : Cliquer sur un joueur du leaderboard → Noter l'URL du profil

Exemple probable : `https://tracker.gg/battlefield-2042/profile/{platform}/{username}`

1. **Network > XHR** : Chercher un endpoint JSON pour les stats/loadouts
2. **Elements** : Inspecter la structure HTML
   - Où sont affichées les **armes utilisées** ?
   - Y a-t-il un onglet "Loadouts" ou "Weapons" ?
   - Structure des **accessoires** : optic, barrel, magazine, etc. ?

**Questions clés** :
- ❓ Le site affiche-t-il les loadouts **complets** (arme + accessoires) ?
- ❓ Ou seulement les **stats par arme** (kills, accuracy, usage %) ?
- ❓ Si pas de loadouts détaillés → **Besoin de sources complémentaires** (GameTools, articles)

**Résultat attendu** :
```python
# Exemple de structure de données à documenter
PLAYER_PROFILE_SELECTORS = {
    'weapon_card': 'section.weapon-stats',  # À ADAPTER
    'weapon_name': '.weapon-title::text',  # À ADAPTER
    'weapon_stats': {
        'kills': '.stat-kills::text',
        'accuracy': '.stat-accuracy::text',
    },
    # Si loadouts disponibles :
    'attachments': {
        'optic': '.attachment-optic::text',
        'barrel': '.attachment-barrel::text',
        # etc.
    }
}
```

---

### ✅ Étape 3 : Vérifier robots.txt

**URL** : https://tracker.gg/robots.txt

1. Vérifier si le scraping est **autorisé**
2. Identifier le **crawl delay** requis
3. Respecter les règles (ou chercher une API officielle)

**Exemple** :
```
User-agent: *
Disallow: /api/
Crawl-delay: 2
```

→ **Conclusion** : Rate limit de 2 secondes entre requêtes obligatoire

---

### ✅ Étape 4 : Tester avec Scrapy Shell

**Commande** :
```bash
scrapy shell "https://tracker.gg/battlefield-2042/leaderboards/stats/all/default?page=1"
```

**Tests à faire** :
```python
# Test 1 : Extraire les lignes du leaderboard
response.css('div.player-row')  # Adapter le sélecteur

# Test 2 : Extraire un username
response.css('.username::text').get()

# Test 3 : Extraire un lien profil
response.css('a.player-link::attr(href)').get()

# Test 4 : Compter le nombre de joueurs sur la page
len(response.css('div.player-row'))
```

---

## 📊 Résultat de l'Exploration

### 🔍 Découvertes (à remplir après exploration)

#### Leaderboard
- **URL** : 
- **Méthode** : [ ] JSON API | [ ] Scraping HTML
- **Endpoint JSON (si trouvé)** : 
- **Pagination** : [ ] Oui | [ ] Non (combien de pages ?)
- **Sélecteurs CSS** :
  ```python
  # À compléter
  ```

#### Profil Joueur
- **URL pattern** : 
- **Loadouts affichés** : [ ] Oui (complets) | [ ] Partiel | [ ] Non
- **Endpoint JSON (si trouvé)** : 
- **Sélecteurs CSS** :
  ```python
  # À compléter
  ```

#### Contraintes Techniques
- **robots.txt** : [ ] Autorisé | [ ] Interdit
- **Rate limit** : ___ secondes
- **Authentification requise** : [ ] Oui | [ ] Non
- **Captcha** : [ ] Oui | [ ] Non

---

## 🚀 Plan d'Action Après Exploration

### Scénario 1 : API JSON disponible ✅
**Meilleur cas** : Tracker.gg expose un endpoint JSON public

**Actions** :
1. Documenter l'endpoint dans `tracker_client.py`
2. Implémenter des requêtes HTTP directes (pas besoin de Scrapy)
3. Parser le JSON → Format NDJSON pour MinIO

**Avantages** : Rapide, stable, légal

---

### Scénario 2 : Scraping HTML nécessaire ⚠️
**Si pas d'API** : Utiliser Scrapy avec sélecteurs CSS/XPath

**Actions** :
1. Compléter `trackergg_spider.py` avec les sélecteurs découverts
2. Tester avec `scrapy crawl trackergg -o test.json`
3. Valider l'extraction sur 10 joueurs
4. Ajuster le rate limiting (respecter robots.txt)

**Contraintes** : Plus fragile (structure HTML peut changer)

---

### Scénario 3 : Loadouts incomplets sur Tracker.gg 🔴
**Si le site ne montre pas les loadouts détaillés** :

**Plan B** : Enrichir avec sources complémentaires
1. **GameTools API** : Vérifier si elle expose les loadouts
2. **Articles guides** : PC Gamer, Skycoach (scraping + LLM)
3. **Fusion DBT** : Croiser stats Tracker.gg + loadouts articles

**Architecture** :
```
Tracker.gg (stats armes) 
    +
GameTools/Articles (loadouts détaillés)
    =
BigQuery Silver (fusion intelligente)
```

---

## 🛠️ Outils d'Exploration

### Browser DevTools
```
1. Network > XHR : Endpoints JSON
2. Elements > Inspect : Sélecteurs CSS
3. Console : Tests jQuery/CSS
```

### Scrapy Shell
```bash
# Tester les sélecteurs en live
scrapy shell "URL"
response.css('selector').getall()
```

### Extensions Navigateur
- **SelectorGadget** : Identifier sélecteurs CSS facilement
- **EditThisCookie** : Gérer cookies/sessions si besoin

---

## 📝 Template de Rapport d'Exploration

Copier ce template et le remplir après exploration :

```markdown
# Rapport d'Exploration Tracker.gg - [DATE]

## Leaderboard
- URL : 
- Méthode : API JSON / Scraping HTML
- Endpoint JSON : 
- Sélecteurs CSS :
  - player_row: 
  - rank: 
  - username: 
  - profile_url: 

## Profil Joueur
- URL : 
- Loadouts disponibles : Oui / Non / Partiel
- Détails : 

## Conclusion
- ✅ Faisable avec : API / Scrapy / Mixte
- ⚠️ Limitations : 
- 📋 Prochaines étapes : 
```

---

## 🎯 Objectif Final

**Après cette exploration, on aura** :
- ✅ Sélecteurs CSS/XPath précis pour Scrapy
- ✅ Ou endpoints JSON pour API directe
- ✅ Validation de la faisabilité technique
- ✅ Plan d'implémentation clair

**Ensuite** : Implémenter le spider/client et passer à MinIO → BigQuery !

# 🔍 EXPLORATION DES SOURCES - Battlefield Meta

**Phase 0.5 : Recherche et analyse avant développement**

---

## 🎯 Objectif de cette phase

**AVANT** de coder, tu dois :
1. ✅ Identifier **toutes** les sources potentielles de données Battlefield
2. ✅ Vérifier si elles ont des **APIs ouvertes** (priorité #1)
3. ✅ Analyser la **qualité et structure** des données
4. ✅ Choisir les **5 meilleures sources** (mix API + Scraping)
5. ✅ Documenter tes findings dans un tableau comparatif

**Pourquoi ?** 
- 🚀 Les APIs sont **10x plus rapides** que le scraping
- 🛡️ Les APIs sont **légales et stables** (pas de risque de ban)
- 📊 Les APIs fournissent des **données structurées** (JSON propre)
- ⚡ Moins de code à écrire et maintenir

---

## 📋 CHECKLIST D'EXPLORATION

### Étape 1 : Recherche initiale (1 jour)

Pour chaque site potentiel, réponds à ces questions :

```
[ ] Nom du site : ________________
[ ] URL : ________________
[ ] Type de contenu : (Tier list / Guide loadouts / Stats / News)
[ ] A une API ? (Oui / Non / À vérifier)
[ ] Si non, crawlable avec Scrapy ? (Facile / Moyen / Difficile)
[ ] Qualité des données : (★★★★★)
[ ] Fréquence de mise à jour : (Quotidienne / Hebdomadaire / Mensuelle)
[ ] Notes spéciales : ________________
```

### Étape 2 : Test API (si disponible)

```bash
# Exemple de test API simple
curl -X GET "https://api.example.com/battlefield/weapons" \
  -H "Accept: application/json"

# Sauvegarder la réponse
curl "https://api.example.com/battlefield/weapons" > test_api_response.json
```

**Questions à se poser** :
- ✅ L'API nécessite-t-elle une clé ? (Gratuite ou payante ?)
- ✅ Quelle est la limite de requêtes ? (rate limit)
- ✅ La documentation est-elle claire ?
- ✅ Les données sont-elles à jour ?

### Étape 3 : Test Scraping (si pas d'API)

```bash
# Crawler la page avec Scrapy shell
scrapy shell "https://example.com/battlefield-meta"

# Tester les sélecteurs CSS
response.css('h2.weapon-name::text').getall()
response.css('div.loadout span::text').getall()
```

**Questions à se poser** :
- ✅ Le HTML est-il bien structuré ?
- ✅ Y a-t-il du JavaScript dynamique ? (nécessite Playwright)
- ✅ Le site bloque-t-il les bots ? (User-Agent, Cloudflare)
- ✅ Quelle est la fréquence acceptable de crawl ?

---

## 🗂️ TABLEAU COMPARATIF DES SOURCES

**Instructions** : Remplis ce tableau au fur et à mesure de ton exploration

| # | Source | Type | API ? | Crawlable ? | Qualité | Fréquence MàJ | Priorité | Notes |
|---|--------|------|-------|-------------|---------|---------------|----------|-------|
| 1 | **PC Gamer** | Guide loadouts | ❌ Non | ✅ Facile | ⭐⭐⭐⭐ | Hebdo | 🟢 HIGH | Spider déjà fait |
| 2 | **WZStats** | Stats armes | ❌ Non | ✅ Facile | ⭐⭐⭐⭐⭐ | Quotidien | 🟢 HIGH | Spider déjà fait |
| 3 | Reddit r/Battlefield6 | Discussions | ⚠️ API Reddit | ✅ Moyen | ⭐⭐⭐ | Temps réel | 🟡 MEDIUM | API officielle disponible |
| 4 | Skycoach | Tier lists | ❓ À vérifier | ❓ À tester | ❓ | ❓ | ⚪ TODO | |
| 5 | Gam3s.gg | Meta analysis | ❓ À vérifier | ❓ À tester | ❓ | ❓ | ⚪ TODO | |
| 6 | Beebom | News/Guides | ❓ À vérifier | ❓ À tester | ❓ | ❓ | ⚪ TODO | |
| 7 | **EA/DICE API ?** | Stats officielles | ⚠️ À chercher | N/A | ⭐⭐⭐⭐⭐ | Temps réel | 🔴 CRITICAL | **API officielle Battlefield ?** |
| 8 | Tracker.gg | Stats joueurs | ⚠️ API possible | ✅ Facile | ⭐⭐⭐⭐ | Temps réel | 🟢 HIGH | Vérifie API publique |
| 9 | BattleLog | Stats/Loadouts | ⚠️ API possible | ✅ Moyen | ⭐⭐⭐⭐⭐ | Temps réel | 🔴 CRITICAL | **API EA/DICE ?** |
| 10 | YouTube (Chaînes pros) | Meta reviews | ❌ Non (API YouTube) | ⚠️ Difficile | ⭐⭐⭐ | Variable | 🟡 MEDIUM | Transcription vidéos ? |

**Légende priorités** :
- 🔴 **CRITICAL** : API officielle ou source ultra-fiable
- 🟢 **HIGH** : Données de qualité, facile à implémenter
- 🟡 **MEDIUM** : Bon complément mais pas essentiel
- ⚪ **TODO** : À explorer

---

## 🔥 SOURCES PRIORITAIRES À EXPLORER

### 1. 🎮 API Officielle EA/DICE (PRIORITÉ #1)

**Pourquoi c'est critique** :
- Source officielle = données 100% fiables
- Stats en temps réel
- Pas de scraping = légal et rapide

**Recherches à faire** :
```
[ ] Chercher "Battlefield API documentation"
[ ] Chercher "EA API developer portal"
[ ] Chercher "DICE Battlefield stats API"
[ ] Vérifier https://www.ea.com/games/battlefield/api (si existe)
[ ] Checker forums développeurs EA
```

**Alternatives** :
- BattleLog API (ancienne mais peut-être active)
- EA Companion App API (reverse engineering)
- Community APIs (ex: BF2042 API par des fans)

### 2. 🔥 Tracker.gg / Tracker Network

**URL** : https://tracker.gg/battlefield-2042

**À vérifier** :
```
[ ] Inspecter Network tab (DevTools) → Chercher appels API
[ ] Chercher "tracker.gg API key" sur Google
[ ] Vérifier https://tracker.gg/developers (si existe)
[ ] Tester GraphQL endpoint (souvent utilisé par Tracker)
```

**Exemple de test** :
```javascript
// Ouvre DevTools → Network → Reload la page
// Cherche des requêtes vers api.tracker.gg
// Exemple trouvé : 
// GET https://api.tracker.gg/api/v2/bf2042/standard/profile/...
```

### 3. 📱 Reddit API (OFFICIELLE)

**URL** : https://www.reddit.com/dev/api/

**Avantages** :
- ✅ API officielle gratuite
- ✅ Documentation complète
- ✅ Bibliothèque Python `praw` (simple à utiliser)

**Code de test** :
```python
import praw

reddit = praw.Reddit(
    client_id="TON_CLIENT_ID",
    client_secret="TON_SECRET",
    user_agent="BattlefieldMetaBot 1.0"
)

# Récupérer top posts r/Battlefield6
for post in reddit.subreddit("Battlefield6").hot(limit=10):
    print(f"{post.title} - {post.score} upvotes")
```

**À faire** :
```
[ ] Créer une app Reddit : https://www.reddit.com/prefs/apps
[ ] Installer praw : pip install praw
[ ] Tester extraction de posts meta/loadouts
```

### 4. 🎥 YouTube Data API (Complémentaire)

**URL** : https://developers.google.com/youtube/v3

**Cas d'usage** :
- Analyser vidéos de pros (Stodeh, JackFrags, etc.)
- Extraction de transcriptions (mentions d'armes)
- Statistiques de popularité des loadouts

**Limites** :
- ⚠️ Quota gratuit limité (10,000 unités/jour)
- ⚠️ Nécessite NLP pour analyser transcriptions

---

## 🛠️ OUTILS D'EXPLORATION

### 1. Inspecter les APIs cachées (DevTools)

```bash
# Étapes :
1. Ouvre le site web (ex: tracker.gg/battlefield)
2. DevTools (F12) → Onglet "Network"
3. Filtre "XHR" ou "Fetch"
4. Recharge la page
5. Cherche des requêtes vers des endpoints API
   → Exemples : api.*, graphql, /v1/, /v2/

# Copie l'URL de la requête
# Teste dans le terminal :
curl "URL_COPIÉE" -H "User-Agent: Mozilla/5.0"
```

### 2. Scrapy Shell (Test rapide de scraping)

```bash
# Tester un site en 30 secondes
scrapy shell "https://example.com/battlefield-meta"

# Dans le shell :
>>> response.css('h2::text').getall()
>>> response.css('div.weapon-stats').get()
>>> response.xpath('//span[@class="score"]/text()').getall()
```

### 3. Postman / Insomnia (Test d'APIs)

- Importe des collections d'APIs
- Teste différents endpoints
- Génère du code Python automatiquement

---

## 📊 CRITÈRES DE SÉLECTION

Pour choisir tes 5 sources finales, note chaque critère sur 5 :

| Critère | Poids | Description |
|---------|-------|-------------|
| **Qualité données** | ×3 | Fiabilité, précision, structure |
| **API disponible** | ×2 | API > Scraping (stabilité) |
| **Fréquence MàJ** | ×2 | Quotidien > Hebdo > Mensuel |
| **Facilité implémentation** | ×1 | Temps de dev estimé |
| **Légalité** | ×3 | Respect des ToS, rate limits |

**Calcul du score** :
```
Score total = (Qualité×3) + (API×2) + (Fréquence×2) + (Facilité×1) + (Légalité×3)
Max possible = 55 points
```

**Exemple** :
```
EA API Officielle :
- Qualité : 5 × 3 = 15
- API : 5 × 2 = 10
- Fréquence : 5 × 2 = 10
- Facilité : 4 × 1 = 4
- Légalité : 5 × 3 = 15
──────────────────────
Total : 54/55 points → 🔴 PRIORITÉ ABSOLUE
```

---

## 📝 TEMPLATE DE RECHERCHE PAR SOURCE

Copie-colle ce template pour chaque source explorée :

```markdown
### Source : [NOM DU SITE]

**URL** : https://...

#### 1. Type de contenu
- [ ] Tier lists
- [ ] Guides loadouts
- [ ] Stats armes
- [ ] News/Patchnotes
- [ ] Discussions communauté

#### 2. API Investigation
- API trouvée ? **[Oui/Non]**
- URL de l'API : ________________
- Documentation : ________________
- Authentification requise ? **[Oui/Non]**
- Rate limit : ________________
- Coût : **[Gratuit/Payant]**

#### 3. Scraping Investigation (si pas d'API)
- HTML structuré ? **[Oui/Non]**
- JavaScript dynamique ? **[Oui/Non]**
- Anti-bot protection ? **[Oui/Non]**
- Sélecteurs CSS testés :
  ```python
  # Armes
  response.css('...').getall()
  
  # Loadouts
  response.css('...').getall()
  
  # Scores
  response.css('...').getall()
  ```

#### 4. Exemple de données
```json
{
  "weapon": "...",
  "attachments": ["...", "..."],
  "meta_score": 0.0,
  "source": "...",
  "date": "..."
}
```

#### 5. Décision finale
- **Score** : __/55 points
- **Priorité** : 🔴 CRITICAL / 🟢 HIGH / 🟡 MEDIUM / ⚪ LOW
- **Implémentation** : API / Scrapy / Hybride / ❌ Skip
- **Notes** : ________________
```

---

## 🎯 LIVRABLE DE CETTE PHASE

À la fin de ton exploration (2-3 jours), tu dois avoir :

### 1. Document complété
- ✅ Tableau comparatif rempli (10+ sources analysées)
- ✅ 5 sources finales choisies avec scores
- ✅ Templates de recherche complétés

### 2. Fichiers de test
```
/data/exploration/
├── test_api_ea.json           # Réponse API EA (si trouvée)
├── test_api_tracker.json      # Réponse Tracker.gg
├── test_api_reddit.json       # Posts Reddit extraits
├── test_scraping_skycoach.html # Page HTML sauvegardée
└── findings_summary.md        # Résumé de tes découvertes
```

### 3. Plan d'implémentation
```markdown
## Sources sélectionnées (5 max)

1. **EA API** (si trouvée) → Priorité #1
   - Implémentation : Python requests
   - Temps estimé : 2 heures
   
2. **Tracker.gg API** → Priorité #2
   - Implémentation : GraphQL client
   - Temps estimé : 3 heures
   
3. **Reddit API** → Priorité #3
   - Implémentation : praw library
   - Temps estimé : 2 heures
   
4. **PC Gamer** (scraping) → Priorité #4
   - Implémentation : Scrapy (déjà fait ✅)
   - Temps estimé : 0 heure
   
5. **WZStats** (scraping) → Priorité #5
   - Implémentation : Scrapy (déjà fait ✅)
   - Temps estimé : 0 heure
```

---

## 🚀 PROCHAINES ÉTAPES (APRÈS EXPLORATION)

Une fois cette phase terminée :

1. **Créer `/extract/apis/`** pour les clients API
2. **Modifier `/extract/spiders/`** pour ne garder que le scraping nécessaire
3. **Mettre à jour `requirements.txt`** avec nouvelles dépendances (praw, etc.)
4. **Créer `scripts/test_all_sources.py`** pour valider toutes les sources

---

## 💡 CONSEILS

### ✅ DO
- ✅ Commence par chercher l'API officielle EA/DICE (PRIORITÉ)
- ✅ Teste toutes les APIs trouvées avec `curl` ou Postman
- ✅ Documente TOUT (même les échecs)
- ✅ Privilégie TOUJOURS l'API au scraping
- ✅ Vérifie les Terms of Service (ToS) de chaque site

### ❌ DON'T
- ❌ Ne code RIEN avant d'avoir exploré
- ❌ Ne te lance pas dans Scrapy si une API existe
- ❌ Ne choisis pas une source juste parce qu'elle est populaire
- ❌ N'ignore pas les rate limits (risque de ban)

---

## 📚 Ressources utiles

- **Chercher des APIs** : https://rapidapi.com/search/battlefield
- **Reddit API Docs** : https://www.reddit.com/dev/api/
- **YouTube API Docs** : https://developers.google.com/youtube/v3
- **DevTools Chrome** : https://developer.chrome.com/docs/devtools/network/
- **Scrapy Shell** : https://docs.scrapy.org/en/latest/topics/shell.html

---

**🎯 OBJECTIF : Privilégier les APIs (rapide, légal, stable) avant le scraping !**

Bon courage pour ton exploration ! 🔍🎮

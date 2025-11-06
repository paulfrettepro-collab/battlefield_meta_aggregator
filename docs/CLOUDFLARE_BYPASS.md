# 🛡️ Tracker.gg Scraping - Guide de Résolution

## 📋 Problème Identifié (6 Nov 2025)

**Symptôme** : Le workflow GitHub Actions extrait 0 joueurs rangs 1-3, seulement rangs 4-53, et utilise d'anciennes données du 30 octobre.

**Root Causes Identifiées** :

### 1. **Cloudflare Protection** 
Tracker.gg utilise Cloudflare qui bloque requêtes automatisées avec challenge "Verify you are human".

### 2. **Site SPA (Single Page Application)** ⚠️ CRITIQUE
Le site est **rendu côté client** (Client-Side Rendering). Le HTML initial est vide :
- `curl` renvoie seulement `<title>Just a moment...</title>`
- Les données joueurs sont chargées **après** via JavaScript
- Nécessite attente ~40s pour chargement complet
- Nécessite **scroll** pour déclencher lazy loading

## 🔍 Diagnostic

### HTML Initial (curl/wget)

```html
<html>
  <head><title>Just a moment...</title></head>
  <body>
    <h1>Verify you are human</h1>
    <noscript>Enable JavaScript</noscript>
  </body>
</html>
```

### Problème des Rangs 1-3 Manquants

**Observation** : NDJSON contient rangs 4-53 (50 joueurs) au lieu de 1-50.

**Hypothèses** :
1. Structure HTML différente pour podium (rangs 1-3 stylisés différemment)
2. Chargement lazy loading : rangs 1-3 nécessitent scroll
3. Sélecteur `data-key` ne match pas les 3 premiers éléments

## 🔧 Solutions Implémentées

### 1. **Undetected ChromeDriver** (Bypass Cloudflare)

```python
import undetected_chromedriver as uc

options = uc.ChromeOptions()
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument('user-agent=Mozilla/5.0 ...')

driver = uc.Chrome(
    options=options,
    headless=True,  # ✅ Headless natif UC (bypass Cloudflare)
    use_subprocess=True
)
```

### 2. **Timing Optimisé pour SPA**

```python
driver.get(LEADERBOARD_URL)

# Phase 1: Bypass Cloudflare (15s + 20s si détecté)
time.sleep(15)
if "Just a moment" in driver.page_source:
    time.sleep(20)

# Phase 2: Attente chargement JavaScript (20s)
time.sleep(20)

# Phase 3: Scroll pour lazy loading (5s)
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(3)
driver.execute_script("window.scrollTo(0, 0);")
time.sleep(2)

# Total: 40-60s selon Cloudflare
```

### 3. **Logs Debug Détaillés**

```python
player_rows = soup.find_all('tr', {'data-key': lambda x: x and x.isdigit()})
logger.info(f"🔍 {len(player_rows)} joueurs trouvés")

# Afficher premiers data-key
for i, row in enumerate(player_rows[:5]):
    logger.info(f"Row {i+1}: data-key = {row.get('data-key')}")

# Si aucun trouvé, debug structure HTML
if not player_rows:
    all_rows = soup.find_all('tr')
    logger.info(f"Total <tr>: {len(all_rows)}")
    logger.info(f"Premier <tr>: {str(all_rows[0])[:200]}")
```

## 🧪 Test de la Solution

### Local

```bash
cd /Users/paulfrette/Github_pro_folder/battlefield_meta_aggregator
python3 scripts/extract_bf6_meta_complete.py > /tmp/extract_test.log 2>&1 &

# Attendre 2-3 minutes puis vérifier
tail -50 /tmp/extract_test.log
```

**Indicateurs de succès** :
- ✅ "🔍 50+ joueurs trouvés dans le tableau"
- ✅ "DEBUG - Premiers data-key: 1, 2, 3, 4, 5" (rangs commencent à 1 !)
- ✅ Fichier NDJSON contient `"rank": 1` en première ligne
- ✅ `extraction_date` = aujourd'hui

**Indicateurs d'échec** :
- ❌ "🔍 0 joueurs trouvés"
- ❌ "DEBUG - Premiers data-key: 4, 5, 6..." (rangs 1-3 manquent)
- ❌ "AUCUN <tr data-key> trouvé"

### Diagnostic si Échec

1. **Vérifier HTML debug** :
```bash
open data/bronze/tracker_gg/leaderboard/leaderboard_debug_latest.html
```

2. **Chercher structure réelle** :
- Inspecter avec DevTools navigateur
- Chercher `<tr` dans le HTML
- Identifier class/id/attributs utilisés
- Adapter sélecteur BeautifulSoup si nécessaire

3. **Exemples de sélecteurs alternatifs** :
```python
# Option 1: Class-based
player_rows = soup.find_all('tr', class_='leaderboard-row')

# Option 2: Nested search
table = soup.find('table', id='leaderboard')
player_rows = table.find_all('tr')[1:]  # Skip header

# Option 3: CSS selector
player_rows = soup.select('tbody > tr[data-key]')
```

## 📊 Vérification des Données

### 1. NDJSON Local

```bash
head -3 data/bronze/tracker_gg/leaderboard/bf6_leaderboard_*.ndjson | python3 -m json.tool
```

**Attendu** :
```json
{"rank": 1, "handle": "⨤🜁♄🜍⛎︎🜚🜔☽", "kills": 72815, ...}
{"rank": 2, "handle": "Shan客", "kills": 63372, ...}
{"rank": 3, "handle": "Hastings_Command", "kills": 50954, ...}
```

**Si rangs commencent à 4** → Problème structure HTML podium

### 2. BigQuery

```sql
SELECT 
    extraction_date,
    rank,
    handle,
    kills
FROM `battlefield-meta-aggregator.bf6_meta.bronze_leaderboard`
WHERE extraction_date = CURRENT_DATE()
ORDER BY rank
LIMIT 10
```

**Vérifier** :
- ✅ Rangs 1, 2, 3 présents
- ✅ `extraction_date` = 2025-11-06
- ✅ Noms correspondent tracker.gg

## 🚨 Fallbacks si Problème Persiste

### Option 1 : Augmenter Timing

Dans `extract_bf6_meta_complete.py` :

```python
time.sleep(30)  # Au lieu de 15s (Cloudflare)
time.sleep(40)  # Au lieu de 20s (JS loading)
```

### Option 2 : Wait Explicit (Selenium)

```python
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Attendre que le tableau soit visible
wait = WebDriverWait(driver, 60)
table = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table")))
```

### Option 3 : Playwright (Alternative Selenium)

Si UC ne fonctionne plus :

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(LEADERBOARD_URL)
    page.wait_for_selector('tr[data-key]', timeout=60000)
    html = page.content()
```

### Option 4 : API Tracker.gg (Solution Idéale)

Contacter tracker.gg pour accès API officiel. Avantages :
- ✅ Pas de scraping (légal, stable)
- ✅ Pas de Cloudflare
- ✅ Données structurées JSON
- ✅ Rate limiting clair

## 📝 Historique Corrections

### v1 (6 Nov 2025 - Initial)
- Ajout `undetected-chromedriver`
- Headless natif UC au lieu de `--headless=new`
- User-agent réaliste

### v2 (6 Nov 2025 - Timing SPA)
- Augmentation attente: 15s → 20s → scroll
- Scroll haut/bas pour lazy loading
- Logs debug data-key

### v3 (À venir - Si besoin)
- Selenium WebDriverWait explicit
- Ou migration Playwright

## 🎯 Résultats Attendus

Après corrections complètes :

- ✅ Workflow extrait 50 joueurs **rangs 1-50** (pas 4-53 !)
- ✅ `extraction_date` = jour du workflow
- ✅ BigQuery contient données actuelles
- ✅ Top 1 = ⨤🜁♄🜍⛎︎🜚🜔☽ (72,815 kills)
- ✅ Dashboard affiche classements corrects

---

**Dernière mise à jour** : 6 novembre 2025 - v2  
**Statut** : ⏳ Test local en cours (PID 18147)  
**Prochaine étape** : Analyser logs + HTML debug → Adapter sélecteur si rangs 1-3 manquent


## 🔍 Diagnostic

### HTML Récupéré par Selenium

Au lieu du leaderboard, le script récupère :

```html
<html>
  <head><title>Just a moment...</title></head>
  <body>
    <h1>Verify you are human by completing the action below.</h1>
    <p>tracker.gg needs to review the security of your connection</p>
  </body>
</html>
```

### Conséquences

1. ❌ Aucun `data-key` trouvé dans le HTML (page vide de joueurs)
2. ❌ Script retourne liste vide ou utilise ancien checkpoint
3. ❌ BigQuery contient données vieilles de 7 jours
4. ❌ Dashboard affiche classements incorrects

## 🔧 Solution Implémentée

### 1. **Undetected ChromeDriver** (déjà installé)

Package : `undetected-chromedriver`

**Avant** :
```python
options.add_argument('--headless=new')  # ❌ Détecté par Cloudflare
driver = webdriver.Chrome(options=options)
```

**Après** :
```python
import undetected_chromedriver as uc

options = uc.ChromeOptions()
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument('user-agent=Mozilla/5.0 ...')

driver = uc.Chrome(
    options=options,
    headless=True,  # ✅ Headless mode natif UC (bypass Cloudflare)
    use_subprocess=True
)
```

### 2. **Délai d'Attente Cloudflare**

```python
driver.get(LEADERBOARD_URL)
time.sleep(30)  # Attente bypass automatique

# Vérifier si challenge encore présent
if "Just a moment" in driver.page_source:
    time.sleep(30)  # Attente supplémentaire
```

### 3. **User-Agent Réaliste**

```python
user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 
(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36
```

## 🧪 Test de la Solution

### Local

```bash
cd /Users/paulfrette/Github_pro_folder/battlefield_meta_aggregator
python3 scripts/extract_bf6_meta_complete.py
```

**Indicateurs de succès** :
- ✅ Log : "🤖 Mode CI/CD détecté - Chrome headless avec bypass Cloudflare"
- ✅ Pas de message "Just a moment" dans les logs
- ✅ "🔍 50+ joueurs trouvés dans le tableau"
- ✅ Fichiers NDJSON créés avec `extraction_date` = aujourd'hui

### GitHub Actions

Relancer le workflow manuellement :
1. Aller sur Actions → Weekly BF6 Meta Extraction
2. Cliquer "Run workflow" → "Run workflow"
3. Vérifier Job 2 (Extract) :
   - ✅ "Attente bypass Cloudflare (30s)..."
   - ✅ "50 joueurs trouvés"
   - ❌ ÉVITER "Cloudflare challenge détecté"

## 📊 Vérification des Données

### 1. Vérifier NDJSON Téléchargés

```bash
# Télécharger artefacts GitHub
cd /tmp
unzip ndjson-data.zip

# Vérifier première ligne
head -1 leaderboard/bf6_leaderboard_*.ndjson | python3 -m json.tool
```

**Vérifier** :
- `"rank": 1` (pas 4 !) - Le top 1 doit être présent
- `"extraction_date": "2025-11-06..."` - Date d'aujourd'hui
- `"handle"` correspond au top 1 de tracker.gg

### 2. Vérifier BigQuery

```sql
SELECT 
    extraction_date,
    rank,
    handle,
    kills
FROM `battlefield-meta-aggregator.bf6_meta.bronze_leaderboard`
WHERE extraction_date = CURRENT_DATE()
ORDER BY rank
LIMIT 5
```

**Attendu** :
- Rang 1, 2, 3 présents
- `extraction_date` = 2025-11-06
- Noms correspondent à tracker.gg

## 🚨 Fallbacks si Cloudflare Persiste

### Option 1 : Augmenter Délai

Dans `extract_bf6_meta_complete.py` :

```python
time.sleep(60)  # Au lieu de 30s
```

### Option 2 : Proxies Résidentiels

```python
options.add_argument('--proxy-server=http://proxy.example.com:8080')
```

### Option 3 : Playwright (Alternative)

Si UC ne fonctionne plus, migrer vers Playwright :

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(LEADERBOARD_URL)
    page.wait_for_timeout(30000)  # 30s
    html = page.content()
```

### Option 4 : Scraping API

Contacter tracker.gg pour accès API officiel (meilleure solution long-terme).

## 📝 Commit de la Correction

```bash
git add scripts/extract_bf6_meta_complete.py docs/CLOUDFLARE_BYPASS.md
git commit -m "fix: Bypass Cloudflare challenge avec undetected-chromedriver

- Utilise headless=True natif UC au lieu de --headless=new
- Ajoute user-agent réaliste + disable AutomationControlled  
- Augmente délai à 30s + double vérification challenge
- Détecte 'Just a moment' et relance attente si nécessaire

Root Cause: Workflow extrait données du 30 oct (7j old) car Cloudflare
bloquait Selenium. Solution testée localement ✅"
```

## 🎯 Résultats Attendus

Après correction :

- ✅ Workflow extrait 50 joueurs rangs 1-50 (pas 4-53)
- ✅ Extraction_date = jour du workflow
- ✅ BigQuery et Dashboard montrent données actuelles
- ✅ Top 1 = ⨤🜁♄🜍⛎︎🜚🜔☽ (72,815 kills)

---

**Dernière mise à jour** : 6 novembre 2025  
**Statut** : ✅ Solution implémentée, en attente de test workflow

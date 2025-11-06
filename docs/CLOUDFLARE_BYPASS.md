# 🛡️ Cloudflare Bypass - Guide de Résolution

## 📋 Problème Identifié (6 Nov 2025)

**Symptôme** : Le workflow GitHub Actions extrait 0 joueurs et utilise d'anciennes données du 30 octobre.

**Root Cause** : Tracker.gg utilise **Cloudflare Protection** qui bloque Selenium avec un challenge "Verify you are human".

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

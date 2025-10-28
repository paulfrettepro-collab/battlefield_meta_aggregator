# ⚡ Optimisation du Temps d'Extraction

## 📊 Analyse Actuelle (30 minutes)

### Breakdown du temps d'extraction

```
97 joueurs × 20 secondes = 1,940 secondes = ~32 minutes
```

**Goulot d'étranglement identifié** :

```python
# scripts/extract_bf6_top_weapons_final.py ligne 148
time.sleep(20)  # ← PROBLÈME : Wait fixe de 20s par joueur
```

### Pourquoi 20 secondes ?

**Cloudflare bypass** : Chaque page nécessite :
1. Chargement initial (2-3s)
2. Résolution challenge Cloudflare (10-15s)
3. Rendu JavaScript (2-3s)

**Total** : ~15-20 secondes minimum

---

## 🎯 Stratégies d'Optimisation

### **Option 1 : Extraction Parallèle** ⭐ **RECOMMANDÉ**

**Principe** : Extraire plusieurs joueurs en parallèle au lieu de séquentiel

**Impact** :
- Actuel : 97 joueurs × 20s = **32 minutes**
- Avec 5 workers : 97 ÷ 5 × 20s = **~6.5 minutes** ✅
- Avec 10 workers : 97 ÷ 10 × 20s = **~3.2 minutes** ✅

**Code** :

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Driver pool (1 par thread)
thread_local = threading.local()

def get_driver():
    """Retourne un driver Chrome par thread"""
    if not hasattr(thread_local, "driver"):
        thread_local.driver = uc.Chrome()
    return thread_local.driver

def extract_player_weapons_threadsafe(player_data):
    """Version thread-safe de l'extraction"""
    driver = get_driver()
    # ... extraction normale
    return result

# Extraction parallèle
def extract_all_weapons_parallel(players, max_workers=5):
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(extract_player_weapons_threadsafe, player): player
            for player in players
        }
        
        for future in as_completed(futures):
            player = futures[future]
            try:
                result = future.result()
                results.append(result)
                print(f"✅ {player['handle']} ({len(results)}/97)")
            except Exception as e:
                print(f"❌ {player['handle']}: {e}")
                
    return results
```

**Avantages** :
- ✅ **6-10x plus rapide** (32 min → 3-6 min)
- ✅ Facile à implémenter (50 lignes de code)
- ✅ Robuste (retry par joueur)

**Inconvénients** :
- ⚠️ RAM : 5 Chrome = ~2GB (gérable)
- ⚠️ Risque de ban Tracker.gg (mitigé avec 5 workers max)

---

### **Option 2 : Wait Dynamique (au lieu de fixe)**

**Principe** : Attendre seulement le temps nécessaire, pas 20s systématiquement

**Code** :

```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

def wait_for_weapons_table(driver, timeout=30):
    """Attendre que le tableau d'armes soit chargé"""
    try:
        # Attendre qu'un élément wp_ apparaisse
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "tr[data-key^='wp_']"))
        )
        # Attendre 2s supplémentaires pour le rendu complet
        time.sleep(2)
        return True
    except:
        return False

# Dans extract_player_weapons()
driver.get(url)
if wait_for_weapons_table(driver):
    html = driver.page_source
    # ... extraction
```

**Impact** :
- Joueurs rapides : 10s au lieu de 20s (**50% gain**)
- Joueurs lents : 20-25s (pas de perte)
- **Moyenne** : ~15s → 97 × 15s = **24 minutes** ✅

**Avantages** :
- ✅ Pas de RAM supplémentaire
- ✅ Pas de risque de ban
- ✅ Simple à implémenter

**Inconvénients** :
- ⚠️ Gain modéré (25% seulement)

---

### **Option 3 : Cache Incrémental** 🆕

**Principe** : Ne ré-extraire que les joueurs modifiés

**Architecture** :

```
1. Extraction initiale : 97 joueurs (32 min)
2. Stockage : hash(handle + kills) → BigQuery
3. Extraction suivante : 
   - Comparer leaderboard actuel vs précédent
   - Extraire seulement nouveaux joueurs + changements
   - Exemple : 10 nouveaux + 5 modifiés = 15 joueurs (5 min)
```

**Code** :

```python
def get_previous_extraction_hashes():
    """Récupérer les hash de la dernière extraction"""
    query = """
    SELECT handle, player_id, 
           MD5(CONCAT(handle, CAST(total_kills AS STRING))) as hash
    FROM `bf6_meta.silver_players`
    WHERE extraction_date = (SELECT MAX(extraction_date) FROM `bf6_meta.silver_players`)
    """
    return bigquery_client.query(query).to_dataframe()

def filter_changed_players(new_leaderboard, previous_hashes):
    """Retourner seulement les joueurs nouveaux/modifiés"""
    changed = []
    for player in new_leaderboard:
        new_hash = hashlib.md5(f"{player['handle']}{player['kills']}".encode()).hexdigest()
        prev_hash = previous_hashes.get(player['handle'])
        
        if prev_hash != new_hash:  # Nouveau ou modifié
            changed.append(player)
            
    return changed
```

**Impact** :
- **1ère extraction** : 32 min (normal)
- **Extractions suivantes** : ~5-10 min ✅ (15-20 joueurs modifiés/semaine)

**Avantages** :
- ✅ **Très rapide** après 1ère fois
- ✅ Économie de ressources
- ✅ Historique préservé

**Inconvénients** :
- ⚠️ Complexité (gestion cache)
- ⚠️ 1ère extraction reste longue

---

### **Option 4 : Headless Optimisé**

**Principe** : Utiliser mode headless avec options optimisées

**Code** :

```python
def create_optimized_driver():
    """Driver Chrome ultra-rapide"""
    options = uc.ChromeOptions()
    options.add_argument('--headless=new')  # Nouveau mode headless
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-images')  # Pas d'images
    options.add_argument('--disable-javascript')  # Si possible
    options.add_argument('--blink-settings=imagesEnabled=false')
    
    # Désactiver extensions
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-plugins')
    
    return uc.Chrome(options=options, version_main=130)
```

**Impact** :
- Gain : **10-20%** (18s au lieu de 20s)
- **29 minutes** au lieu de 32 ✅

**Avantages** :
- ✅ Facile à tester
- ✅ Pas de changement d'architecture

**Inconvénients** :
- ⚠️ Headless parfois bloqué par Cloudflare
- ⚠️ Gain faible

---

## 🏆 Solution Recommandée : **COMBO Option 1 + Option 2**

### Architecture Finale

```python
# Extraction parallèle (5 workers) + Wait dynamique

from concurrent.futures import ThreadPoolExecutor
import threading

thread_local = threading.local()

def get_driver():
    if not hasattr(thread_local, "driver"):
        thread_local.driver = uc.Chrome()
    return thread_local.driver

def wait_for_weapons(driver, timeout=30):
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By
    
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "tr[data-key^='wp_']"))
        )
        time.sleep(2)  # Buffer de sécurité
        return True
    except:
        return False

def extract_player_parallel(player_data):
    driver = get_driver()
    url = f"https://tracker.gg/battlefield-6/profile/{player_data['player_id']}/weapons"
    
    driver.get(url)
    
    if not wait_for_weapons(driver):
        return {'status': 'timeout', 'handle': player_data['handle']}
    
    html = driver.page_source
    weapons = extract_weapons_from_table(html)
    
    return {
        'handle': player_data['handle'],
        'player_id': player_data['player_id'],
        'top_weapons': weapons[:3],
        'status': 'success'
    }

# Main extraction
def main():
    players = load_leaderboard()
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(extract_player_parallel, players))
    
    save_results(results)
```

### Résultats Attendus

| Métrique | Avant | Après | Gain |
|----------|-------|-------|------|
| **Temps total** | 32 min | **4-6 min** | **85% ✅** |
| **Temps/joueur** | 20s | ~3-4s (parallel) | 80% |
| **RAM** | 500 MB | 2 GB | Acceptable |
| **Succès rate** | 95% | 95% | = |

---

## 🚀 Plan d'Implémentation (1h)

### Phase 1 : Test Option 2 (Wait Dynamique) - 15 min

```bash
# Créer branch
git checkout -b feature/optimize-extraction

# Modifier scripts/extract_bf6_top_weapons_final.py
# Ajouter wait_for_weapons()

# Tester sur 5 joueurs
python scripts/extract_bf6_top_weapons_final.py --limit 5
```

### Phase 2 : Implémenter Option 1 (Parallèle) - 30 min

```bash
# Créer scripts/extract_bf6_top_weapons_parallel.py
# Copier extract_bf6_top_weapons_final.py
# Ajouter ThreadPoolExecutor

# Tester sur 10 joueurs
python scripts/extract_bf6_top_weapons_parallel.py --limit 10 --workers 3
```

### Phase 3 : Validation complète - 15 min

```bash
# Extraction complète (97 joueurs)
time python scripts/extract_bf6_top_weapons_parallel.py --workers 5

# Vérifier résultats
python scripts/load_to_bigquery.py
```

---

## 📈 Monitoring

### Métriques à tracker

```python
import time

start = time.time()
results = extract_all_parallel(players, workers=5)
duration = time.time() - start

print(f"⏱️ Durée totale: {duration/60:.1f} min")
print(f"⚡ Vitesse: {len(players)/duration:.2f} joueurs/s")
print(f"✅ Succès: {sum(1 for r in results if r['status']=='success')}/{len(players)}")
```

---

## ⚠️ Limites & Risques

### Rate Limiting Tracker.gg

**Risque** : Ban temporaire si trop de requêtes

**Mitigation** :
- Max 5 workers simultanés
- User-Agent rotation
- Proxy rotation (si besoin)

### Stabilité Cloudflare

**Risque** : Bypass plus difficile en parallèle

**Mitigation** :
- Retry automatique (2 tentatives)
- Fallback séquentiel si échec

---

## 🎯 Objectif Final

```
Temps d'extraction: 30 min → 5 min ✅
Bouton "Refresh" utilisable ✅
Expérience utilisateur fluide ✅
```

**Phase 5+ : Ajouter Option 3 (cache) pour descendre à 2-3 min** 🚀

---

**Dernière mise à jour** : 27 octobre 2025

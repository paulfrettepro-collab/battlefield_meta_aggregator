# 🔧 GUIDE DÉPANNAGE - BF6 META AGGREGATOR

## 🚨 SCÉNARIO 1: Workflow v4 échoue encore avec Cloudflare

**Si logs montrent encore**: `"Cloudflare challenge non résolu après 45s"`

### Option A: Augmenter timeout encore plus (60s)
```python
# Dans extract_bf6_meta_complete.py, ligne ~127
wait_time = 30 if os.getenv('GITHUB_ACTIONS') == 'true' else 15  # Au lieu de 20
time.sleep(30)  # Au lieu de 25
```

### Option B: Utiliser Playwright au lieu de Selenium
Playwright a un meilleur bypass Cloudflare intégré.

```bash
# Dans workflow yml
pip install playwright
playwright install chromium
```

### Option C: Utiliser un proxy résidentiel
Cloudflare whitelist les IPs résidentielles.

### Option D: Extraire via API (si disponible)
Vérifier si tracker.gg a une API publique ou GraphQL.

---

## 🚨 SCÉNARIO 2: Rangs 1-3 manquent encore

**Si validation shows**: `"Le fichier commence au rang 4"`

### Debug étapes:
1. Vérifier HTML debug file:
```bash
grep -A 5 'data-key="1"' leaderboard_debug_latest.html
```

2. Vérifier logs parsing:
```bash
grep "structure podium" pipeline_*.log
```

3. Test parsing local:
```python
python3 << 'EOF'
from bs4 import BeautifulSoup
html = open('leaderboard_debug_latest.html').read()
soup = BeautifulSoup(html, 'html.parser')
row = soup.find('tr', {'data-key': '1'})
print(f"Row 1 trouvée: {row is not None}")
if row:
    cells = row.find_all('td')
    print(f"Nombre de cellules: {len(cells)}")
    rank_span = cells[0].find('span', class_='min-w-9')
    print(f"Span min-w-9: {rank_span is not None}")
    print(f"data-key: {row.get('data-key')}")
EOF
```

### Si structure HTML a changé:
Tracker.gg peut avoir modifié la structure. Adapter les sélecteurs dans `extract_bf6_meta_complete.py`.

---

## 🚨 SCÉNARIO 3: Extraction réussie mais BigQuery vide

**Vérifier**:
1. Job 3 (Load to BigQuery) logs
2. Permissions GCP
3. Schema table

```bash
# Vérifier schema
bq show --format=prettyjson battlefield-meta-aggregator:bf6_meta.bronze_leaderboard
```

---

## 🚨 SCÉNARIO 4: DBT tests échouent

**Si tests DBT rouges**:
1. Vérifier données source valides
2. Vérifier transformations silver/gold
3. Logs Job 4

```sql
-- Vérifier données silver
SELECT * FROM bf6_meta_silver.silver_players 
WHERE extraction_date = CURRENT_DATE()
LIMIT 5;
```

---

## 🚨 SCÉNARIO 5: Dashboard ne se met pas à jour

**Vérifier**:
1. Streamlit Cloud connecté à BigQuery
2. Credentials GCP valides
3. Cache Streamlit (`st.cache_data` TTL)

**Forcer refresh**:
- Redémarrer app dans Streamlit Cloud
- Vider cache navigateur
- Vérifier logs Streamlit Cloud

---

## 🛠️ OUTILS DIAGNOSTIC

### 1. Vérifier état complet pipeline
```bash
# Vérifier dernière extraction
ls -lt data/bronze/tracker_gg/leaderboard/*.ndjson | head -1

# Valider extraction
./scripts/validate_extraction.sh <fichier_ndjson>

# Valider BigQuery
python3 scripts/validate_bigquery.py
```

### 2. Tester extraction locale (sans Cloudflare)
```python
python3 scripts/extract_bf6_meta_complete.py
# Vérifier data/bronze/tracker_gg/leaderboard/
```

### 3. Comparer avec tracker.gg actuel
```bash
# Ouvrir https://tracker.gg/bf6/leaderboards?platform=all&board=Kills&page=1
# Comparer manuellement top 3 avec nos données
```

---

## 📊 MÉTRIQUES SUCCÈS

**Pipeline sain si**:
- ✅ Workflow < 10 minutes (actuellement ~6min)
- ✅ 50 joueurs extraits (pas 0)
- ✅ Rangs 1-50 (pas 4-53)
- ✅ extraction_date = jour actuel
- ✅ 44/44 tests DBT passés
- ✅ Dashboard mis à jour < 5 min après workflow

---

## 🔄 PLAN B: Fallback MinIO

**Si extraction échoue systématiquement**:

Le workflow utilise déjà un fallback MinIO (Job 3 ligne ~160):
```yaml
- name: Download from MinIO if extraction failed
```

**Amélioration**: Ajouter alerte email si fallback utilisé.

---

## 📞 CONTACT SUPPORT

**Issues GitHub**: https://github.com/paulfrettepro-collab/battlefield_meta_aggregator/issues

**Logs utiles à fournir**:
1. Job 2 (Extract) logs complets
2. Fichier leaderboard_debug_latest.html
3. Artefacts NDJSON
4. BigQuery validation output

---

## 🎯 NEXT STEPS SI TOUT FONCTIONNE

1. **Automatiser validation**: Ajouter Job 6 au workflow
2. **Monitoring**: Setup alerts Slack/Discord
3. **Documentation**: Mettre à jour README
4. **Tests**: Ajouter tests unitaires parsing
5. **Performance**: Optimiser timing (réduire 45s si stable)

---

**Dernière mise à jour**: 6 novembre 2025  
**Version**: v4 (Xvfb)

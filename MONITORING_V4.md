# 🚀 MONITORING WORKFLOW V4 - FIX XVFB

**Date**: 6 novembre 2025  
**Commit**: a7a21b4 (Xvfb display virtuel)  
**Objectif**: Extraire rangs 1-50 avec données du jour

---

## ✅ CHECKLIST PRE-RUN

- [x] Commit a7a21b4 pushed avec succès
- [x] Script modifié: Chrome avec DISPLAY=:99 (pas headless)
- [x] Workflow modifié: Install Xvfb avant extraction
- [x] Timeout augmenté: 45s max (vs 35s avant)
- [x] Scripts de validation créés et testés
- [ ] **ACTION REQUISE**: Déclencher workflow manuellement sur GitHub

---

## 📊 ÉTAPES À SURVEILLER (Job 2: Extract)

### ✅ Step 1: Install and start Xvfb
**Attendu**:
```
sudo apt-get install -y xvfb
sudo Xvfb :99 -ac -screen 0 1920x1080x24 &
✅ Xvfb démarré sur DISPLAY=:99
```

### ✅ Step 2: Run extraction script (avec DISPLAY=:99)
**Logs attendus**:
```
🤖 Mode CI/CD détecté - Chrome avec display virtuel :99
⏳ Attente bypass Cloudflare + chargement JS (20s)...
⏳ Attente chargement tableau JavaScript (20s)...
🔍 100 joueurs trouvés dans le tableau
🔎 DEBUG - Premiers data-key trouvés:
  Row 1: data-key = 1
  Row 2: data-key = 2
  Row 3: data-key = 3
Rang 1 : structure podium détectée (pas de span min-w-9)
Rang 2 : structure podium détectée (pas de span min-w-9)
Rang 3 : structure podium détectée (pas de span min-w-9)
✅ 50 joueurs extraits
```

**🚨 ERREURS À ÉVITER** (v3):
```
❌ Cloudflare challenge non résolu après 35s
❌ Aucun joueur extrait du leaderboard
```

---

## 🎯 CRITÈRES DE SUCCÈS

### Job 2 (Extract)
- [ ] ✅ Xvfb installé et lancé sur :99
- [ ] ✅ Chrome détecte DISPLAY=:99
- [ ] ✅ Cloudflare challenge résolu (pas d'erreur après 45s)
- [ ] ✅ 100 joueurs détectés dans HTML
- [ ] ✅ Rangs 1-3 détectés avec structure podium
- [ ] ✅ 50 joueurs extraits dans NDJSON
- [ ] ✅ extraction_date = 2025-11-06

### Job 3 (Load to BigQuery)
- [ ] ✅ 50 lignes insérées
- [ ] ✅ Pas d'erreurs de schema

### Job 4 (DBT Transformations)
- [ ] ✅ silver_players: 50 lignes
- [ ] ✅ gold_player_rankings: 50 lignes
- [ ] ✅ 44 tests DBT passés

### Job 5 (Validate Pipeline Output)
- [ ] ✅ Validation réussie

---

## 📦 VALIDATION ARTEFACTS (v4)

Une fois le workflow terminé, télécharger les artefacts et valider :

```bash
# 1. Télécharger artefacts v4 depuis GitHub Actions

# 2. Valider extraction
./scripts/validate_extraction.sh "git_hub_action_artifacts/v4/ndjson-data/leaderboard/bf6_leaderboard_*.ndjson"

# Attendu:
# ✅ Premier rang: 1
# ✅ Joueurs extraits: 50
# ✅ Date extraction: 2025-11-06
# 🎉 Les rangs 1-3 sont présents et valides !
```

---

## 🗄️ VALIDATION BIGQUERY

```bash
# Vérifier BigQuery
python3 scripts/validate_bigquery.py

# Attendu:
# ✅ Données du jour trouvées: 50 joueurs
# ✅ VALIDATION CRITIQUE: Le rang 1 est présent ! 🎉
# 🏆 TOP 5 JOUEURS (BigQuery):
#    Rang  1: [Top player actuel]
#    Rang  2: [2e joueur]
#    Rang  3: [3e joueur]
```

---

## 🎨 VALIDATION DASHBOARD

Dashboard URL: https://[your-app].streamlit.app

**Vérifications**:
- [ ] Top 1 player affiché = joueur actuel tracker.gg (pas ancien)
- [ ] Kills affichées cohérentes (70k+)
- [ ] Date extraction visible = 6 nov 2025
- [ ] Top weapons mis à jour
- [ ] Graphiques cohérents

---

## 🎉 CRITÈRES SUCCÈS FINAL

**VICTOIRE TOTALE si**:
1. ✅ Workflow v4 termine avec succès (6 jobs verts)
2. ✅ Artefacts NDJSON commencent au rang 1 (pas 4)
3. ✅ extraction_date = 2025-11-06 (pas 30 oct)
4. ✅ BigQuery contient rangs 1-3 avec noms corrects
5. ✅ Dashboard affiche top player actuel

**Si SUCCÈS** → 🎊 Problème RÉSOLU ! Pipeline opérationnel et robuste !

**Si ÉCHEC** → Analyser logs Job 2, identifier nouvelle stratégie (Playwright? Proxy?)

---

## 📝 NOTES

- **Root cause v3**: headless=True détecté par Cloudflare sur Ubuntu
- **Fix v4**: Xvfb (display virtuel :99) + Chrome normal = moins détectable
- **Parsing podium**: Commit 66c6df6 (data-key fallback) déjà appliqué
- **Timeout**: 45s max au lieu de 35s

---

**Status**: 🟡 EN ATTENTE - Workflow à déclencher manuellement

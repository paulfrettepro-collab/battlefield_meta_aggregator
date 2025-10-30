# 🤖 Automatisation du Pipeline BF6 Meta Aggregator

Ce guide explique comment automatiser l'exécution hebdomadaire du pipeline complet.

---

## 📋 Vue d'Ensemble

Le pipeline automatisé exécute les 4 étapes suivantes :

1. **Extraction** : Scraping du leaderboard + top 3 armes (~30 min)
2. **Chargement** : Upload vers BigQuery (Bronze) (~10s)
3. **Transformation** : DBT (Silver → Gold) (~15s)
4. **Validation** : Vérification des données

**Durée totale** : ~30-35 minutes

---

## 🛠️ Configuration

### Prérequis

- ✅ Python 3.12+ installé
- ✅ Chrome/Chromium installé
- ✅ DBT installé (`/Users/paulfrette/.local/bin/dbt`)
- ✅ Credentials BigQuery configurées
- ✅ Variables d'environnement (.env)

### Fichiers du Pipeline

```
scripts/
├── run_pipeline.sh          # 🎯 Script principal d'automatisation
├── crontab_setup.txt        # 📝 Instructions cron
├── extract_bf6_meta_complete.py
└── load_to_bigquery_latest.py

logs/
├── pipeline_YYYYMMDD_HHMMSS.log  # Logs d'exécution
└── cron.log                      # Logs cron
```

---

## 🚀 Méthodes d'Automatisation

### Option 1 : Cron (Local) ⭐ **RECOMMANDÉ POUR TEST**

**Avantages** :
- Simple à configurer
- Gratuit
- Contrôle total

**Inconvénients** :
- Nécessite un Mac allumé 24/7
- Pas de monitoring centralisé

**Installation** :

1. **Tester manuellement le pipeline** :
   ```bash
   cd /Users/paulfrette/Github_pro_folder/battlefield_meta_aggregator
   ./scripts/run_pipeline.sh
   ```

2. **Configurer cron** :
   ```bash
   crontab -e
   ```

3. **Ajouter la ligne suivante** (Dimanche 2h00) :
   ```
   0 2 * * 0 /Users/paulfrette/Github_pro_folder/battlefield_meta_aggregator/scripts/run_pipeline.sh >> /Users/paulfrette/Github_pro_folder/battlefield_meta_aggregator/logs/cron.log 2>&1
   ```

4. **Sauvegarder et vérifier** :
   ```bash
   crontab -l
   ```

**Monitoring** :
```bash
# Voir les logs en temps réel
tail -f logs/cron.log

# Lister les exécutions passées
ls -ltr logs/pipeline_*.log

# Voir le dernier log
tail -100 logs/pipeline_$(ls -t logs/pipeline_*.log | head -1)
```

---

### Option 2 : GitHub Actions (Cloud) ⭐ **RECOMMANDÉ POUR PRODUCTION**

**Avantages** :
- Pas besoin de serveur local
- Gratuit (2000 min/mois)
- Logs centralisés
- Historique des runs
- Notifications par email

**Inconvénients** :
- Credentials à stocker dans GitHub Secrets
- Limitation de durée (6h max par job)

**Setup** :

1. **Créer `.github/workflows/weekly_extraction.yml`** :
   ```yaml
   name: Weekly BF6 Meta Extraction
   
   on:
     schedule:
       - cron: '0 2 * * 0'  # Dimanche 2h00 UTC
     workflow_dispatch:  # Permet trigger manuel
   
   jobs:
     extract-and-load:
       runs-on: ubuntu-latest
       timeout-minutes: 60
       
       steps:
         - name: Checkout code
           uses: actions/checkout@v3
         
         - name: Setup Python
           uses: actions/setup-python@v4
           with:
             python-version: '3.12'
         
         - name: Install dependencies
           run: |
             pip install -r requirements.txt
             pip install dbt-core dbt-bigquery
         
         - name: Setup Chrome
           uses: browser-actions/setup-chrome@latest
         
         - name: Create credentials file
           run: |
             echo '${{ secrets.GCP_CREDENTIALS }}' > config/bigquery-key.json
         
         - name: Run extraction
           run: python scripts/extract_bf6_meta_complete.py
         
         - name: Load to BigQuery
           run: python scripts/load_to_bigquery_latest.py
         
         - name: Run DBT
           run: |
             cd dbt
             dbt run
             dbt test
         
         - name: Upload logs
           uses: actions/upload-artifact@v3
           if: always()
           with:
             name: pipeline-logs
             path: logs/
   ```

2. **Configurer les Secrets GitHub** :
   - Aller dans `Settings → Secrets → Actions`
   - Ajouter `GCP_CREDENTIALS` (contenu de bigquery-key.json)

3. **Tester manuellement** :
   - Aller dans `Actions`
   - Sélectionner "Weekly BF6 Meta Extraction"
   - Cliquer "Run workflow"

---

### Option 3 : Google Cloud Scheduler + Cloud Functions 💰

**Avantages** :
- 100% cloud managed
- Auto-scaling
- Monitoring intégré (Stackdriver)
- Haute disponibilité

**Inconvénients** :
- Coût (quelques $/mois)
- Configuration plus complexe
- Nécessite déploiement

**Coût estimé** :
- Cloud Functions : ~$0.40/mois (1 run/semaine × 30min)
- Cloud Scheduler : $0.10/mois
- BigQuery : Gratuit (< 10 GB)
- **Total** : ~$0.50/mois

**Setup** (Résumé) :

1. Créer une Cloud Function :
   ```bash
   gcloud functions deploy bf6-extract \
     --runtime python312 \
     --trigger-http \
     --entry-point main \
     --timeout 3600s
   ```

2. Créer un Cloud Scheduler :
   ```bash
   gcloud scheduler jobs create http bf6-weekly \
     --schedule="0 2 * * 0" \
     --uri="https://REGION-PROJECT.cloudfunctions.net/bf6-extract" \
     --http-method=POST
   ```

---

## 📊 Monitoring et Alertes

### Vérifications Post-Exécution

**1. Vérifier les logs** :
```bash
tail -100 logs/pipeline_$(ls -t logs/pipeline_*.log | head -1)
```

**2. Vérifier BigQuery** :
```sql
-- Dernière extraction
SELECT MAX(extraction_date) FROM bf6_meta.bronze_leaderboard;

-- Nombre de joueurs/armes
SELECT COUNT(*) FROM bf6_meta.bronze_leaderboard;
SELECT COUNT(*) FROM bf6_meta.bronze_weapons;

-- TOP 5 armes
SELECT weapon_name, SUM(total_kills) as kills
FROM bf6_meta_gold.gold_top_weapons_global
ORDER BY global_rank
LIMIT 5;
```

**3. Vérifier le dashboard Streamlit** :
```bash
cd dashboard
streamlit run app.py
```

### Alertes

**Email cron (macOS)** :
```bash
# Ajouter MAILTO en haut de crontab
MAILTO="votre.email@example.com"
0 2 * * 0 /path/to/run_pipeline.sh
```

**Slack Webhook (optionnel)** :
```bash
# Ajouter en fin de run_pipeline.sh
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"✅ BF6 Pipeline terminé!"}' \
  https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

---

## 🔧 Dépannage

### Le pipeline ne se lance pas

1. **Vérifier cron** :
   ```bash
   crontab -l  # Voir les tâches
   sudo launchctl list | grep cron  # Vérifier si cron est actif
   ```

2. **Permissions** :
   ```bash
   chmod +x scripts/run_pipeline.sh
   ```

3. **Chemins absolus** :
   - S'assurer que tous les chemins dans le script sont absolus
   - Vérifier que `PYTHON_BIN` et `DBT_BIN` pointent vers les bons exécutables

### L'extraction échoue

1. **Chrome/Chromium** :
   ```bash
   which chrome
   which chromium
   ```

2. **Cloudflare** :
   - Vérifier que `undetected-chromedriver` est installé
   - Essayer avec un délai plus long (`time.sleep(10)`)

### DBT échoue

1. **PATH** :
   ```bash
   export PATH="/Users/paulfrette/.local/bin:$PATH"
   which dbt
   ```

2. **Profiles** :
   ```bash
   cat ~/.dbt/profiles.yml
   ```

---

## 📅 Planning Recommandé

**Dimanche 2h00** (Option 1 - cron) :
- Faible trafic sur tracker.gg
- Temps d'exécution : 30-35 min
- Dashboard mis à jour pour la semaine

**Alternative** : Mercredi 1h00 (milieu de semaine)

---

## 📝 Checklist de Mise en Production

- [ ] Tester `run_pipeline.sh` manuellement
- [ ] Vérifier que tous les chemins sont corrects
- [ ] Créer le répertoire `logs/`
- [ ] Configurer cron (Option 1) OU GitHub Actions (Option 2)
- [ ] Tester l'exécution automatique (attendre 1 semaine)
- [ ] Vérifier les logs après la première exécution
- [ ] Configurer des alertes (email/Slack)
- [ ] Documenter les incidents éventuels

---

## 🎯 Prochaines Améliorations

- [ ] Retry automatique en cas d'échec
- [ ] Slack/Discord notifications
- [ ] Dashboard de monitoring (Grafana)
- [ ] Historisation des extractions (plusieurs semaines)
- [ ] Comparaison meta week-over-week
- [ ] API REST pour interroger les données

---

**Dernière mise à jour** : 29 octobre 2025  
**Statut** : ✅ Pipeline testé et fonctionnel  
**Automatisation** : ⏳ En attente de configuration cron/GitHub Actions

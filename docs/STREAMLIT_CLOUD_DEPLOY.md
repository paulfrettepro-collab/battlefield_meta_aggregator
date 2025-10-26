# 🚀 Déploiement Streamlit Cloud - Guide Express

## Étape 1 : Préparer le code

### 1.1 Créer `.streamlit/secrets.toml` (local uniquement)

```bash
mkdir -p dashboard/.streamlit
```

Créer `dashboard/.streamlit/secrets.toml` :
```toml
# NE PAS COMMITTER CE FICHIER

[gcp_service_account]
type = "service_account"
project_id = "battlefield-meta-aggregator"
private_key_id = "VOTRE_PRIVATE_KEY_ID"
private_key = "-----BEGIN PRIVATE KEY-----\nVOTRE_CLE\n-----END PRIVATE KEY-----\n"
client_email = "VOTRE_SERVICE_ACCOUNT@battlefield-meta-aggregator.iam.gserviceaccount.com"
client_id = "VOTRE_CLIENT_ID"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/VOTRE_SERVICE_ACCOUNT%40battlefield-meta-aggregator.iam.gserviceaccount.com"
```

### 1.2 Modifier `.gitignore`

Ajouter :
```
.streamlit/secrets.toml
```

### 1.3 Modifier `dashboard/utils/bigquery.py`

Remplacer la fonction `get_bigquery_client()` :

```python
import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account
from pathlib import Path

@st.cache_resource
def get_bigquery_client():
    """
    Create and cache a BigQuery client.
    Works both locally and on Streamlit Cloud.
    """
    # Check if running on Streamlit Cloud (secrets available)
    if "gcp_service_account" in st.secrets:
        # Production (Streamlit Cloud)
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"]
        )
        return bigquery.Client(
            credentials=credentials,
            project=st.secrets["gcp_service_account"]["project_id"]
        )
    else:
        # Local development
        credentials_path = Path(__file__).parent.parent.parent / "config" / "bigquery-key.json"
        
        if not credentials_path.exists():
            st.error(f"❌ BigQuery credentials not found at: {credentials_path}")
            st.stop()
        
        return bigquery.Client.from_service_account_json(str(credentials_path))
```

---

## Étape 2 : Pousser sur GitHub

```bash
cd /Users/paulfrette/Github_pro_folder/battlefield_meta_aggregator

# S.A.C.P (Status → Add → Commit → Push)
git status
git add .
git commit -m "feat: Prepare for Streamlit Cloud deployment"
git push origin main
```

---

## Étape 3 : Déployer sur Streamlit Cloud

### 3.1 Créer un compte

1. Aller sur https://streamlit.io/cloud
2. **Sign up with GitHub** (utiliser votre compte GitHub)
3. Autoriser l'accès à vos repos

### 3.2 Déployer l'app

1. Cliquer **"New app"**
2. Sélectionner :
   - **Repository :** `paulfrettepro-collab/battlefield_meta_aggregator`
   - **Branch :** `main`
   - **Main file path :** `dashboard/app.py`
   - **App URL :** `bf6-meta` (ou autre nom)

3. Cliquer **"Advanced settings"**
   - **Python version :** 3.12
   - **Requirements file :** `dashboard/requirements.txt`

4. Cliquer **"Deploy"**

### 3.3 Ajouter les secrets BigQuery

1. Une fois déployé, cliquer sur **⚙️ Settings** (en haut à droite)
2. Aller dans **"Secrets"**
3. Copier le contenu de votre fichier `config/bigquery-key.json`
4. Coller dans le format suivant :

```toml
[gcp_service_account]
type = "service_account"
project_id = "battlefield-meta-aggregator"
private_key_id = "COPIER_ICI"
private_key = "-----BEGIN PRIVATE KEY-----\nCOPIER_ICI\n-----END PRIVATE KEY-----\n"
client_email = "COPIER_ICI"
client_id = "COPIER_ICI"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "COPIER_ICI"
```

5. **Save**

### 3.4 Reboot l'app

L'app va redémarrer automatiquement avec les secrets.

---

## Étape 4 : Tester

Votre app sera accessible sur :
```
https://bf6-meta.streamlit.app
```

Ou l'URL que vous avez choisie.

---

## 🔧 Troubleshooting

### Erreur : "BigQuery credentials not found"

**Cause :** Secrets mal configurés

**Solution :**
1. Vérifier dans Settings → Secrets
2. S'assurer que le format TOML est correct (pas de virgules, utiliser `=`)
3. Reboot l'app

### Erreur : "Module not found"

**Cause :** Dépendances manquantes

**Solution :**
Vérifier `dashboard/requirements.txt` contient :
```
streamlit>=1.28.0
plotly>=5.17.0
pandas>=2.1.0
google-cloud-bigquery>=3.14.0
pandas-gbq>=0.19.0
db-dtypes>=1.1.0
```

### App trop lente

**Cause :** Free tier limité

**Solution :**
- Augmenter le cache TTL : `@st.cache_data(ttl=3600)` (1h)
- Limiter les queries lourdes
- Utiliser LIMIT dans les requêtes SQL

---

## 📊 Monitoring

Une fois déployé, vous pouvez :

1. **Voir les logs** : Settings → Logs
2. **Voir les métriques** : Settings → Analytics
3. **Mettre à jour** : Juste push sur GitHub, auto-deploy !

---

## 🔐 Sécurité

### Ce qui est sécurisé ✅

- Secrets BigQuery non accessibles publiquement
- HTTPS automatique
- Credentials jamais dans le code source

### Ce qui ne l'est PAS ❌

- App accessible par tout le monde (public)
- Pas d'authentification utilisateurs

### Pour ajouter l'authentification (optionnel)

Utiliser `streamlit-authenticator` :
```bash
pip install streamlit-authenticator
```

Voir : https://blog.streamlit.io/streamlit-authenticator-part-1-adding-an-authentication-component-to-your-app/

---

## 🚀 Workflow de déploiement continu

```bash
# 1. Faire des changements en local
code dashboard/app.py

# 2. Tester localement
.venv/bin/streamlit run dashboard/app.py

# 3. Pousser sur GitHub
git add .
git commit -m "feat: Add new feature"
git push origin main

# 4. Streamlit Cloud déploie automatiquement ! ✅
```

---

## 💰 Coûts

**Streamlit Community Cloud :** GRATUIT
**BigQuery :** $0/mois (free tier)

**Total :** $0/mois 🎉

---

**URL finale :** https://bf6-meta.streamlit.app (à partager avec le monde !)

---

*Guide créé le 26 octobre 2025*

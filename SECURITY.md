# 🔐 Politique de Sécurité

## Fichiers Sensibles Protégés

Ce projet utilise **.gitignore** pour empêcher l'exposition de données sensibles. Les fichiers suivants ne doivent **JAMAIS** être commités :

### 🚨 Credentials GCP
- `config/bigquery-key.json` - Clé service account BigQuery
- `*.json` (sauf `package.json`, `devcontainer.json`)

### 🔑 Variables d'Environnement
- `.env` - Variables locales (PROJECT_ID, GOOGLE_APPLICATION_CREDENTIALS)
- `.env.local`, `.env.production`, etc.

### 🗄️ Secrets Streamlit
- `.streamlit/secrets.toml` - Credentials dashboard
- `dashboard/.streamlit/`

## Configuration Requise

### Pour Développement Local

1. **Créer `config/bigquery-key.json`** (obtenu depuis GCP Console)
2. **Créer `.env`** avec :
   ```bash
   GCP_PROJECT_ID=battlefield-meta-aggregator
   GOOGLE_APPLICATION_CREDENTIALS=config/bigquery-key.json
   ```

### Pour GitHub Actions (CI/CD)

Secrets configurés dans GitHub Settings > Secrets :
- `GCP_SERVICE_ACCOUNT_KEY` : Contenu de `bigquery-key.json` (encodé base64)
- `GCP_PROJECT_ID` : ID projet Google Cloud

### Pour Streamlit Cloud

Dashboard Settings > Secrets > `secrets.toml` :
```toml
[gcp_service_account]
type = "service_account"
project_id = "battlefield-meta-aggregator"
private_key_id = "xxx..."
private_key = "-----BEGIN PRIVATE KEY-----\n..."
client_email = "xxx@xxx.iam.gserviceaccount.com"
client_id = "xxx"
```

## Vérification Avant Commit

**Commandes de sécurité** :

```bash
# Vérifier qu'aucun secret n'est tracké
git ls-files | grep -E "key\.json|secret|\.env"
# Résultat attendu : rien (exit code 1)

# Lister fichiers ignorés (doivent inclure secrets)
git status --ignored

# Vérifier .gitignore
cat .gitignore | grep -E "key\.json|\.env|secrets\.toml"
```

## Reporting Vulnérabilités

Si vous découvrez une faille de sécurité :
1. **NE PAS** créer d'issue publique
2. Contacter via [GitHub Security Advisories](https://github.com/paulfrettepro-collab/battlefield_meta_aggregator/security/advisories)

## Bonnes Pratiques

✅ **À FAIRE** :
- Utiliser GitHub Secrets pour CI/CD
- Rotation des clés GCP tous les 90 jours
- Limiter permissions service account (BigQuery Data Editor uniquement)
- Activer audit logs GCP

❌ **NE JAMAIS** :
- Commit credentials en clair
- Partager clés service account publiquement
- Utiliser clés personnelles (toujours service accounts)
- Laisser credentials dans artifacts GitHub Actions

---

**Dernière mise à jour** : 8 novembre 2025

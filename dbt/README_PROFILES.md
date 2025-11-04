# DBT Profiles Configuration

## 🔧 Usage Local (Development)

Pour utiliser DBT localement, **renommer** `profiles.yml.local` → `profiles.yml` :

```bash
cd dbt/
cp profiles.yml.local profiles.yml
# OU
mv profiles.yml.local profiles.yml
```

Le fichier `profiles.yml` pointe vers `../config/bigquery-key.json` (clé locale).

⚠️ **NE PAS COMMIT** `profiles.yml` (déjà dans `.gitignore`).

---

## 🤖 Usage CI/CD (GitHub Actions)

Le workflow GitHub Actions **crée automatiquement** `~/.dbt/profiles.yml` avec :
- Service account depuis secret `GCP_SERVICE_ACCOUNT_KEY`
- Target : `prod`
- Dataset : `bf6_meta`

**Aucune action requise** pour CI/CD.

---

## 🏗️ Structure

```
dbt/
├── profiles.yml.local    # Template pour dev local (committé)
├── profiles.yml          # Fichier actif local (ignoré par git)
└── README_PROFILES.md    # Ce fichier
```

~/.dbt/
└── profiles.yml          # Créé par GitHub Actions (CI/CD uniquement)
```

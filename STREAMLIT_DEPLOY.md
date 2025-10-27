# 🚀 Streamlit Cloud Deployment Guide

## Quick Deploy (5 minutes)

### Step 1: Push to GitHub ✅

```bash
git add -A
git commit -m "feat: Add Streamlit Cloud support with secrets management"
git push origin main
```

### Step 2: Deploy on Streamlit Cloud

1. Go to **https://share.streamlit.io/**
2. Click **"New app"**
3. Select repository: `paulfrettepro-collab/battlefield_meta_aggregator`
4. Main file path: `dashboard/app.py`
5. Click **"Deploy"**

### Step 3: Configure BigQuery Secrets

1. In your deployed app, click **⚙️ Settings**
2. Go to **"Secrets"** section
3. Paste your BigQuery credentials in TOML format:

```toml
[gcp_service_account]
type = "service_account"
project_id = "battlefield-meta-aggregator"
private_key_id = "YOUR_PRIVATE_KEY_ID"
private_key = "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----\n"
client_email = "YOUR_EMAIL@battlefield-meta-aggregator.iam.gserviceaccount.com"
client_id = "YOUR_CLIENT_ID"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/YOUR_EMAIL%40battlefield-meta-aggregator.iam.gserviceaccount.com"
universe_domain = "googleapis.com"
```

**To get your credentials:**
```bash
cat config/bigquery-key.json
```

Then copy-paste each field into the TOML format above.

4. Click **"Save"**

### Step 4: Test Your App 🎉

Your app will be available at:
```
https://YOUR-APP-NAME.streamlit.app
```

Example: `https://bf6-meta.streamlit.app`

## Troubleshooting

### Error: "No module named 'google.cloud'"

**Solution**: Check that `dashboard_requirements.txt` is used.

In Streamlit Cloud settings:
- Advanced settings > Python version: `3.12`
- Advanced settings > Requirements file: `dashboard_requirements.txt`

### Error: "BigQuery credentials not found"

**Solution**: Verify secrets are configured correctly in Streamlit Cloud dashboard.

The secret must be named exactly `gcp_service_account` (in square brackets).

### Error: "Permission denied"

**Solution**: Verify your BigQuery service account has `BigQuery Data Viewer` role:

```bash
gcloud projects add-iam-policy-binding battlefield-meta-aggregator \
  --member="serviceAccount:YOUR_EMAIL@battlefield-meta-aggregator.iam.gserviceaccount.com" \
  --role="roles/bigquery.dataViewer"
```

## Local Testing

Test with secrets before deploying:

```bash
# Ensure .streamlit/secrets.toml exists with your credentials
streamlit run dashboard/app.py
```

The app should work identically in local and cloud environments.

## URLs

- **Local**: http://localhost:8501
- **Network**: http://192.168.1.12:8501
- **Cloud**: https://YOUR-APP-NAME.streamlit.app (after deployment)

---

**Next**: Once deployed, add the public URL to your `readme.md` ! 🚀

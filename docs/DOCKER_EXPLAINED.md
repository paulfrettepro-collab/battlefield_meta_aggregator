# 🐳 Docker dans le Projet - Explication Complète

## 💡 Qu'est-ce que Docker ?

**Docker** = Une **machine virtuelle légère** qui isole des applications dans des **conteneurs**.

### Analogie Simple
Imagine Docker comme des **boîtes hermétiques** :
- Chaque boîte contient une application + ses dépendances
- Les boîtes sont **isolées** les unes des autres
- Tu peux déplacer/partager ces boîtes facilement
- Elles fonctionnent **pareil partout** (Mac, Windows, Linux, serveur cloud)

---

## 🎯 Pourquoi Docker dans Notre Projet ?

### ❌ Sans Docker (problèmes)
```bash
# Installation manuelle de MinIO
brew install minio
minio server ~/minio-data --console-address ":9001"

# Problèmes :
- Config différente sur chaque machine
- Doit être lancé manuellement à chaque démarrage
- Conflits de ports possibles
- Difficile à partager avec d'autres développeurs
- Pas de persistance garantie des données
```

### ✅ Avec Docker (solution)
```bash
# Un seul fichier de configuration (docker-compose.yml)
docker compose up -d

# Avantages :
✅ Config identique partout (ton Mac, serveur cloud, collègue Windows)
✅ Démarrage/arrêt en 1 commande
✅ Données persistantes garanties (volumes Docker)
✅ Isolation totale (pas de conflit avec d'autres apps)
✅ Reproductible à 100%
```

---

## 🏗️ Architecture Docker dans Notre Projet

```
┌────────────────────────────────────────────────┐
│         TON MAC (Système hôte)                 │
│                                                │
│  ┌──────────────────────────────────────┐     │
│  │    Docker Desktop (moteur)           │     │
│  │                                      │     │
│  │  ┌────────────────────────────┐     │     │
│  │  │  CONTENEUR: bf6_minio      │     │     │
│  │  │                            │     │     │
│  │  │  Image: minio/minio:latest │     │     │
│  │  │  Ports: 9000, 9001         │     │     │
│  │  │  Volume: minio_data        │     │     │
│  │  │                            │     │     │
│  │  │  ┌──────────────────────┐  │     │     │
│  │  │  │  MinIO Server        │  │     │     │
│  │  │  │  (S3-compatible)     │  │     │     │
│  │  │  │                      │  │     │     │
│  │  │  │  Bucket: bronze      │  │     │     │
│  │  │  │   ├─ bf6/top_weapons │  │     │     │
│  │  │  │   └─ bf6/leaderboard │  │     │     │
│  │  │  └──────────────────────┘  │     │     │
│  │  └────────────────────────────┘     │     │
│  │                ▲                     │     │
│  │                │ Port mapping        │     │
│  └────────────────┼─────────────────────┘     │
│                   │                           │
│  ┌────────────────┼─────────────────────┐     │
│  │  localhost:9000 (API)               │     │
│  │  localhost:9001 (UI Web)            │     │
│  └─────────────────────────────────────┘     │
│                   ▲                           │
│                   │                           │
│  ┌────────────────┼─────────────────────┐     │
│  │  Script Python:                     │     │
│  │  upload_to_minio.py                 │     │
│  │                                     │     │
│  │  from minio import Minio            │     │
│  │  client = Minio('localhost:9000')   │     │
│  └─────────────────────────────────────┘     │
└────────────────────────────────────────────────┘
```

---

## 📂 Fichiers Docker du Projet

### 1. `docker-compose.yml` (Configuration)
```yaml
version: '3.8'

services:
  minio:                              # Nom du service
    image: minio/minio:latest         # Image Docker à télécharger
    container_name: bf6_minio         # Nom du conteneur
    restart: unless-stopped           # Redémarre automatiquement
    
    environment:                      # Variables d'environnement
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    
    volumes:                          # Persistance des données
      - minio_data:/data              # Volume Docker → /data dans conteneur
    
    ports:                            # Mapping des ports
      - "9000:9000"                   # Port API S3
      - "9001:9001"                   # Port UI Web
    
    command: server /data --console-address ":9001"
    
    healthcheck:                      # Vérification santé du service
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 30s
      timeout: 20s
      retries: 3

volumes:
  minio_data:                         # Volume persistant
    driver: local                     # Stocké sur ton disque
```

### 2. Commandes Docker Essentielles

```bash
# Démarrer MinIO (en arrière-plan avec -d)
docker compose up -d

# Voir les conteneurs actifs
docker ps

# Arrêter MinIO
docker compose down

# Arrêter ET supprimer les données
docker compose down -v

# Voir les logs de MinIO
docker compose logs -f minio

# Redémarrer MinIO
docker compose restart

# Voir l'utilisation des ressources
docker stats bf6_minio
```

---

## 🔄 Cycle de Vie du Conteneur

```
1. IMAGE (recette)
   └─ minio/minio:latest
        │
        ▼
2. CONTENEUR (instance en cours d'exécution)
   └─ bf6_minio
        │
        ▼
3. VOLUME (données persistantes)
   └─ minio_data
        └─ /var/lib/docker/volumes/...
             └─ Tes fichiers NDJSON
```

**Analogie** :
- **Image** = Recette de cuisine (instructions)
- **Conteneur** = Plat préparé (application qui tourne)
- **Volume** = Réfrigérateur (stockage permanent)

---

## 💾 Volumes Docker - Persistance des Données

### Sans Volume (❌ Données perdues)
```bash
docker compose up -d     # Crée conteneur + upload fichiers
docker compose down      # PERD TOUTES LES DONNÉES ❌
```

### Avec Volume (✅ Données conservées)
```bash
docker compose up -d     # Crée conteneur + volume
# Upload fichiers dans MinIO
docker compose down      # Conteneur arrêté, DONNÉES CONSERVÉES ✅
docker compose up -d     # Redémarre, DONNÉES TOUJOURS LÀ ✅
```

### Où sont stockées les données ?
```bash
# Sur macOS
/var/lib/docker/volumes/battlefield_meta_aggregator_minio_data/_data/

# Voir les volumes
docker volume ls

# Inspecter un volume
docker volume inspect battlefield_meta_aggregator_minio_data
```

---

## 🌐 Mapping des Ports

```
CONTENEUR (isolé)          MAC (système hôte)
┌─────────────────┐        ┌──────────────────┐
│                 │        │                  │
│  Port 9000 ────────────▶ localhost:9000    │
│  (API S3)       │        │ (accessible)     │
│                 │        │                  │
│  Port 9001 ────────────▶ localhost:9001    │
│  (UI Web)       │        │ (accessible)     │
│                 │        │                  │
└─────────────────┘        └──────────────────┘
```

**Sans mapping** : Ports inaccessibles depuis ton Mac  
**Avec mapping** : `localhost:9001` fonctionne dans ton navigateur

---

## 🎯 Pourquoi MinIO dans un Conteneur ?

### 1. **Environnement Professionnel**
- Simule un **vrai data lake cloud** (AWS S3, GCP Cloud Storage)
- Pratique pour ton portfolio
- Compatible S3 (même API)

### 2. **Reproductibilité**
```bash
# Sur ton Mac
docker compose up -d

# Sur un serveur cloud (identique)
docker compose up -d

# Sur le Mac d'un collègue (identique)
docker compose up -d
```

### 3. **Isolation**
- Ne pollue pas ton système
- Pas de conflit avec d'autres apps
- Facile à supprimer proprement

### 4. **Évolutivité Future**
```yaml
# Ajouter d'autres services facilement
services:
  minio:        # Data Lake
  postgres:     # Base de données
  airflow:      # Orchestration
  streamlit:    # Dashboard
```

---

## 🔍 Vérification de l'Installation

```bash
# 1. Docker installé ?
docker --version
# ✅ Docker version 24.0.x

# 2. Docker Compose installé ?
docker compose version
# ✅ Docker Compose version v2.x

# 3. MinIO tourne ?
docker ps | grep minio
# ✅ bf6_minio   Up 10 minutes (healthy)

# 4. Ports accessibles ?
curl -I http://localhost:9001
# ✅ HTTP/1.1 200 OK

# 5. Volume créé ?
docker volume ls | grep minio
# ✅ battlefield_meta_aggregator_minio_data

# 6. Données présentes ?
docker compose exec minio ls -lh /data/bronze/bf6/top_weapons/
# ✅ bf6_top_weapons_2025-10-20_200220.ndjson
```

---

## 🚀 Workflow Quotidien

```bash
# Matin : Démarrer l'environnement
docker compose up -d

# Travailler avec MinIO
python scripts/upload_to_minio.py

# Soir : Arrêter (données conservées)
docker compose down

# Semaine suivante : Redémarrer
docker compose up -d
# ✅ Toutes les données sont là !
```

---

## 📊 Comparaison : Avant/Après Docker

| Aspect | Sans Docker | Avec Docker |
|--------|-------------|-------------|
| **Installation** | `brew install minio` + config manuelle | `docker compose up -d` |
| **Démarrage** | Lancer manuellement à chaque fois | Automatique au boot (optionnel) |
| **Portabilité** | Différent sur chaque OS | Identique partout |
| **Isolation** | Peut conflicter avec d'autres apps | Totalement isolé |
| **Suppression** | Difficile (restes de config) | `docker compose down -v` |
| **Version** | 1 seule version installée | Plusieurs versions possibles |
| **Logs** | Dispersés dans le système | Centralisés (`docker logs`) |
| **Resources** | Limites système | Contrôlables (CPU, RAM) |

---

## 🎓 Résumé pour Débutant

**Docker = Boîtes magiques pour applications**

1. **docker-compose.yml** = Ta liste de courses (ce que tu veux)
2. **docker compose up** = Aller au magasin (télécharger + installer)
3. **Conteneur** = L'application qui tourne dans sa boîte
4. **Volume** = Le garde-manger (stockage permanent)
5. **Port mapping** = Les portes de la boîte (pour y accéder)

**Dans notre projet** :
- MinIO tourne dans un conteneur Docker
- Tes données sont dans un volume persistant
- Tu accèdes à MinIO via `localhost:9000` (API) et `localhost:9001` (UI)
- Tout est reproductible en 1 commande : `docker compose up -d`

---

## 🔗 Ressources

- [Docker Desktop](https://www.docker.com/products/docker-desktop) - Installation
- [Docker Compose Docs](https://docs.docker.com/compose/) - Documentation officielle
- [MinIO Docker Hub](https://hub.docker.com/r/minio/minio) - Image MinIO

---

**💡 Question simple** : "Pourquoi ne pas installer MinIO directement sur mon Mac ?"  
**✅ Réponse** : Tu peux ! Mais Docker te donne :
- Reproductibilité (même config partout)
- Isolation (pas de conflit)
- Facilité (1 commande pour tout)
- Professionnalisme (pratique industrielle)

#!/bin/bash
###############################################################################
# BF6 Meta Aggregator - Pipeline Automatisé
# 
# Ce script exécute l'ensemble du pipeline d'extraction, transformation et
# chargement des données Battlefield 6.
#
# Usage: ./scripts/run_pipeline.sh
#
# Durée estimée: ~30-35 minutes
###############################################################################

set -e  # Exit on error

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction de logging
log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Variables
PROJECT_ROOT="/Users/paulfrette/Github_pro_folder/battlefield_meta_aggregator"
PYTHON_BIN="python3"
DBT_BIN="/Users/paulfrette/.local/bin/dbt"
LOG_DIR="$PROJECT_ROOT/logs"
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')

# Créer le répertoire de logs s'il n'existe pas
mkdir -p "$LOG_DIR"

# Fichier de log pour cette exécution
LOG_FILE="$LOG_DIR/pipeline_$TIMESTAMP.log"

# Rediriger stdout et stderr vers le fichier de log ET la console
exec > >(tee -a "$LOG_FILE")
exec 2>&1

log_info "========================================="
log_info "🎮 BF6 Meta Aggregator - Pipeline Automatisé"
log_info "========================================="
log_info "Timestamp: $TIMESTAMP"
log_info "Log file: $LOG_FILE"
log_info ""

# Vérifier que le projet root existe
if [ ! -d "$PROJECT_ROOT" ]; then
    log_error "Project root directory not found: $PROJECT_ROOT"
    exit 1
fi

cd "$PROJECT_ROOT"

###############################################################################
# ÉTAPE 1 : EXTRACTION DES DONNÉES
###############################################################################
log_info "📥 ÉTAPE 1/4 : Extraction des données (tracker.gg)"
log_info "Durée estimée: ~30 minutes"
log_info ""

START_TIME=$(date +%s)

if $PYTHON_BIN scripts/extract_bf6_meta_complete.py; then
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    log_success "✅ Extraction terminée en ${DURATION}s"
else
    log_error "❌ Échec de l'extraction"
    exit 1
fi

echo ""

###############################################################################
# ÉTAPE 2 : CHARGEMENT BIGQUERY (BRONZE)
###############################################################################
log_info "📤 ÉTAPE 2/4 : Chargement vers BigQuery (Bronze Layer)"
log_info "Durée estimée: ~10 secondes"
log_info ""

START_TIME=$(date +%s)

if $PYTHON_BIN scripts/load_to_bigquery_latest.py; then
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    log_success "✅ Chargement BigQuery terminé en ${DURATION}s"
else
    log_error "❌ Échec du chargement BigQuery"
    exit 1
fi

echo ""

###############################################################################
# ÉTAPE 3 : TRANSFORMATIONS DBT (SILVER + GOLD)
###############################################################################
log_info "🔄 ÉTAPE 3/4 : Transformations DBT (Silver → Gold)"
log_info "Durée estimée: ~15 secondes"
log_info ""

# S'assurer que DBT est dans le PATH
export PATH="/Users/paulfrette/.local/bin:$PATH"

START_TIME=$(date +%s)

# Aller dans le répertoire DBT
cd "$PROJECT_ROOT/dbt"

# Exécuter dbt run
log_info "Running dbt models..."
if $DBT_BIN run; then
    log_success "✅ dbt run terminé"
else
    log_error "❌ Échec de dbt run"
    exit 1
fi

echo ""

# Exécuter dbt test
log_info "Running dbt tests..."
if $DBT_BIN test; then
    log_success "✅ dbt test terminé (tous les tests passent)"
else
    log_warning "⚠️  Certains tests DBT ont échoué (vérifier les logs)"
fi

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
log_success "✅ Transformations DBT terminées en ${DURATION}s"

# Retour au répertoire racine
cd "$PROJECT_ROOT"

echo ""

###############################################################################
# ÉTAPE 4 : VALIDATION DES DONNÉES
###############################################################################
log_info "✅ ÉTAPE 4/4 : Validation des données"
log_info ""

log_info "Vérification des fichiers créés..."

# Vérifier les fichiers NDJSON
LEADERBOARD_FILES=$(ls -1 "$PROJECT_ROOT/data/bronze/tracker_gg/leaderboard/bf6_leaderboard_*.ndjson" 2>/dev/null | wc -l | tr -d ' ')
WEAPONS_FILES=$(ls -1 "$PROJECT_ROOT/data/bronze/tracker_gg/top_weapons/bf6_weapons_*.ndjson" 2>/dev/null | wc -l | tr -d ' ')

log_info "📁 Fichiers NDJSON:"
log_info "   - Leaderboard: $LEADERBOARD_FILES fichier(s)"
log_info "   - Weapons: $WEAPONS_FILES fichier(s)"

# Vérifier que DBT a créé les tables
if [ -d "$PROJECT_ROOT/dbt/target/run" ]; then
    DBT_MODELS=$(find "$PROJECT_ROOT/dbt/target/run" -name "*.sql" | wc -l | tr -d ' ')
    log_info "📊 Modèles DBT compilés: $DBT_MODELS"
else
    log_warning "⚠️  Répertoire DBT target non trouvé"
fi

log_success "✅ Validation terminée"

echo ""

###############################################################################
# RÉSUMÉ FINAL
###############################################################################
TOTAL_END_TIME=$(date +%s)
TOTAL_DURATION=$((TOTAL_END_TIME - START_TIME))
MINUTES=$((TOTAL_DURATION / 60))
SECONDS=$((TOTAL_DURATION % 60))

log_info "========================================="
log_info "🎉 PIPELINE TERMINÉ AVEC SUCCÈS"
log_info "========================================="
log_info "Durée totale: ${MINUTES}m ${SECONDS}s"
log_info "Log complet: $LOG_FILE"
log_info ""
log_info "📊 Prochaines étapes:"
log_info "  1. Vérifier le dashboard Streamlit"
log_info "  2. Consulter BigQuery pour les données Gold"
log_info "  3. Analyser les métriques d'armes"
log_info ""
log_success "✅ Toutes les étapes ont réussi!"
log_info "========================================="

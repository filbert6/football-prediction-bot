#!/bin/bash
# 🧪 Script de vérification rapide du système
# Utilisation: bash quick_check.sh

echo "════════════════════════════════════════════════════════════"
echo "🧪 Football Prediction Bot - Vérification rapide"
echo "════════════════════════════════════════════════════════════"

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Compteurs
passed=0
failed=0

# Fonction pour tester
test_cmd() {
    local name=$1
    local cmd=$2
    
    echo -n "Vérification: $name... "
    if eval "$cmd" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ OK${NC}"
        ((passed++))
    else
        echo -e "${RED}❌ FAIL${NC}"
        ((failed++))
    fi
}

# Tests
echo ""
echo "📋 Tests système..."
echo "─────────────────────────────────────────────────────────────"

test_cmd "Python disponible" "python --version"
test_cmd "pip disponible" "pip --version"
test_cmd "Streamlit installé" "python -c 'import streamlit'"
test_cmd "pandas installé" "python -c 'import pandas'"
test_cmd "joblib installé" "python -c 'import joblib'"
test_cmd "numpy installé" "python -c 'import numpy'"

echo ""
echo "📁 Fichiers requis..."
echo "─────────────────────────────────────────────────────────────"

test_cmd "streamlit_app.py existe" "test -f streamlit_app.py"
test_cmd "train_models.py existe" "test -f train_models.py"
test_cmd "test_system.py existe" "test -f test_system.py"
test_cmd "examples.py existe" "test -f examples.py"
test_cmd "prediction_service.py existe" "test -f football_prediction/prediction_service.py"
test_cmd "data_loader.py existe" "test -f football_prediction/data_loader.py"
test_cmd "dummy_model.py existe" "test -f football_prediction/models/dummy_model.py"

echo ""
echo "🤖 Modèles..."
echo "─────────────────────────────────────────────────────────────"

test_cmd "Dossier models_output existe" "test -d football_prediction/models_output"
test_cmd "Modèle dummy entraîné" "test -f football_prediction/models_output/dummy_model.joblib"

echo ""
echo "📚 Documentation..."
echo "─────────────────────────────────────────────────────────────"

test_cmd "README.md existe" "test -f README.md"
test_cmd "SETUP_GUIDE.md existe" "test -f SETUP_GUIDE.md"
test_cmd "INTEGRATION_GUIDE.md existe" "test -f INTEGRATION_GUIDE.md"
test_cmd "CHANGELOG.md existe" "test -f CHANGELOG.md"
test_cmd "FINAL_SUMMARY.md existe" "test -f FINAL_SUMMARY.md"

echo ""
echo "✅ Syntaxe Python..."
echo "─────────────────────────────────────────────────────────────"

test_cmd "streamlit_app.py syntaxe" "python -m py_compile streamlit_app.py"
test_cmd "prediction_service.py syntaxe" "python -m py_compile football_prediction/prediction_service.py"
test_cmd "data_loader.py syntaxe" "python -m py_compile football_prediction/data_loader.py"
test_cmd "examples.py syntaxe" "python -m py_compile examples.py"

echo ""
echo "════════════════════════════════════════════════════════════"
echo "📊 Résumé:"
echo "  ✅ Tests réussis: $passed"
echo "  ❌ Tests échoués: $failed"
echo "════════════════════════════════════════════════════════════"

if [ $failed -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 TOUS LES TESTS SONT PASSÉS!${NC}"
    echo ""
    echo "Prochaines étapes:"
    echo "  1. python train_models.py  # Entraîner les modèles"
    echo "  2. streamlit run streamlit_app.py  # Lancer l'app"
    echo ""
    exit 0
else
    echo ""
    echo -e "${RED}⚠️  CERTAINS TESTS ONT ÉCHOUÉ${NC}"
    echo ""
    echo "Aide:"
    echo "  - Vérifiez les dépendances: pip install -r football_prediction/requirements.txt"
    echo "  - Entraînez les modèles: python train_models.py"
    echo "  - Consultez SETUP_GUIDE.md pour plus d'aide"
    echo ""
    exit 1
fi

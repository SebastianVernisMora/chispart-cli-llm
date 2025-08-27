#!/bin/bash

# Script para ejecutar todos los tests de Chispart Mobile

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🧪 Ejecutando Suite de Tests - Chispart Mobile${NC}"
echo "=================================================="

# Activar entorno virtual si existe
if [ -d "venv" ]; then
    source venv/bin/activate
    echo -e "${GREEN}✅ Entorno virtual activado${NC}"
fi

# Función para mostrar resultados
show_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2 - PASSED${NC}"
    else
        echo -e "${RED}❌ $2 - FAILED${NC}"
    fi
}

# 1. Linting
echo -e "\n${YELLOW}1. Code Linting${NC}"
echo "----------------"

if command -v flake8 &> /dev/null; then
    flake8 core/ app.py 2>/dev/null
    show_result $? "Flake8 Linting"
else
    echo -e "${YELLOW}⚠️  flake8 not installed - skipping${NC}"
fi

if command -v black &> /dev/null; then
    black --check core/ app.py 2>/dev/null
    show_result $? "Black Formatting"
else
    echo -e "${YELLOW}⚠️  black not installed - skipping${NC}"
fi

# 2. Unit Tests
echo -e "\n${YELLOW}2. Unit Tests${NC}"
echo "-------------"
python -m pytest tests/unit/ -v --tb=short -q
show_result $? "Unit Tests"

# 3. Integration Tests
echo -e "\n${YELLOW}3. Integration Tests${NC}"
echo "-------------------"
python -m pytest tests/integration/ -v --tb=short -q
show_result $? "Integration Tests"

# 4. Coverage Report
echo -e "\n${YELLOW}4. Coverage Report${NC}"
echo "------------------"
python -m pytest --cov=core --cov=app --cov-report=term-missing --cov-report=html -q
show_result $? "Coverage Report"

echo -e "\n${GREEN}🎉 Testing Suite Completado${NC}"
echo -e "${BLUE}📊 Reporte HTML disponible en: htmlcov/index.html${NC}"

# Mostrar resumen de cobertura si existe
if [ -f ".coverage" ]; then
    echo -e "\n${BLUE}📈 Resumen de Cobertura:${NC}"
    python -m coverage report --show-missing | tail -n 1
fi

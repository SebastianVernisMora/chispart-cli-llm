#!/bin/bash

# Cambiar al directorio del script para que se pueda ejecutar desde cualquier lugar
cd "$(dirname "$0")"

# Script para ejecutar todos los tests de Chispart Mobile

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}🧪 Ejecutando Suite Completa de Tests - Chispart Mobile${NC}"
echo "============================================================"

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
    echo -e "${CYAN}Ejecutando Flake8...${NC}"
    flake8 core/ app.py 2>/dev/null
    show_result $? "Flake8 Linting"
else
    echo -e "${YELLOW}⚠️  flake8 not installed - skipping${NC}"
fi

if command -v black &> /dev/null; then
    echo -e "${CYAN}Ejecutando Black...${NC}"
    black --check core/ app.py 2>/dev/null
    show_result $? "Black Formatting"
else
    echo -e "${YELLOW}⚠️  black not installed - skipping${NC}"
fi

if command -v mypy &> /dev/null; then
    echo -e "${CYAN}Ejecutando Mypy...${NC}"
    mypy core/ app.py 2>/dev/null
    show_result $? "Mypy Type Checking"
else
    echo -e "${YELLOW}⚠️  mypy not installed - skipping${NC}"
fi

# 2. Unit Tests
echo -e "\n${YELLOW}2. Unit Tests${NC}"
echo "-------------"
echo -e "${CYAN}Ejecutando tests unitarios...${NC}"
python -m pytest tests/unit/ -v
show_result $? "Unit Tests"

# 3. Integration Tests
echo -e "\n${YELLOW}3. Integration Tests${NC}"
echo "-------------------"
echo -e "${CYAN}Ejecutando tests de integración...${NC}"
python -m pytest tests/integration/ -v
show_result $? "Integration Tests"

# 4. PWA Tests
echo -e "\n${YELLOW}4. PWA Tests${NC}"
echo "-------------"
echo -e "${CYAN}Ejecutando tests de PWA...${NC}"
python -m pytest tests/pwa/ -v
show_result $? "PWA Tests"

# 5. Security Tests
echo -e "\n${YELLOW}5. Security Tests${NC}"
echo "----------------"
echo -e "${CYAN}Ejecutando tests de seguridad...${NC}"
python -m pytest tests/security/ -v
show_result $? "Security Tests"

# 6. Performance Tests
echo -e "\n${YELLOW}6. Performance Tests${NC}"
echo "------------------"
echo -e "${CYAN}Ejecutando tests de rendimiento...${NC}"
python -m pytest tests/performance/ -v
show_result $? "Performance Tests"

# 7. Coverage Report
echo -e "\n${YELLOW}7. Coverage Report${NC}"
echo "------------------"
echo -e "${CYAN}Generando reporte de cobertura...${NC}"
python -m pytest --cov=core --cov=app --cov-report=term-missing --cov-report=html
show_result $? "Coverage Report"

echo -e "\n${GREEN}🎉 Testing Suite Completado${NC}"
echo -e "${BLUE}📊 Reporte HTML disponible en: htmlcov/index.html${NC}"

# Mostrar resumen de cobertura si existe
if [ -f ".coverage" ]; then
    echo -e "\n${BLUE}📈 Resumen de Cobertura:${NC}"
    python -m coverage report --show-missing | tail -n 1
fi

# Mostrar resumen de tests
echo -e "\n${PURPLE}📋 Resumen de Tests:${NC}"
echo -e "${CYAN}Unit Tests:${NC} $(python -m pytest tests/unit/ -v --collect-only | grep -c 'collected')"
echo -e "${CYAN}Integration Tests:${NC} $(python -m pytest tests/integration/ -v --collect-only | grep -c 'collected')"
echo -e "${CYAN}PWA Tests:${NC} $(python -m pytest tests/pwa/ -v --collect-only | grep -c 'collected')"
echo -e "${CYAN}Security Tests:${NC} $(python -m pytest tests/security/ -v --collect-only | grep -c 'collected')"
echo -e "${CYAN}Performance Tests:${NC} $(python -m pytest tests/performance/ -v --collect-only | grep -c 'collected')"

echo -e "\n${GREEN}✅ Testing completo finalizado${NC}"

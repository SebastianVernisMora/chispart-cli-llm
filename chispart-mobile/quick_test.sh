#!/bin/bash

# Test rápido para verificar que todo funciona

echo "🚀 Quick Test - Chispart Mobile"
echo "==============================="

# Activar entorno virtual
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Test básico de importación
echo "Testing imports..."
python -c "
try:
    import sys
    sys.path.append('.')
    from core.api_key_manager import APIKeyManager
    from core.config_manager import ConfigManager
    print('✅ Core modules import OK')
except ImportError as e:
    print(f'❌ Import error: {e}')

try:
    from app import app_instance
    print('✅ Flask app import OK')
except ImportError as e:
    print(f'❌ Flask app import error: {e}')
"

# Test básico de pytest
echo -e "\nTesting pytest..."
python -m pytest --version > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ pytest OK"
else
    echo "❌ pytest not working"
fi

# Test de un archivo específico si existe
if [ -f "tests/unit/test_api_key_manager.py" ]; then
    echo -e "\nRunning sample test..."
    python -m pytest tests/unit/test_api_key_manager.py::TestAPIKeyManager::test_init -v
fi

echo -e "\n🎯 Quick test completed!"

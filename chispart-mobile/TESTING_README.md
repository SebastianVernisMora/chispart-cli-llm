# Testing Guide - Chispart Mobile

## 🚀 Quick Start

```bash
# Ejecutar todos los tests
./run_tests.sh

# Test rápido
./quick_test.sh

# Tests específicos
python -m pytest tests/unit/ -v
python -m pytest tests/integration/ -v
```

## 📁 Estructura de Tests

```
tests/
├── unit/                   # Tests unitarios
├── integration/            # Tests de integración
├── security/              # Tests de seguridad
├── pwa/                   # Tests PWA
├── performance/           # Tests de performance
├── fixtures/              # Datos de prueba
└── conftest.py           # Configuración pytest
```

## 🧪 Tipos de Tests

### Unit Tests
- `test_api_key_manager.py` - Tests del gestor de API keys
- `test_config_manager.py` - Tests del gestor de configuración
- `test_pwa_manager.py` - Tests del gestor PWA

### Integration Tests
- `test_flask_app.py` - Tests de la aplicación Flask
- `test_api_endpoints.py` - Tests de endpoints API

## 📊 Coverage

Los reportes de cobertura se generan en:
- Terminal: Resumen en consola
- HTML: `htmlcov/index.html`

## 🔧 Configuración

- `pytest.ini` - Configuración de pytest
- `.flake8` - Configuración de linting
- `pyproject.toml` - Configuración de black

## 📝 Escribir Tests

### Ejemplo de Unit Test

```python
import pytest

class TestMyFeature:
    def test_basic_functionality(self):
        # Arrange
        expected = "expected_result"
        
        # Act
        result = my_function()
        
        # Assert
        assert result == expected
```

### Fixtures Disponibles

- `temp_dir` - Directorio temporal
- `mock_config_dir` - Directorio de configuración mock
- `app_client` - Cliente de testing Flask
- `mock_api_key` - API key de prueba

## 🐛 Debugging Tests

```bash
# Ejecutar con más detalle
python -m pytest -v -s

# Ejecutar test específico
python -m pytest tests/unit/test_api_key_manager.py::TestAPIKeyManager::test_init

# Parar en primer fallo
python -m pytest -x

# Mostrar variables locales en fallos
python -m pytest -l
```

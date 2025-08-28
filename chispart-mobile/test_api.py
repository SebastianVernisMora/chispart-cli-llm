#!/usr/bin/env python3
"""
Test simple para verificar que la API de chat funciona correctamente
"""

import requests
import json


def test_chat_api():
    """Prueba la API de chat directamente"""
    url = "http://127.0.0.1:5001/api/chat"

    data = {
        "message": "Hola, ¿puedes confirmar que estás funcionando correctamente?",
        "api": "blackbox",
        "model": "blackboxai/openai/gpt-3.5-turbo",
        "stream": False,
    }

    headers = {"Content-Type": "application/json"}

    print("🧪 Probando API de chat...")
    print(f"URL: {url}")
    print(f"Datos: {json.dumps(data, indent=2)}")

    try:
        response = requests.post(url, json=data, headers=headers, timeout=30)

        print(f"\n📊 Respuesta HTTP: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")

        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Respuesta exitosa:")
            print(f"API usada: {result.get('api_used', 'N/A')}")
            print(f"Modelo usado: {result.get('model_used', 'N/A')}")
            print(f"Respuesta: {result.get('response', 'N/A')[:200]}...")
            print(f"Tokens: {result.get('usage', {}).get('total_tokens', 'N/A')}")
            return True
        else:
            print(f"\n❌ Error HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error: {error_data}")
            except:
                print(f"Respuesta: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error de conexión: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        return False


def test_config_api():
    """Prueba la API de configuración"""
    url = "http://127.0.0.1:5001/api/config"

    print("\n🔧 Probando API de configuración...")

    try:
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Configuración obtenida:")
            print(
                f"API por defecto: {result.get('config', {}).get('default_api', 'N/A')}"
            )
            print(
                f"Modelo por defecto: {result.get('config', {}).get('default_model', 'N/A')}"
            )
            return True
        else:
            print(f"❌ Error HTTP {response.status_code}: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_api_keys():
    """Prueba la API de claves"""
    url = "http://127.0.0.1:5001/api/api-keys"

    print("\n🔑 Probando API de claves...")

    try:
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            result = response.json()
            providers = result.get("providers", [])
            print(f"✅ Proveedores configurados: {len(providers)}")
            for provider in providers:
                print(
                    f"  - {provider.get('provider', 'N/A')}: {provider.get('validation_status', 'N/A')}"
                )
            return True
        else:
            print(f"❌ Error HTTP {response.status_code}: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Iniciando pruebas de API de Chispart Mobile")
    print("=" * 50)

    # Probar APIs
    config_ok = test_config_api()
    keys_ok = test_api_keys()
    chat_ok = test_chat_api()

    print("\n" + "=" * 50)
    print("📋 Resumen de pruebas:")
    print(f"  Configuración: {'✅' if config_ok else '❌'}")
    print(f"  API Keys: {'✅' if keys_ok else '❌'}")
    print(f"  Chat: {'✅' if chat_ok else '❌'}")

    if all([config_ok, keys_ok, chat_ok]):
        print("\n🎉 ¡Todas las pruebas pasaron! La API está funcionando correctamente.")
    else:
        print("\n⚠️  Algunas pruebas fallaron. Revisa los errores arriba.")

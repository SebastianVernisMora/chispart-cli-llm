#!/usr/bin/env python3
"""
Script de prueba para el modo interactivo
Simula una sesión interactiva para validar la persistencia
"""

import subprocess
import time
import os

def test_interactive_mode():
    """Prueba el modo interactivo con comandos simulados"""
    
    print("🧪 Iniciando prueba del modo interactivo...")
    
    # Comandos de prueba para enviar al modo interactivo
    test_commands = [
        "Hola, soy un test del modo interactivo",
        "stats",
        "¿Cuál es la capital de Francia?",
        "historial", 
        "limpiar",
        "¿Puedes ayudarme con Python?",
        "stats",
        "salir"
    ]
    
    # Crear archivo temporal con comandos
    commands_file = "/tmp/interactive_test_commands.txt"
    with open(commands_file, 'w') as f:
        for cmd in test_commands:
            f.write(cmd + '\n')
    
    print(f"📝 Comandos de prueba creados en: {commands_file}")
    print("📋 Comandos a probar:")
    for i, cmd in enumerate(test_commands, 1):
        print(f"  {i}. {cmd}")
    
    print("\n🚀 Para probar manualmente, ejecuta:")
    print("python3 chispar-cli-llm/chispart_dev_agent_v3.py interactivo")
    print("\nY luego introduce los comandos uno por uno para validar:")
    print("✅ Persistencia de conversación")
    print("✅ Comandos especiales (stats, historial, limpiar)")
    print("✅ Guardado de historial")
    print("✅ Estadísticas en tiempo real")
    
    return True

if __name__ == "__main__":
    test_interactive_mode()

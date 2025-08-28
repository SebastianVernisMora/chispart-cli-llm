from flask import Flask, jsonify, request
from core.shell import InteractiveShell
from core.analyzer import DirectoryAnalyzer
import os

app = Flask(__name__)

# Instancia global del shell para mantener el estado de la sesión.
# Nota: Esto no es seguro para hilos en un entorno de producción real.
interactive_shell = InteractiveShell()

@app.route('/')
def index():
    return "Chispart Cloud Tools - Interactive API"

@app.route('/api/interactive', methods=['POST'])
def interactive_endpoint():
    data = request.json
    if not data or 'input' not in data:
        return jsonify({"error": "Invalid input"}), 400

    user_input = data['input'].strip()

    # Router de comandos
    if user_input.startswith('@analizar'):
        # Comando de análisis de directorio
        parts = user_input.split(' ', 1)
        if len(parts) < 2:
            return jsonify({"status": "error", "output": "Uso: @analizar <directorio>"}), 400

        target_dir = parts[1]
        try:
            # Usar el directorio de trabajo actual del shell como base
            analysis_path = interactive_shell.current_path / target_dir
            analyzer = DirectoryAnalyzer(str(analysis_path))
            analysis_result = analyzer.analyze()

            # Formatear la salida para el JSON
            output = ""
            if analysis_result.get("documentation_summary"):
                output += "--- Documentación Detectada ---\n"
                output += analysis_result["documentation_summary"]
            if analysis_result.get("content_samples"):
                output += "\n--- Fragmentos de Archivos ---\n"
                output += analysis_result["content_samples"]

            if not output:
                output = "Análisis completado. No se encontró documentación prioritaria ni archivos para muestrear."

            return jsonify({"status": "ok", "output": output.strip()})
        except Exception as e:
            return jsonify({"status": "error", "output": str(e)})

    else:
        # Pasar el comando al shell interactivo
        result = interactive_shell.execute(user_input)

        if result["status"] == "passthrough":
            # El shell no manejó el comando, tratarlo como chat
            # En un futuro, esto se pasaría a un LLM
            result["output"] = f"Comando no reconocido o chat: {result['output']}"
            result["status"] = "ok"

        return jsonify(result)

if __name__ == '__main__':
    # Usar el puerto 8080 para evitar conflictos comunes y desactivar el reloader para mantener el estado
    app.run(host='0.0.0.0', port=8080, debug=True, use_reloader=False)

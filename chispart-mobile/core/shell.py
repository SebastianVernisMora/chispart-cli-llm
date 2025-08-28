import os
import subprocess
import re
from collections import deque
from pathlib import Path
from typing import List, Dict, Optional, Tuple

# Comandos seguros permitidos para ejecución directa
COMMAND_WHITELIST = [
    'ls', 'pwd', 'echo', 'cat', 'head', 'tail', 'grep', 'find',
    'git status', 'git diff', 'git log'
]

class InteractiveShell:
    def __init__(self, histmax: int = 300, log_queue=None):
        self.current_path = Path.cwd()
        self.history = deque(maxlen=histmax)
        self.session_vars = {
            "timeout": 45,
            "outmax": 10000,
            "histmax": histmax
        }
        self.log_queue = log_queue

    def execute(self, user_input: str) -> Dict[str, str]:
        """
        Procesa un comando de usuario, lo delega o ejecuta.
        """
        user_input = user_input.strip()
        if not user_input:
            return {"status": "empty"}

        # Añadir al historial (si no es una re-ejecución)
        if not user_input.startswith(('!!', '!run', '!?')):
             self.history.append(user_input)

        # Manejar comandos especiales
        if user_input.startswith('!'):
            return self._handle_shell_command(user_input)
        elif user_input.startswith('cd'):
            return self._handle_cd(user_input)
        elif user_input.startswith('history'):
            return self._handle_history(user_input)
        elif user_input.startswith('set '):
            return self._handle_set(user_input)

        # Si no es un comando especial, se tratará como chat o análisis
        return {"status": "passthrough", "output": user_input}

    def _log(self, message: Dict):
        if self.log_queue:
            self.log_queue.put(message)

    def _handle_shell_command(self, command: str) -> Dict[str, str]:
        """Maneja comandos que empiezan con '!'."""
        self._log({"type": "command", "command": command})
        if command == '!!':
            if len(self.history) > 1:
                # El comando más reciente es '!!', el anterior es el que queremos
                last_command = self.history[-2]
                self.history.append(last_command) # Añadir el comando re-ejecutado
                return self.execute(last_command)

            error_message = "No hay comandos en el historial para re-ejecutar."
            result = {"status": "error", "output": error_message}
            self._log({"type": "output", "status": "error", "output": error_message})
            return result

        elif command.startswith('!run '):
            try:
                index = int(command.split(' ')[1])
                if 1 <= index <= len(self.history):
                    # El historial es 0-indexed, el input es 1-indexed
                    run_command = list(self.history)[index-1]
                    self.history.append(run_command)
                    return self.execute(run_command)

                error_message = f"Índice de historial inválido: {index}"
                result = {"status": "error", "output": error_message}
                self._log({"type": "output", "status": "error", "output": error_message})
                return result
            except (ValueError, IndexError):
                error_message = "Uso: !run <número_de_historial>"
                result = {"status": "error", "output": error_message}
                self._log({"type": "output", "status": "error", "output": error_message})
                return result

        elif command.startswith('!?'):
            match = re.match(r'!\?\s*/(.*?)/(i?)\s*$', command)
            if not match:
                error_message = "Formato de búsqueda inválido. Uso: !? /regex/i"
                result = {"status": "error", "output": error_message}
                self._log({"type": "output", "status": "error", "output": error_message})
                return result

            pattern, flags_str = match.groups()
            flags = re.IGNORECASE if 'i' in flags_str else 0

            try:
                # Buscar hacia atrás en el historial (excluyendo el comando actual)
                for cmd in reversed(list(self.history)[:-1]):
                    if re.search(pattern, cmd, flags):
                        self.history.append(cmd)
                        return self.execute(cmd)

                error_message = f"No se encontró comando que coincida con /{pattern}/"
                result = {"status": "error", "output": error_message}
                self._log({"type": "output", "status": "error", "output": error_message})
                return result
            except re.error as e:
                error_message = f"Error en la expresión regular: {e}"
                result = {"status": "error", "output": error_message}
                self._log({"type": "output", "status": "error", "output": error_message})
                return result

        # Comando normal: !comando
        actual_command = command[1:]
        return self._run_subprocess(actual_command)

    def _run_subprocess(self, command: str) -> Dict[str, str]:
        """Ejecuta un comando en un subproceso de forma segura."""
        self._log({"type": "command", "command": command})
        # Validar contra la whitelist
        command_to_run = command.strip()
        if not any(command_to_run.startswith(prefix) for prefix in COMMAND_WHITELIST):
            error_message = f"Comando no permitido: '{command_to_run}'. Solo se permiten comandos en la lista blanca."
            result = {"status": "error", "output": error_message}
            self._log({"type": "output", "status": "error", "output": error_message})
            return result

        try:
            process = subprocess.run(
                command_to_run,
                shell=True,
                capture_output=True,
                text=True,
                cwd=self.current_path,
                timeout=self.session_vars["timeout"]
            )

            output = process.stdout
            if process.stderr:
                output += f"\n--- STDERR ---\n{process.stderr}"

            if len(output) > self.session_vars["outmax"]:
                output = output[:self.session_vars["outmax"]] + "\n\n[... SALIDA TRUNCADA ...]"

            result = {"status": "ok", "output": output}
            self._log({"type": "output", "status": "ok", "output": output})
            return result

        except subprocess.TimeoutExpired:
            error_message = f"Comando '{command_to_run}' excedió el tiempo límite de {self.session_vars['timeout']}s."
            result = {"status": "error", "output": error_message}
            self._log({"type": "output", "status": "error", "output": error_message})
            return result
        except Exception as e:
            error_message = f"Error ejecutando comando: {e}"
            result = {"status": "error", "output": error_message}
            self._log({"type": "output", "status": "error", "output": error_message})
            return result

    def _handle_cd(self, command: str) -> Dict[str, str]:
        """Maneja el comando 'cd'."""
        self._log({"type": "command", "command": command})
        parts = command.strip().split(' ', 1)
        if len(parts) == 1:
            # 'cd' sin argumentos, ir al home del repo (o donde se inició)
            self.current_path = Path.cwd()
            result = {"status": "ok", "output": f"Directorio actual: {self.current_path}"}
            self._log({"type": "output", "status": "ok", "output": result["output"]})
            return result

        path_str = parts[1]
        try:
            new_path = self.current_path / path_str

            if new_path.is_dir():
                self.current_path = new_path.resolve()
                result = {"status": "ok", "output": f"Directorio actual: {self.current_path}"}
                self._log({"type": "output", "status": "ok", "output": result["output"]})
                return result
            else:
                error_message = f"Directorio no encontrado: {new_path}"
                result = {"status": "error", "output": error_message}
                self._log({"type": "output", "status": "error", "output": error_message})
                return result
        except Exception as e:
            error_message = f"Error en cd: {e}"
            result = {"status": "error", "output": error_message}
            self._log({"type": "output", "status": "error", "output": error_message})
            return result

    def _handle_history(self, command: str) -> Dict[str, str]:
        """Maneja el comando 'history'."""
        self._log({"type": "command", "command": command})
        parts = command.split()

        limit = None
        pattern = None

        # Parsear: history -n 20 /regex/
        if '-n' in parts:
            try:
                limit_index = parts.index('-n') + 1
                limit = int(parts[limit_index])
            except (ValueError, IndexError):
                error_message = "Uso: history -n <número>"
                result = {"status": "error", "output": error_message}
                self._log({"type": "output", "status": "error", "output": error_message})
                return result

        for part in parts:
            if part.startswith('/') and part.endswith('/'):
                pattern = part[1:-1]
                break

        # Filtrar historial
        # Excluimos el comando 'history' actual
        history_list = list(self.history)[:-1]
        if pattern:
            try:
                history_list = [cmd for cmd in history_list if re.search(pattern, cmd)]
            except re.error:
                error_message = "Expresión regular inválida."
                result = {"status": "error", "output": error_message}
                self._log({"type": "output", "status": "error", "output": error_message})
                return result

        if limit:
            history_list = history_list[-limit:]

        # Formatear salida
        output = [f"{i+1}: {cmd}" for i, cmd in enumerate(history_list)]
        result = {"status": "ok", "output": "\n".join(output)}
        self._log({"type": "output", "status": "ok", "output": result["output"]})
        return result

    def _handle_set(self, command: str) -> Dict[str, str]:
        """Maneja el comando 'set'."""
        self._log({"type": "command", "command": command})
        try:
            _, var, value_str = command.split()
            value = int(value_str)
            if var in self.session_vars:
                self.session_vars[var] = value
                if var == 'histmax':
                    self.history = deque(self.history, maxlen=value)
                result = {"status": "ok", "output": f"{var} actualizado a {value}."}
                self._log({"type": "output", "status": "ok", "output": result["output"]})
                return result

            error_message = f"Variable desconocida: {var}"
            result = {"status": "error", "output": error_message}
            self._log({"type": "output", "status": "error", "output": error_message})
            return result
        except (ValueError, IndexError):
            error_message = "Uso: set <variable> <valor_numérico>"
            result = {"status": "error", "output": error_message}
            self._log({"type": "output", "status": "error", "output": error_message})
            return result

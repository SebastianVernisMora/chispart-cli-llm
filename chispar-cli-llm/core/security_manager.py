"""
Sistema de Seguridad para Chispart CLI
Implementa whitelist de comandos y validación de seguridad
"""

import re
import os
import subprocess
import shlex
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from config_extended import SECURITY_CONFIG

@dataclass
class CommandValidation:
    """Resultado de validación de comando"""
    is_allowed: bool
    reason: str
    requires_confirmation: bool = False
    suggested_alternative: Optional[str] = None

class SecurityManager:
    """Gestor de seguridad para comandos del sistema"""
    
    def __init__(self):
        self.whitelist = set(SECURITY_CONFIG['allowed_commands'])
        self.blacklist = set(SECURITY_CONFIG['blocked_commands'])
        self.confirmation_required = set(SECURITY_CONFIG['require_confirmation'])
        self.enabled = SECURITY_CONFIG['whitelist_enabled']
    
    def validate_command(self, command: str) -> CommandValidation:
        """Valida si un comando es seguro para ejecutar"""
        if not self.enabled:
            return CommandValidation(True, "Seguridad deshabilitada")
        
        # Limpiar y parsear comando
        command = command.strip()
        if not command:
            return CommandValidation(False, "Comando vacío")
        
        # Extraer comando base
        try:
            parts = shlex.split(command)
            base_command = parts[0] if parts else ""
        except ValueError:
            return CommandValidation(False, "Comando mal formateado")
        
        # Verificar blacklist primero
        if self._is_blacklisted(base_command, command):
            return CommandValidation(
                False, 
                f"Comando '{base_command}' está en la lista negra por seguridad",
                suggested_alternative=self._get_safe_alternative(base_command)
            )
        
        # Verificar whitelist
        if not self._is_whitelisted(base_command):
            return CommandValidation(
                False,
                f"Comando '{base_command}' no está en la lista blanca",
                suggested_alternative=self._get_safe_alternative(base_command)
            )
        
        # Verificar si requiere confirmación
        requires_confirmation = self._requires_confirmation(base_command, command)
        
        # Validaciones adicionales de seguridad
        security_check = self._additional_security_checks(command)
        if not security_check.is_allowed:
            return security_check
        
        return CommandValidation(
            True, 
            "Comando permitido",
            requires_confirmation=requires_confirmation
        )
    
    def _is_blacklisted(self, base_command: str, full_command: str) -> bool:
        """Verifica si un comando está en la blacklist"""
        # Verificar comando base
        if base_command in self.blacklist:
            return True
        
        # Verificar patrones peligrosos
        dangerous_patterns = [
            r'sudo\s+',  # sudo seguido de espacio
            r'su\s+',    # su seguido de espacio
            r'rm\s+-rf\s+/',  # rm -rf /
            r'chmod\s+777',   # chmod 777
            r'>\s*/dev/',     # redirección a /dev/
            r'\|\s*sh',       # pipe a shell
            r'\|\s*bash',     # pipe a bash
            r'`.*`',          # command substitution
            r'\$\(',          # command substitution
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, full_command, re.IGNORECASE):
                return True
        
        return False
    
    def _is_whitelisted(self, base_command: str) -> bool:
        """Verifica si un comando está en la whitelist"""
        return base_command in self.whitelist
    
    def _requires_confirmation(self, base_command: str, full_command: str) -> bool:
        """Verifica si un comando requiere confirmación"""
        # Verificar comando base
        if base_command in self.confirmation_required:
            return True
        
        # Verificar patrones que requieren confirmación
        confirmation_patterns = [
            r'rm\s+.*',       # cualquier rm
            r'mv\s+.*',       # cualquier mv
            r'cp\s+-r\s+.*',  # cp recursivo
            r'git\s+push',    # git push
            r'docker\s+run',  # docker run
        ]
        
        for pattern in confirmation_patterns:
            if re.search(pattern, full_command, re.IGNORECASE):
                return True
        
        return False
    
    def _additional_security_checks(self, command: str) -> CommandValidation:
        """Verificaciones adicionales de seguridad"""
        
        # Verificar longitud del comando
        if len(command) > 1000:
            return CommandValidation(False, "Comando demasiado largo")
        
        # Verificar caracteres sospechosos
        suspicious_chars = ['&', ';', '|', '>', '<', '`', '$']
        suspicious_found = [char for char in suspicious_chars if char in command]
        
        if suspicious_found:
            # Permitir algunos casos seguros
            safe_patterns = [
                r'grep.*\|.*less',  # grep | less
                r'cat.*\|.*grep',   # cat | grep
                r'ls.*\|.*grep',    # ls | grep
                r'find.*\|.*grep',  # find | grep
                r'echo.*>.*\.txt',  # echo > file.txt
            ]
            
            is_safe = any(re.search(pattern, command) for pattern in safe_patterns)
            
            if not is_safe:
                return CommandValidation(
                    False,
                    f"Caracteres potencialmente peligrosos: {', '.join(suspicious_found)}"
                )
        
        # Verificar paths absolutos peligrosos
        dangerous_paths = ['/etc/', '/usr/bin/', '/bin/', '/sbin/', '/root/']
        for path in dangerous_paths:
            if path in command and ('rm' in command or 'mv' in command or 'chmod' in command):
                return CommandValidation(
                    False,
                    f"Operación peligrosa en directorio del sistema: {path}"
                )
        
        return CommandValidation(True, "Verificaciones adicionales pasadas")
    
    def _get_safe_alternative(self, command: str) -> Optional[str]:
        """Sugiere alternativas seguras para comandos no permitidos"""
        alternatives = {
            'sudo': 'Ejecuta el comando sin sudo o configura permisos apropiados',
            'su': 'Usa tu usuario actual o configura permisos apropiados',
            'passwd': 'Cambia la contraseña desde la configuración del sistema',
            'useradd': 'Gestiona usuarios desde la interfaz del sistema',
            'systemctl': 'Usa herramientas de monitoreo en lugar de controlar servicios',
            'mount': 'Los dispositivos se montan automáticamente',
            'iptables': 'Configura el firewall desde la interfaz del sistema',
            'nc': 'Usa curl o wget para conexiones de red',
            'nmap': 'Usa herramientas de diagnóstico de red más específicas'
        }
        
        return alternatives.get(command)
    
    def execute_safe_command(self, command: str, working_dir: str = None) -> Tuple[bool, str, str]:
        """Ejecuta un comando de forma segura"""
        validation = self.validate_command(command)
        
        if not validation.is_allowed:
            return False, "", f"Comando no permitido: {validation.reason}"
        
        try:
            # Configurar entorno seguro
            env = os.environ.copy()
            
            # Limitar variables de entorno peligrosas
            dangerous_env_vars = ['LD_PRELOAD', 'LD_LIBRARY_PATH', 'PATH']
            for var in dangerous_env_vars:
                if var in env and var != 'PATH':
                    del env[var]
            
            # Ejecutar comando con timeout
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,  # Timeout de 30 segundos
                cwd=working_dir,
                env=env
            )
            
            return True, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            return False, "", "Comando excedió el tiempo límite (30s)"
        except Exception as e:
            return False, "", f"Error ejecutando comando: {str(e)}"
    
    def add_to_whitelist(self, command: str) -> bool:
        """Añade un comando a la whitelist (solo para administradores)"""
        if command not in self.blacklist:
            self.whitelist.add(command)
            return True
        return False
    
    def remove_from_whitelist(self, command: str) -> bool:
        """Remueve un comando de la whitelist"""
        if command in self.whitelist:
            self.whitelist.remove(command)
            return True
        return False
    
    def get_security_status(self) -> Dict:
        """Obtiene el estado actual de la seguridad"""
        return {
            'enabled': self.enabled,
            'whitelist_count': len(self.whitelist),
            'blacklist_count': len(self.blacklist),
            'confirmation_required_count': len(self.confirmation_required),
            'whitelist': sorted(list(self.whitelist)),
            'blacklist': sorted(list(self.blacklist))
        }
    
    def enable_security(self):
        """Habilita el sistema de seguridad"""
        self.enabled = True
    
    def disable_security(self):
        """Deshabilita el sistema de seguridad (no recomendado)"""
        self.enabled = False

# Instancia global del gestor de seguridad
security_manager = SecurityManager()

"""
Sistema de Split Chat para Chispart CLI
Permite crear múltiples sesiones de chat paralelas y fusionarlas
"""

import json
import os
import time
import threading
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import subprocess
import signal
import psutil

@dataclass
class ChatSession:
    """Representa una sesión de chat"""
    id: str
    name: str
    port: int
    pid: Optional[int]
    created_at: str
    last_activity: str
    messages: List[Dict[str, Any]]
    profile: Optional[str] = None
    model: Optional[str] = None
    status: str = "active"

class SplitChatManager:
    """Gestor de sesiones de chat paralelas"""
    
    def __init__(self, base_port: int = 5001, max_splits: int = 5):
        self.base_port = base_port
        self.max_splits = max_splits
        self.sessions: Dict[str, ChatSession] = {}
        self.sessions_file = "split_chat_sessions.json"
        self.load_sessions()
    
    def create_split_chat(self, name: str, profile: Optional[str] = None, 
                         model: Optional[str] = None) -> Optional[ChatSession]:
        """Crea una nueva sesión de chat split"""
        if len(self.sessions) >= self.max_splits:
            return None
        
        # Encontrar puerto disponible
        port = self._find_available_port()
        if not port:
            return None
        
        # Crear sesión
        session_id = str(uuid.uuid4())[:8]
        session = ChatSession(
            id=session_id,
            name=name,
            port=port,
            pid=None,
            created_at=datetime.now().isoformat(),
            last_activity=datetime.now().isoformat(),
            messages=[],
            profile=profile,
            model=model
        )
        
        # Iniciar servidor Flask para esta sesión
        if self._start_chat_server(session):
            self.sessions[session_id] = session
            self.save_sessions()
            return session
        
        return None
    
    def _find_available_port(self) -> Optional[int]:
        """Encuentra un puerto disponible"""
        for i in range(self.max_splits):
            port = self.base_port + i
            if not self._is_port_in_use(port):
                return port
        return None
    
    def _is_port_in_use(self, port: int) -> bool:
        """Verifica si un puerto está en uso"""
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('localhost', port))
                return False
            except OSError:
                return True
    
    def _start_chat_server(self, session: ChatSession) -> bool:
        """Inicia un servidor Flask para la sesión de chat"""
        try:
            # Comando para iniciar el servidor
            cmd = [
                'python', '-c', f'''
import sys
sys.path.append(".")
from core.split_chat_server import create_split_server
app = create_split_server("{session.id}", "{session.profile or ''}", "{session.model or ''}")
app.run(host="0.0.0.0", port={session.port}, debug=False)
'''
            ]
            
            # Iniciar proceso
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid
            )
            
            # Esperar un momento para verificar que inició correctamente
            time.sleep(2)
            if process.poll() is None:
                session.pid = process.pid
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Error iniciando servidor: {e}")
            return False
    
    def stop_split_chat(self, session_id: str) -> bool:
        """Detiene una sesión de chat split"""
        session = self.sessions.get(session_id)
        if not session or not session.pid:
            return False
        
        try:
            # Terminar proceso y sus hijos
            parent = psutil.Process(session.pid)
            children = parent.children(recursive=True)
            for child in children:
                child.terminate()
            parent.terminate()
            
            # Esperar a que termine
            parent.wait(timeout=5)
            
            session.status = "stopped"
            session.pid = None
            self.save_sessions()
            return True
            
        except (psutil.NoSuchProcess, psutil.TimeoutExpired):
            # El proceso ya no existe o no terminó a tiempo
            session.status = "stopped"
            session.pid = None
            self.save_sessions()
            return True
        except Exception as e:
            print(f"Error deteniendo sesión: {e}")
            return False
    
    def list_sessions(self) -> List[ChatSession]:
        """Lista todas las sesiones activas"""
        # Actualizar estado de las sesiones
        self._update_sessions_status()
        return list(self.sessions.values())
    
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Obtiene una sesión específica"""
        return self.sessions.get(session_id)
    
    def merge_chats(self, session_ids: List[str], new_name: str = "Merged Chat") -> Optional[str]:
        """Fusiona múltiples chats en uno nuevo"""
        if len(session_ids) < 2:
            return None
        
        # Obtener sesiones
        sessions_to_merge = []
        for sid in session_ids:
            session = self.sessions.get(sid)
            if session:
                sessions_to_merge.append(session)
        
        if len(sessions_to_merge) < 2:
            return None
        
        # Crear contexto fusionado
        merged_context = self._create_merged_context(sessions_to_merge)
        
        # Crear nueva sesión con el contexto fusionado
        merged_session = self.create_split_chat(new_name)
        if merged_session:
            # Añadir contexto inicial
            initial_message = {
                "role": "system",
                "content": merged_context,
                "timestamp": datetime.now().isoformat(),
                "type": "merged_context"
            }
            merged_session.messages.append(initial_message)
            self.save_sessions()
            return merged_session.id
        
        return None
    
    def _create_merged_context(self, sessions: List[ChatSession]) -> str:
        """Crea un contexto fusionado de múltiples sesiones"""
        context_parts = []
        
        context_parts.append("# Contexto Fusionado de Múltiples Chats\n")
        context_parts.append("Este chat fusiona el contexto de las siguientes sesiones:\n")
        
        for i, session in enumerate(sessions, 1):
            context_parts.append(f"\n## Sesión {i}: {session.name}")
            context_parts.append(f"- ID: {session.id}")
            context_parts.append(f"- Perfil: {session.profile or 'Ninguno'}")
            context_parts.append(f"- Modelo: {session.model or 'Por defecto'}")
            context_parts.append(f"- Creada: {session.created_at}")
            context_parts.append(f"- Mensajes: {len(session.messages)}")
            
            # Añadir últimos mensajes importantes
            if session.messages:
                context_parts.append("\n### Últimos mensajes relevantes:")
                recent_messages = session.messages[-5:]  # Últimos 5 mensajes
                for msg in recent_messages:
                    if msg.get("role") == "user":
                        content = msg.get("content", "")[:200]  # Limitar longitud
                        context_parts.append(f"**Usuario**: {content}...")
                    elif msg.get("role") == "assistant":
                        content = msg.get("content", "")[:300]  # Limitar longitud
                        context_parts.append(f"**Asistente**: {content}...")
        
        context_parts.append("\n---\n")
        context_parts.append("Por favor, continúa la conversación considerando todo este contexto.")
        
        return "\n".join(context_parts)
    
    def _update_sessions_status(self):
        """Actualiza el estado de todas las sesiones"""
        for session in self.sessions.values():
            if session.pid:
                try:
                    process = psutil.Process(session.pid)
                    if process.is_running():
                        session.status = "active"
                    else:
                        session.status = "stopped"
                        session.pid = None
                except psutil.NoSuchProcess:
                    session.status = "stopped"
                    session.pid = None
    
    def cleanup_inactive_sessions(self):
        """Limpia sesiones inactivas"""
        to_remove = []
        for session_id, session in self.sessions.items():
            if session.status == "stopped" and not session.pid:
                # Verificar si ha estado inactiva por mucho tiempo
                last_activity = datetime.fromisoformat(session.last_activity)
                if (datetime.now() - last_activity).total_seconds() > 3600:  # 1 hora
                    to_remove.append(session_id)
        
        for session_id in to_remove:
            del self.sessions[session_id]
        
        if to_remove:
            self.save_sessions()
    
    def save_sessions(self):
        """Guarda las sesiones en archivo"""
        try:
            sessions_data = {}
            for sid, session in self.sessions.items():
                sessions_data[sid] = asdict(session)
            
            with open(self.sessions_file, 'w') as f:
                json.dump(sessions_data, f, indent=2)
        except Exception as e:
            print(f"Error guardando sesiones: {e}")
    
    def load_sessions(self):
        """Carga las sesiones desde archivo"""
        try:
            if os.path.exists(self.sessions_file):
                with open(self.sessions_file, 'r') as f:
                    sessions_data = json.load(f)
                
                for sid, data in sessions_data.items():
                    session = ChatSession(**data)
                    # Marcar como detenida al cargar (se verificará después)
                    session.status = "stopped"
                    session.pid = None
                    self.sessions[sid] = session
        except Exception as e:
            print(f"Error cargando sesiones: {e}")

# Instancia global del gestor
split_chat_manager = SplitChatManager()

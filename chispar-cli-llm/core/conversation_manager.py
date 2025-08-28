"""
Gestor de Conversaciones para Chispart CLI
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

class ConversationManager:
    """Gestor de conversaciones y historial"""
    
    def __init__(self):
        self.history_file = "chat_history.json"
    
    def save_conversation(self, conversation: Dict[str, Any]):
        """Guarda una conversación en el historial"""
        try:
            # Cargar historial existente
            history = self.load_history()
            
            # Añadir timestamp si no existe
            if "timestamp" not in conversation:
                conversation["timestamp"] = datetime.now().isoformat()
            
            # Añadir conversación
            history.append(conversation)
            
            # Guardar historial actualizado
            with open(self.history_file, 'w') as f:
                json.dump(history, f, indent=2)
                
        except Exception as e:
            print(f"Error guardando conversación: {e}")
    
    def load_history(self) -> List[Dict[str, Any]]:
        """Carga el historial de conversaciones"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error cargando historial: {e}")
        
        return []
    
    def get_recent_conversations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtiene las conversaciones más recientes"""
        history = self.load_history()
        return history[-limit:] if history else []
    
    def clear_history(self):
        """Limpia el historial de conversaciones"""
        try:
            if os.path.exists(self.history_file):
                os.remove(self.history_file)
        except Exception as e:
            print(f"Error limpiando historial: {e}")
    
    def search_conversations(self, query: str) -> List[Dict[str, Any]]:
        """Busca conversaciones que contengan el query"""
        history = self.load_history()
        results = []
        
        for conv in history:
            # Buscar en mensaje y respuesta
            message = conv.get("message", "").lower()
            response = conv.get("response", "").lower()
            
            if query.lower() in message or query.lower() in response:
                results.append(conv)
        
        return results

# Instancia global
conversation_manager = ConversationManager()

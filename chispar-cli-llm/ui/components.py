"""
Componentes de interfaz de usuario modernos y reutilizables para Chispart CLI
"""

import os
import time
from typing import Dict, List, Optional, Any, Union
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
from rich.text import Text
from rich.markdown import Markdown
from rich.align import Align
from rich.columns import Columns
from rich.layout import Layout
from rich.live import Live
from rich.spinner import Spinner

from .theme_manager import get_rich_theme, get_theme

class ChispartConsole:
    """Console personalizada de Chispart con tema integrado"""
    
    def __init__(self, force_terminal: Optional[bool] = None):
        self.theme = get_rich_theme()
        self.console = Console(theme=self.theme, force_terminal=force_terminal)
        self.colors = get_theme()
    
    def print(self, *args, **kwargs):
        """Print con tema aplicado"""
        self.console.print(*args, **kwargs)
    
    def status(self, *args, **kwargs):
        """Status con tema aplicado"""
        return self.console.status(*args, **kwargs)
    
    def input(self, prompt: str = "") -> str:
        """Input con tema aplicado"""
        return self.console.input(f"[chispart.brand]{prompt}[/]")

# Instancia global de console
console = ChispartConsole()

def create_panel(
    content: Union[str, Text, Markdown],
    title: Optional[str] = None,
    subtitle: Optional[str] = None,
    style: str = "panel.border",
    title_style: str = "panel.title",
    expand: bool = True,
    padding: tuple = (1, 2)
) -> Panel:
    """Crea un panel con el tema actual aplicado"""
    return Panel(
        content,
        title=title,
        subtitle=subtitle,
        border_style=style,
        title_align="left",
        expand=expand,
        padding=padding,
        style=title_style if title else None
    )

def create_table(
    title: Optional[str] = None,
    show_header: bool = True,
    show_lines: bool = False,
    expand: bool = True
) -> Table:
    """Crea una tabla con el tema actual aplicado"""
    table = Table(
        title=title,
        show_header=show_header,
        show_lines=show_lines,
        expand=expand,
        header_style="table.header",
        row_styles=["table.row", "table.row_alt"]
    )
    return table

def create_progress() -> Progress:
    """Crea una barra de progreso con el tema actual aplicado"""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(style="progress.bar", complete_style="progress.complete"),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=console.console
    )

def show_banner(style: str = "neon", show_info: bool = True):
    """Muestra el banner de Chispart con estilo moderno"""
    colors = get_theme()
    
    if style == "neon":
        banner_text = f"""
[{colors['primary']}]  ██████╗██╗  ██╗██╗███████╗██████╗  █████╗ ██████╗ ████████╗[/]
[{colors['secondary']}] ██╔════╝██║  ██║██║██╔════╝██╔══██╗██╔══██╗██╔══██╗╚══██╔══╝[/]
[{colors['accent']}] ██║     ███████║██║███████╗██████╔╝███████║██████╔╝   ██║   [/]
[{colors['info']}] ██║     ██╔══██║██║╚════██║██╔═══╝ ██╔══██║██╔══██╗   ██║   [/]
[{colors['primary']}] ╚██████╗██║  ██║██║███████║██║     ██║  ██║██║  ██║   ██║   [/]
[{colors['secondary']}]  ╚═════╝╚═╝  ╚═╝╚═╝╚══════╝╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   [/]
"""
    elif style == "minimal":
        banner_text = f"[{colors['primary']}]🚀 CHISPART CLI[/] [{colors['secondary']}]- Interfaz Conversacional con IA Híbrida[/]"
    else:
        banner_text = f"[{colors['primary']}]CHISPART[/] [{colors['accent']}]CLI[/]"
    
    panel_content = banner_text
    
    if show_info:
        info_text = f"""
[{colors['dim']}]Versión 2.0.0 - CLI Universal para LLMs[/]
[{colors['info']}]🌐 Multi-API[/] [{colors['success']}]📱 Mobile-First[/] [{colors['accent']}]⚡ Ultra-Rápido[/]

[{colors['dim']}]Escribe [/][{colors['primary']}]chispart --help[/][{colors['dim']}] para ver todos los comandos disponibles[/]
"""
        panel_content = f"{banner_text}\n{info_text}"
    
    console.print(create_panel(
        panel_content,
        title="🤖 Bienvenido a Chispart",
        style="chispart.brand",
        title_style="chispart.title"
    ))

def show_status(message: str, status_type: str = "info"):
    """Muestra un mensaje de estado con iconos y colores"""
    icons = {
        "info": "ℹ️",
        "success": "✅",
        "warning": "⚠️",
        "error": "❌",
        "loading": "⏳",
        "api": "🤖",
        "file": "📁",
        "network": "🌐"
    }
    
    styles = {
        "info": "chispart.status",
        "success": "chispart.success",
        "warning": "chispart.warning",
        "error": "chispart.error",
        "loading": "chispart.status",
        "api": "chispart.highlight",
        "file": "chispart.status",
        "network": "chispart.status"
    }
    
    icon = icons.get(status_type, "•")
    style = styles.get(status_type, "chispart.status")
    
    console.print(f"[{style}]{icon} {message}[/]")

def show_error(message: str, suggestion: Optional[str] = None):
    """Muestra un error con sugerencia opcional"""
    error_panel = f"[chispart.error]❌ Error: {message}[/]"
    
    if suggestion:
        error_panel += f"\n\n[chispart.dim]💡 Sugerencia: {suggestion}[/]"
    
    console.print(create_panel(
        error_panel,
        title="Error",
        style="error",
        title_style="chispart.error"
    ))

def show_success(message: str, details: Optional[str] = None):
    """Muestra un mensaje de éxito"""
    success_panel = f"[chispart.success]✅ {message}[/]"
    
    if details:
        success_panel += f"\n\n[chispart.dim]{details}[/]"
    
    console.print(create_panel(
        success_panel,
        title="Éxito",
        style="success",
        title_style="chispart.success"
    ))

def show_warning(message: str, action: Optional[str] = None):
    """Muestra una advertencia"""
    warning_panel = f"[chispart.warning]⚠️ {message}[/]"
    
    if action:
        warning_panel += f"\n\n[chispart.dim]🔧 Acción recomendada: {action}[/]"
    
    console.print(create_panel(
        warning_panel,
        title="Advertencia",
        style="warning",
        title_style="chispart.warning"
    ))

def show_info(message: str, extra_info: Optional[str] = None):
    """Muestra información"""
    info_panel = f"[chispart.status]ℹ️ {message}[/]"
    
    if extra_info:
        info_panel += f"\n\n[chispart.dim]{extra_info}[/]"
    
    console.print(create_panel(
        info_panel,
        title="Información",
        style="info",
        title_style="chispart.status"
    ))

def show_api_response(
    content: str,
    api_name: str,
    model: str,
    usage: Optional[Dict[str, Any]] = None,
    filename: Optional[str] = None
):
    """Muestra una respuesta de API con formato mejorado"""
    
    # Determinar el estilo de la API
    api_styles = {
        "openai": "api.openai",
        "anthropic": "api.anthropic", 
        "groq": "api.groq",
        "together": "api.together",
        "blackbox": "api.blackbox",
        "chispart": "api.chispart"
    }
    
    api_style = api_styles.get(api_name.lower(), "chispart.brand")
    
    # Crear título con información de la API
    title_parts = [f"🤖 Respuesta de {api_name}"]
    if filename:
        title_parts.append(f"📁 {filename}")
    
    title = " - ".join(title_parts)
    
    # Crear subtítulo con modelo y uso
    subtitle_parts = [f"Modelo: {model}"]
    if usage and usage.get('total_tokens'):
        subtitle_parts.append(f"Tokens: {usage['total_tokens']}")
    
    subtitle = " | ".join(subtitle_parts)
    
    # Mostrar la respuesta
    console.print(create_panel(
        Markdown(content),
        title=title,
        subtitle=subtitle,
        style=api_style,
        title_style="chispart.title"
    ))

def show_models_table(models: Dict[str, str], api_name: str, default_model: str):
    """Muestra una tabla de modelos disponibles"""
    table = create_table(
        title=f"🤖 Modelos Disponibles para {api_name}",
        show_lines=True
    )
    
    table.add_column("Nombre", style="chispart.brand", width=20)
    table.add_column("ID del Modelo", style="chispart.status", width=40)
    table.add_column("Estado", style="chispart.success", width=15)
    table.add_column("Descripción", style="chispart.dim")
    
    # Descripciones de modelos
    descriptions = {
        "gpt-4": "🧠 Modelo más potente de OpenAI",
        "gpt-4o": "⚡ GPT-4 Optimizado - Más rápido",
        "gpt-4-turbo": "🚀 GPT-4 Turbo - Velocidad mejorada",
        "gpt-3.5-turbo": "💨 Rápido y eficiente",
        "claude-3.5-sonnet": "🎭 Claude más avanzado",
        "claude-3-opus": "🎨 Más creativo de Anthropic",
        "llama-3.1-70b": "🦙 Modelo grande de Meta",
        "mixtral-8x7b": "🔀 Mezcla de expertos",
        "gemini-2.5-flash": "⚡ Gemini más rápido"
    }
    
    for name, model_id in models.items():
        status = "🌟 Por defecto" if name == default_model else "✅ Disponible"
        description = descriptions.get(name, f"Modelo de {api_name}")
        
        table.add_row(name, model_id, status, description)
    
    console.print(table)
    console.print(f"\n[chispart.dim]💡 Modelo por defecto: [/][chispart.brand]{default_model}[/]")

def show_history_table(conversations: List[Dict[str, Any]], limit: int):
    """Muestra una tabla del historial de conversaciones"""
    colors = get_theme()
    table = create_table(
        title=f"📚 Historial de Conversaciones (últimas {limit})",
        show_lines=True
    )
    
    table.add_column("Fecha", style="chispart.status", width=16)
    table.add_column("Tipo", style="chispart.brand", width=12)
    table.add_column("API", style=colors["accent"], width=12)
    table.add_column("Modelo", style=colors["secondary"], width=15)
    table.add_column("Contenido", style="chispart.dim")
    table.add_column("Tokens", style=colors["info"], width=8)
    
    type_icons = {
        "chat": "💬",
        "image": "🖼️",
        "pdf": "📄",
        "interactive": "🔄",
        "web_chat": "🌐"
    }
    
    for conv in conversations:
        # Formatear fecha
        timestamp = conv.get("timestamp", "N/A")
        if timestamp != "N/A":
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                timestamp = dt.strftime("%m-%d %H:%M")
            except:
                timestamp = "N/A"
        
        conv_type = conv.get("type", "N/A")
        api_name = conv.get("api", "N/A")
        model = conv.get("model", "N/A")
        
        # Obtener contenido
        if conv_type in ["image", "pdf"]:
            content = conv.get("file", "N/A")
        else:
            content = conv.get("message", "N/A")
            if len(content) > 50:
                content = content[:47] + "..."
        
        # Obtener tokens
        tokens = "N/A"
        if conv.get("usage") and conv["usage"].get("total_tokens"):
            tokens = str(conv["usage"]["total_tokens"])
        
        # Añadir icono al tipo
        type_with_icon = f"{type_icons.get(conv_type, '•')} {conv_type}"
        
        table.add_row(timestamp, type_with_icon, api_name, model, content, tokens)
    
    console.print(table)

def show_apis_status(apis_info: List[Dict[str, Any]]):
    """Muestra el estado de las APIs disponibles"""
    colors = get_theme()
    table = create_table(
        title="🌐 Estado de APIs Disponibles",
        show_lines=True
    )
    
    table.add_column("API", style="chispart.brand", width=20)
    table.add_column("Estado", style="chispart.success", width=15)
    table.add_column("Características", style=colors["info"])
    table.add_column("Descripción", style="chispart.dim")
    
    status_icons = {
        "configured": "✅ Configurada",
        "not_configured": "❌ Sin configurar"
    }
    
    descriptions = {
        "openai": "🧠 Modelos GPT más avanzados",
        "anthropic": "🎭 Claude - Conversaciones naturales",
        "groq": "⚡ Velocidad ultra-rápida",
        "together": "🤝 Modelos open source",
        "blackbox": "💻 Especializado en código",
        "chispart": "🚀 Acceso unificado a múltiples APIs"
    }
    
    for api in apis_info:
        name = api['name']
        key = api['key']
        status = status_icons.get(api['status'], api['status'])
        
        # Características
        features = []
        if api.get('supports_vision'):
            features.append("🖼️ Imágenes")
        if api.get('supports_pdf'):
            features.append("📄 PDFs")
        features.append("💬 Chat")
        
        characteristics = " | ".join(features)
        description = descriptions.get(key, "API de IA")
        
        table.add_row(name, status, characteristics, description)
    
    console.print(table)

def create_progress_bar(description: str = "Procesando...") -> Progress:
    """Crea una barra de progreso personalizada"""
    colors = get_theme()
    
    return Progress(
        SpinnerColumn(spinner_style=colors["primary"]),
        TextColumn(f"[{colors['info']}]{{task.description}}[/]"),
        BarColumn(
            style=colors["secondary"],
            complete_style=colors["success"],
            finished_style=colors["success"]
        ),
        TaskProgressColumn(style=colors["accent"]),
        TimeElapsedColumn(style=colors["dim"]),
        console=console.console
    )

def create_loading_spinner(message: str = "Procesando...") -> Live:
    """Crea un spinner de carga animado"""
    colors = get_theme()
    spinner = Spinner("dots", style=colors["primary"])
    
    layout = Layout()
    layout.split_column(
        Layout(Align.center(spinner), size=3),
        Layout(Align.center(f"[{colors['primary']}]{message}[/]"), size=1)
    )
    
    return Live(layout, console=console.console, refresh_per_second=10)

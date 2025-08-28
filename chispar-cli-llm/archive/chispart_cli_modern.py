#!/usr/bin/env python3
"""
Chispart CLI Modernizado - Interfaz Universal para LLMs
Versión completamente refactorizada con arquitectura modular
"""

import click
import sys
import os
from typing import Optional

# Importar componentes modernos
from core import ChispartCLIManager, CommandHandler, set_debug_mode
from ui.theme_manager import ThemeManager
from ui.components import console, create_panel
from config import AVAILABLE_APIS, DEFAULT_API

# Configuración global
CONTEXT_SETTINGS = dict(
    help_option_names=['-h', '--help'],
    max_content_width=120
)

# Instancia global del gestor CLI
cli_manager = None

def get_cli_manager(debug: bool = False) -> ChispartCLIManager:
    """Obtiene o crea la instancia del gestor CLI"""
    global cli_manager
    if cli_manager is None:
        cli_manager = ChispartCLIManager(debug_mode=debug)
    return cli_manager

@click.group(context_settings=CONTEXT_SETTINGS)
@click.option('--debug', is_flag=True, help='Activar modo debug con información detallada')
@click.option('--theme', type=click.Choice(['neon', 'dark', 'light', 'retro']), 
              help='Tema de la interfaz')
@click.option('--api', '-a', type=click.Choice(['chispart']), 
              default=DEFAULT_API, help='API por defecto a utilizar')
@click.version_option(version="2.0.0", prog_name="Chispart CLI")
@click.pass_context
def cli(ctx, debug: bool, theme: Optional[str], api: str):
    """
    🚀 Chispart CLI - Interfaz Universal para LLMs
    
    Una herramienta moderna y potente para interactuar con múltiples APIs de IA
    desde tu terminal, optimizada para móviles y escritorio.
    
    \b
    Características principales:
    • Soporte para BlackboxAI/Chispart con múltiples modelos
    • Interfaz moderna con temas personalizables
    • Optimizado para Termux/Android
    • Análisis de imágenes y PDFs
    • Modo interactivo avanzado
    • Historial persistente
    
    \b
    Ejemplos de uso:
      chispart chat "¿Cuál es la capital de Francia?"
      chispart imagen foto.jpg "Describe esta imagen"
      chispart pdf documento.pdf "Resume el contenido"
      chispart interactivo --api openai
    """
    # Configurar contexto
    ctx.ensure_object(dict)
    ctx.obj['debug'] = debug
    ctx.obj['api'] = api
    
    # Configurar debug mode globalmente
    set_debug_mode(debug)
    
    # Inicializar gestor CLI
    manager = get_cli_manager(debug)
    ctx.obj['manager'] = manager
    
    # Configurar tema si se especifica
    if theme:
        manager.theme_manager.set_theme(theme)
    
    # Configurar API actual
    manager.set_current_api(api)
    
    # Mostrar bienvenida solo para comando principal sin subcomandos
    if ctx.invoked_subcommand is None:
        manager.show_welcome()

@cli.command()
@click.argument('mensaje')
@click.option('--modelo', '-m', help='Modelo específico a utilizar')
@click.option('--api', '-a', type=click.Choice(['chispart']), 
              help='API a utilizar (sobrescribe la configuración global)')
@click.option('--no-guardar', is_flag=True, help='No guardar en historial')
@click.option('--stream', is_flag=True, help='Activar streaming de respuesta')
@click.pass_context
def chat(ctx, mensaje: str, modelo: Optional[str], api: Optional[str], 
         no_guardar: bool, stream: bool):
    """
    💬 Envía un mensaje de texto a la API seleccionada
    
    \b
    Ejemplos:
      chispart chat "Explícame la física cuántica"
      chispart chat "Escribe un poema" --modelo gpt-4
      chispart chat "¿Cómo está el clima?" --api openai --stream
    """
    manager = ctx.obj['manager']
    api_name = api or ctx.obj['api']
    
    try:
        result = manager.command_handler.handle_chat(
            api_name=api_name,
            message=mensaje,
            model=modelo,
            save_history=not no_guardar,
            stream=stream
        )
        
        if not result["success"]:
            sys.exit(1)
            
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)

@cli.command()
@click.argument('archivo', type=click.Path(exists=True))
@click.option('--prompt', '-p', default="¿Qué hay en esta imagen?", 
              help='Pregunta sobre la imagen')
@click.option('--modelo', '-m', help='Modelo específico a utilizar')
@click.option('--api', '-a', type=click.Choice(['chispart']), 
              help='API a utilizar')
@click.option('--no-guardar', is_flag=True, help='No guardar en historial')
@click.pass_context
def imagen(ctx, archivo: str, prompt: str, modelo: Optional[str], 
           api: Optional[str], no_guardar: bool):
    """
    🖼️ Analiza una imagen con IA
    
    \b
    Formatos soportados: JPG, JPEG, PNG, WebP
    Tamaño máximo: 20MB
    
    \b
    Ejemplos:
      chispart imagen foto.jpg
      chispart imagen screenshot.png "Extrae el texto de esta imagen"
      chispart imagen ~/storage/shared/Pictures/imagen.jpg --api openai
    """
    manager = ctx.obj['manager']
    api_name = api or ctx.obj['api']
    
    try:
        result = manager.command_handler.handle_image_analysis(
            api_name=api_name,
            file_path=archivo,
            prompt=prompt,
            model=modelo,
            save_history=not no_guardar
        )
        
        if not result["success"]:
            sys.exit(1)
            
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)

@cli.command()
@click.argument('archivo', type=click.Path(exists=True))
@click.option('--prompt', '-p', default="Resume el contenido de este documento", 
              help='Pregunta sobre el PDF')
@click.option('--modelo', '-m', help='Modelo específico a utilizar')
@click.option('--api', '-a', type=click.Choice(['chispart']), 
              help='API a utilizar')
@click.option('--no-guardar', is_flag=True, help='No guardar en historial')
@click.pass_context
def pdf(ctx, archivo: str, prompt: str, modelo: Optional[str], 
        api: Optional[str], no_guardar: bool):
    """
    📄 Analiza un documento PDF con IA
    
    \b
    Características:
    • Extracción automática de texto
    • Soporte para documentos grandes (hasta 20MB)
    • Truncado inteligente para documentos muy largos
    
    \b
    Ejemplos:
      chispart pdf documento.pdf
      chispart pdf paper.pdf "¿Cuáles son las conclusiones principales?"
      chispart pdf ~/storage/shared/Download/informe.pdf --modelo claude-3-sonnet
    """
    manager = ctx.obj['manager']
    api_name = api or ctx.obj['api']
    
    try:
        result = manager.command_handler.handle_pdf_analysis(
            api_name=api_name,
            file_path=archivo,
            prompt=prompt,
            model=modelo,
            save_history=not no_guardar
        )
        
        if not result["success"]:
            sys.exit(1)
            
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)

@cli.command()
@click.option('--modelo', '-m', help='Modelo específico a utilizar')
@click.option('--api', '-a', type=click.Choice(['chispart']), 
              help='API a utilizar')
@click.pass_context
def interactivo(ctx, modelo: Optional[str], api: Optional[str]):
    """
    🗣️ Inicia una sesión de chat interactiva
    
    \b
    Características:
    • Conversación continua con contexto
    • Comandos especiales integrados
    • Estadísticas de sesión en tiempo real
    • Historial persistente
    
    \b
    Comandos especiales en sesión:
      'salir', 'exit', 'quit' - Terminar sesión
      'limpiar', 'clear' - Limpiar contexto
      'stats' - Ver estadísticas de sesión
    
    \b
    Ejemplos:
      chispart interactivo
      chispart interactivo --modelo gpt-4 --api openai
    """
    manager = ctx.obj['manager']
    api_name = api or ctx.obj['api']
    
    try:
        manager.command_handler.handle_interactive_session(
            api_name=api_name,
            model=modelo
        )
    except KeyboardInterrupt:
        console.print("\n[yellow]Sesión interrumpida. ¡Hasta luego![/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)

@cli.command()
@click.option('--limite', '-l', default=10, help='Número de conversaciones a mostrar')
@click.pass_context
def historial(ctx, limite: int):
    """
    📚 Muestra el historial de conversaciones
    
    \b
    Información mostrada:
    • Fecha y hora de cada conversación
    • Tipo de interacción (chat, imagen, PDF)
    • API y modelo utilizados
    • Tokens consumidos
    • Contenido resumido
    
    \b
    Ejemplos:
      chispart historial
      chispart historial --limite 20
    """
    manager = ctx.obj['manager']
    manager.show_history(limite)

@cli.command()
@click.option('--api', '-a', type=click.Choice(['chispart']), 
              help='Mostrar modelos de una API específica')
@click.pass_context
def modelos(ctx, api: Optional[str]):
    """
    🤖 Lista los modelos disponibles
    
    \b
    Información mostrada:
    • Nombre del modelo
    • ID interno del modelo
    • Modelo por defecto marcado
    • Descripción de capacidades
    
    \b
    Ejemplos:
      chispart modelos
      chispart modelos --api openai
      chispart modelos --api anthropic
    """
    manager = ctx.obj['manager']
    api_name = api or ctx.obj['api']
    manager.show_models(api_name)

@cli.command()
@click.pass_context
def estado(ctx):
    """
    📊 Muestra el estado detallado del sistema
    
    \b
    Información mostrada:
    • Estado de configuración de todas las APIs
    • Estadísticas de uso (comandos, tokens, etc.)
    • Información del entorno (Termux, tema, etc.)
    • Recomendaciones de optimización
    
    \b
    Útil para:
    • Diagnosticar problemas de configuración
    • Verificar el estado de las APIs
    • Monitorear el uso de tokens
    """
    manager = ctx.obj['manager']
    manager.show_status()

@cli.command()
@click.pass_context
def configurar(ctx):
    """
    ⚙️ Ejecuta el asistente de configuración interactivo
    
    \b
    El asistente te guiará para:
    • Configurar claves API de diferentes proveedores
    • Seleccionar tema de la interfaz
    • Optimizar configuración para tu entorno
    • Verificar que todo funcione correctamente
    
    \b
    Recomendado para:
    • Primera instalación
    • Agregar nuevas APIs
    • Cambiar configuración existente
    """
    manager = ctx.obj['manager']
    
    try:
        success = manager.run_setup_wizard()
        if success:
            console.print("[green]✅ Configuración completada exitosamente[/green]")
        else:
            console.print("[yellow]⚠️ Configuración cancelada[/yellow]")
    except Exception as e:
        console.print(f"[red]Error durante la configuración: {str(e)}[/red]")
        sys.exit(1)

@cli.command()
@click.pass_context
def tema(ctx):
    """
    🎨 Configura el tema de la interfaz
    
    \b
    Temas disponibles:
    • neon - Colores vibrantes estilo cyberpunk
    • dark - Tema oscuro elegante
    • light - Tema claro y limpio
    • retro - Estilo vintage terminal
    
    \b
    El tema se guarda automáticamente y se aplica
    a todas las futuras sesiones de Chispart.
    """
    manager = ctx.obj['manager']
    
    try:
        success = manager.configure_theme()
        if success:
            console.print("[green]✅ Tema configurado exitosamente[/green]")
        else:
            console.print("[yellow]⚠️ Configuración de tema cancelada[/yellow]")
    except Exception as e:
        console.print(f"[red]Error configurando tema: {str(e)}[/red]")
        sys.exit(1)

@cli.command()
@click.option('--api', '-a', type=click.Choice(['chispart']), 
              required=True, help='API a establecer como actual')
@click.pass_context
def usar(ctx, api: str):
    """
    🔄 Cambia la API por defecto
    
    \b
    Establece una API como la predeterminada para
    todos los comandos subsecuentes, a menos que
    se especifique otra con --api.
    
    \b
    Ejemplos:
      chispart usar --api openai
      chispart usar --api anthropic
      chispart usar --api groq
    """
    manager = ctx.obj['manager']
    
    if manager.set_current_api(api):
        console.print(f"[green]✅ API por defecto cambiada a {api}[/green]")
    else:
        sys.exit(1)

@cli.command()
@click.pass_context
def version(ctx):
    """
    ℹ️ Muestra información detallada de la versión
    """
    from ui.components import create_panel
    
    version_info = """
[bold]Chispart CLI v2.0.0[/bold]

[dim]Interfaz Universal para LLMs[/dim]
[dim]Arquitectura Modular Modernizada[/dim]

[blue]API Soportada:[/blue]
• BlackboxAI/Chispart (GPT-4, Claude, Llama, Gemini, Mixtral, DeepSeek, Qwen)

[green]Características:[/green]
• Interfaz moderna con temas
• Optimizado para Termux/Android
• Análisis de imágenes y PDFs
• Modo interactivo avanzado
• Validación robusta
• Manejo de errores inteligente

[yellow]Desarrollado por:[/yellow]
Sebastian Vernis Mora
"""
    
    console.print(create_panel(
        version_info,
        title="Información de Versión",
        style="chispart.brand"
    ))

# Aliases para comandos comunes (shortcuts)
@cli.command(hidden=True)
@click.argument('mensaje')
@click.pass_context
def c(ctx, mensaje: str):
    """Alias para 'chat' - Envío rápido de mensajes"""
    ctx.invoke(chat, mensaje=mensaje)

@cli.command(hidden=True)
@click.pass_context
def i(ctx):
    """Alias para 'interactivo' - Sesión rápida"""
    ctx.invoke(interactivo)

@cli.command(hidden=True)
@click.pass_context
def h(ctx):
    """Alias para 'historial' - Ver historial rápido"""
    ctx.invoke(historial)

@cli.command(hidden=True)
@click.pass_context
def s(ctx):
    """Alias para 'estado' - Estado rápido"""
    ctx.invoke(estado)

def main():
    """Función principal de entrada"""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️ Operación cancelada por el usuario[/yellow]")
        sys.exit(130)
    except Exception as e:
        if '--debug' in sys.argv:
            raise
        console.print(f"[red]❌ Error inesperado: {str(e)}[/red]")
        console.print("[dim]Usa --debug para ver más detalles[/dim]")
        sys.exit(1)
    finally:
        # Cleanup si es necesario
        if cli_manager:
            cli_manager.cleanup()

if __name__ == "__main__":
    main()

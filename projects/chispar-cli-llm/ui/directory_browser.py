"""
Interfaz interactiva para navegación y exploración de directorios
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from rich.prompt import Prompt, Confirm, IntPrompt
from rich.tree import Tree
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text

from .components import console, create_panel, create_table
from .theme_manager import get_theme
from .interactive import InteractivePrompt, MenuSelector
from core.directory_analyzer import directory_analyzer


class DirectoryBrowser:
    """Navegador interactivo de directorios con capacidades de análisis"""
    
    def __init__(self):
        self.colors = get_theme()
        self.current_path = Path.cwd()
        self.history = [self.current_path]
        self.bookmarks = []
        self.analysis_cache = {}
    
    def start_interactive_session(self) -> None:
        """Inicia una sesión interactiva de navegación de directorios"""
        console.print(create_panel(
            f"""
[{self.colors['primary']}]🗂️ Navegador Interactivo de Directorios[/]

[{self.colors['dim']}]Comandos disponibles:[/]
[{self.colors['info']}]• ls, dir - Listar contenido actual[/]
[{self.colors['info']}]• cd <directorio> - Cambiar directorio[/]
[{self.colors['info']}]• analizar - Analizar directorio actual[/]
[{self.colors['info']}]• tree - Mostrar árbol de directorios[/]
[{self.colors['info']}]• info - Información del directorio[/]
[{self.colors['info']}]• bookmark - Guardar marcador[/]
[{self.colors['info']}]• bookmarks - Ver marcadores[/]
[{self.colors['info']}]• back - Volver atrás[/]
[{self.colors['info']}]• home - Ir al directorio home[/]
[{self.colors['info']}]• help - Mostrar ayuda[/]
[{self.colors['info']}]• exit, quit - Salir[/]
""",
            title="🚀 Navegador de Directorios",
            style="chispart.brand"
        ))
        
        self._show_current_location()
        
        while True:
            try:
                # Mostrar prompt con directorio actual
                current_dir = self.current_path.name or str(self.current_path)
                command = InteractivePrompt.ask(
                    f"[{self.colors['accent']}]{current_dir}[/] $"
                ).strip()
                
                if not command:
                    continue
                
                # Procesar comando
                if command.lower() in ['exit', 'quit', 'salir']:
                    console.print(f"[{self.colors['success']}]👋 ¡Hasta luego![/]")
                    break
                
                self._process_command(command)
                
            except KeyboardInterrupt:
                console.print(f"\n[{self.colors['warning']}]Navegación interrumpida. ¡Hasta luego![/]")
                break
            except Exception as e:
                console.print(f"[{self.colors['error']}]❌ Error: {str(e)}[/]")
    
    def _process_command(self, command: str) -> None:
        """Procesa un comando del usuario"""
        parts = command.split()
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        if cmd in ['ls', 'dir', 'list']:
            self._list_directory()
        elif cmd == 'cd':
            if args:
                self._change_directory(' '.join(args))
            else:
                self._change_directory(str(Path.home()))
        elif cmd == 'analizar':
            self._analyze_current_directory()
        elif cmd == 'tree':
            depth = int(args[0]) if args and args[0].isdigit() else 3
            self._show_directory_tree(depth)
        elif cmd == 'info':
            self._show_directory_info()
        elif cmd == 'bookmark':
            name = ' '.join(args) if args else None
            self._add_bookmark(name)
        elif cmd == 'bookmarks':
            self._show_bookmarks()
        elif cmd == 'back':
            self._go_back()
        elif cmd == 'home':
            self._change_directory(str(Path.home()))
        elif cmd == 'help':
            self._show_help()
        elif cmd == 'pwd':
            console.print(f"[{self.colors['info']}]{self.current_path}[/]")
        elif cmd == 'clear':
            console.clear()
        elif cmd.startswith('/') or cmd.startswith('~') or Path(cmd).exists():
            # Ruta directa
            self._change_directory(cmd)
        else:
            console.print(f"[{self.colors['error']}]❌ Comando no reconocido: {cmd}[/]")
            console.print(f"[{self.colors['dim']}]Usa 'help' para ver comandos disponibles[/]")
    
    def _list_directory(self, show_hidden: bool = False) -> None:
        """Lista el contenido del directorio actual"""
        try:
            items = list(self.current_path.iterdir())
            
            if not show_hidden:
                items = [item for item in items if not item.name.startswith('.')]
            
            # Separar directorios y archivos
            directories = [item for item in items if item.is_dir()]
            files = [item for item in items if item.is_file()]
            
            # Ordenar
            directories.sort(key=lambda x: x.name.lower())
            files.sort(key=lambda x: x.name.lower())
            
            # Crear tabla
            table = create_table(title=f"📁 Contenido de {self.current_path.name}")
            table.add_column("Tipo", width=6)
            table.add_column("Nombre", style=self.colors["primary"])
            table.add_column("Tamaño", width=12, style=self.colors["dim"])
            table.add_column("Modificado", width=20, style=self.colors["dim"])
            
            # Añadir directorios
            for directory in directories:
                try:
                    stat = directory.stat()
                    modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
                    table.add_row(
                        "📁 DIR",
                        f"[{self.colors['accent']}]{directory.name}/[/]",
                        "-",
                        modified
                    )
                except (OSError, PermissionError):
                    table.add_row(
                        "📁 DIR",
                        f"[{self.colors['accent']}]{directory.name}/[/]",
                        "?",
                        "?"
                    )
            
            # Añadir archivos
            for file in files:
                try:
                    stat = file.stat()
                    size = self._format_size(stat.st_size)
                    modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
                    
                    # Determinar icono por extensión
                    icon = self._get_file_icon(file.suffix)
                    
                    table.add_row(
                        f"{icon} FILE",
                        file.name,
                        size,
                        modified
                    )
                except (OSError, PermissionError):
                    table.add_row(
                        "📄 FILE",
                        file.name,
                        "?",
                        "?"
                    )
            
            console.print(table)
            
            # Mostrar resumen
            console.print(f"\n[{self.colors['dim']}]📊 Total: {len(directories)} directorios, {len(files)} archivos[/]")
            
        except PermissionError:
            console.print(f"[{self.colors['error']}]❌ Sin permisos para listar {self.current_path}[/]")
        except Exception as e:
            console.print(f"[{self.colors['error']}]❌ Error listando directorio: {str(e)}[/]")
    
    def _change_directory(self, path: str) -> None:
        """Cambia al directorio especificado"""
        try:
            # Expandir ~ y resolver ruta
            new_path = Path(path).expanduser().resolve()
            
            if not new_path.exists():
                console.print(f"[{self.colors['error']}]❌ El directorio {path} no existe[/]")
                return
            
            if not new_path.is_dir():
                console.print(f"[{self.colors['error']}]❌ {path} no es un directorio[/]")
                return
            
            # Verificar permisos
            if not os.access(new_path, os.R_OK):
                console.print(f"[{self.colors['error']}]❌ Sin permisos de lectura para {path}[/]")
                return
            
            # Cambiar directorio
            self.history.append(self.current_path)
            self.current_path = new_path
            
            self._show_current_location()
            
        except Exception as e:
            console.print(f"[{self.colors['error']}]❌ Error cambiando directorio: {str(e)}[/]")
    
    def _analyze_current_directory(self) -> None:
        """Analiza el directorio actual"""
        console.print(f"[{self.colors['info']}]🔍 Analizando {self.current_path.name}...[/]")
        
        try:
            # Verificar cache
            cache_key = str(self.current_path)
            if cache_key in self.analysis_cache:
                analysis = self.analysis_cache[cache_key]
                console.print(f"[{self.colors['dim']}]📋 Usando análisis en cache[/]")
            else:
                # Realizar análisis
                analysis = directory_analyzer.analyze_directory(
                    str(self.current_path),
                    max_depth=3,
                    analyze_content=True
                )
                self.analysis_cache[cache_key] = analysis
            
            # Mostrar resultados
            directory_analyzer.display_analysis_summary(analysis)
            
        except Exception as e:
            console.print(f"[{self.colors['error']}]❌ Error en análisis: {str(e)}[/]")
    
    def _show_directory_tree(self, max_depth: int = 3) -> None:
        """Muestra el árbol de directorios"""
        console.print(f"[{self.colors['info']}]🌳 Árbol de {self.current_path.name} (profundidad: {max_depth})[/]")
        
        try:
            tree = Tree(
                f"[{self.colors['primary']}]📁 {self.current_path.name}[/]",
                style=self.colors["primary"]
            )
            
            self._build_tree_recursive(tree, self.current_path, max_depth, 0)
            console.print(tree)
            
        except Exception as e:
            console.print(f"[{self.colors['error']}]❌ Error generando árbol: {str(e)}[/]")
    
    def _build_tree_recursive(self, tree_node, directory: Path, max_depth: int, current_depth: int) -> None:
        """Construye el árbol de directorios recursivamente"""
        if current_depth >= max_depth:
            return
        
        try:
            items = sorted(directory.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
            
            for item in items:
                if item.name.startswith('.'):
                    continue
                
                if item.is_dir():
                    # Añadir directorio
                    dir_node = tree_node.add(
                        f"[{self.colors['accent']}]📁 {item.name}/[/]",
                        style=self.colors["accent"]
                    )
                    
                    # Recursión para subdirectorios
                    if current_depth < max_depth - 1:
                        try:
                            self._build_tree_recursive(dir_node, item, max_depth, current_depth + 1)
                        except PermissionError:
                            dir_node.add(f"[{self.colors['error']}]❌ Sin permisos[/]")
                
                elif item.is_file():
                    # Añadir archivo
                    icon = self._get_file_icon(item.suffix)
                    size = self._format_size(item.stat().st_size)
                    tree_node.add(
                        f"[{self.colors['dim']}]{icon} {item.name} ({size})[/]",
                        style=self.colors["dim"]
                    )
        
        except PermissionError:
            tree_node.add(f"[{self.colors['error']}]❌ Sin permisos para listar[/]")
    
    def _show_directory_info(self) -> None:
        """Muestra información detallada del directorio actual"""
        try:
            stat = self.current_path.stat()
            
            # Contar elementos
            total_items = 0
            total_files = 0
            total_dirs = 0
            total_size = 0
            
            for item in self.current_path.rglob('*'):
                total_items += 1
                if item.is_file():
                    total_files += 1
                    try:
                        total_size += item.stat().st_size
                    except (OSError, PermissionError):
                        pass
                elif item.is_dir():
                    total_dirs += 1
            
            # Información básica
            info = f"""
[{self.colors['primary']}]📁 Directorio:[/] {self.current_path.name}
[{self.colors['info']}]📍 Ruta completa:[/] {self.current_path}
[{self.colors['info']}]👤 Propietario:[/] {stat.st_uid}
[{self.colors['info']}]🔒 Permisos:[/] {oct(stat.st_mode)[-3:]}
[{self.colors['info']}]📅 Modificado:[/] {datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}

[{self.colors['success']}]📊 Estadísticas:[/]
[{self.colors['dim']}]• Total de elementos: {total_items}[/]
[{self.colors['dim']}]• Archivos: {total_files}[/]
[{self.colors['dim']}]• Directorios: {total_dirs}[/]
[{self.colors['dim']}]• Tamaño total: {self._format_size(total_size)}[/]
"""
            
            console.print(create_panel(
                info.strip(),
                title="ℹ️ Información del Directorio",
                style=self.colors["info"]
            ))
            
        except Exception as e:
            console.print(f"[{self.colors['error']}]❌ Error obteniendo información: {str(e)}[/]")
    
    def _add_bookmark(self, name: Optional[str] = None) -> None:
        """Añade un marcador del directorio actual"""
        if not name:
            name = InteractivePrompt.ask("Nombre del marcador", default=self.current_path.name)
        
        bookmark = {
            'name': name,
            'path': str(self.current_path),
            'created': datetime.now().isoformat()
        }
        
        # Verificar si ya existe
        existing = next((b for b in self.bookmarks if b['path'] == str(self.current_path)), None)
        if existing:
            if Confirm.ask(f"Ya existe un marcador para esta ruta. ¿Actualizar?"):
                existing['name'] = name
                existing['created'] = datetime.now().isoformat()
                console.print(f"[{self.colors['success']}]✅ Marcador actualizado: {name}[/]")
            return
        
        self.bookmarks.append(bookmark)
        console.print(f"[{self.colors['success']}]✅ Marcador añadido: {name}[/]")
    
    def _show_bookmarks(self) -> None:
        """Muestra los marcadores guardados"""
        if not self.bookmarks:
            console.print(f"[{self.colors['warning']}]📭 No hay marcadores guardados[/]")
            return
        
        table = create_table(title="🔖 Marcadores")
        table.add_column("#", width=3)
        table.add_column("Nombre", style=self.colors["primary"])
        table.add_column("Ruta", style=self.colors["dim"])
        table.add_column("Creado", width=20, style=self.colors["dim"])
        
        for i, bookmark in enumerate(self.bookmarks, 1):
            created = datetime.fromisoformat(bookmark['created']).strftime('%Y-%m-%d %H:%M')
            table.add_row(
                str(i),
                bookmark['name'],
                bookmark['path'],
                created
            )
        
        console.print(table)
        
        # Opción de navegar a marcador
        if Confirm.ask("¿Navegar a un marcador?"):
            try:
                choice = IntPrompt.ask(
                    "Número de marcador",
                    choices=[str(i) for i in range(1, len(self.bookmarks) + 1)]
                )
                bookmark = self.bookmarks[choice - 1]
                self._change_directory(bookmark['path'])
            except (ValueError, IndexError):
                console.print(f"[{self.colors['error']}]❌ Selección inválida[/]")
    
    def _go_back(self) -> None:
        """Vuelve al directorio anterior"""
        if len(self.history) > 1:
            self.current_path = self.history.pop()
            self._show_current_location()
        else:
            console.print(f"[{self.colors['warning']}]⚠️ No hay directorio anterior[/]")
    
    def _show_current_location(self) -> None:
        """Muestra la ubicación actual"""
        console.print(f"\n[{self.colors['info']}]📍 Ubicación actual: [bold]{self.current_path}[/bold][/]")
    
    def _show_help(self) -> None:
        """Muestra la ayuda de comandos"""
        help_text = f"""
[{self.colors['primary']}]🆘 Comandos Disponibles:[/]

[{self.colors['accent']}]Navegación:[/]
[{self.colors['dim']}]• ls, dir - Listar contenido del directorio[/]
[{self.colors['dim']}]• cd <directorio> - Cambiar a directorio[/]
[{self.colors['dim']}]• back - Volver al directorio anterior[/]
[{self.colors['dim']}]• home - Ir al directorio home[/]
[{self.colors['dim']}]• pwd - Mostrar directorio actual[/]

[{self.colors['accent']}]Análisis:[/]
[{self.colors['dim']}]• analizar - Analizar directorio actual[/]
[{self.colors['dim']}]• tree [profundidad] - Mostrar árbol (def: 3)[/]
[{self.colors['dim']}]• info - Información detallada[/]

[{self.colors['accent']}]Marcadores:[/]
[{self.colors['dim']}]• bookmark [nombre] - Guardar marcador[/]
[{self.colors['dim']}]• bookmarks - Ver y navegar marcadores[/]

[{self.colors['accent']}]Utilidades:[/]
[{self.colors['dim']}]• clear - Limpiar pantalla[/]
[{self.colors['dim']}]• help - Mostrar esta ayuda[/]
[{self.colors['dim']}]• exit, quit - Salir del navegador[/]

[{self.colors['warning']}]💡 Tip:[/] También puedes escribir rutas directas como /home/user o ~/Documents
"""
        
        console.print(create_panel(
            help_text.strip(),
            title="📚 Ayuda del Navegador",
            style="chispart.brand"
        ))
    
    def _get_file_icon(self, extension: str) -> str:
        """Obtiene el icono apropiado para un tipo de archivo"""
        icons = {
            '.py': '🐍',
            '.js': '📜',
            '.ts': '📘',
            '.html': '🌐',
            '.css': '🎨',
            '.json': '📋',
            '.md': '📝',
            '.txt': '📄',
            '.pdf': '📕',
            '.jpg': '🖼️',
            '.jpeg': '🖼️',
            '.png': '🖼️',
            '.gif': '🖼️',
            '.mp4': '🎬',
            '.mp3': '🎵',
            '.zip': '📦',
            '.tar': '📦',
            '.gz': '📦',
            '.exe': '⚙️',
            '.sh': '⚡',
            '.bat': '⚡',
        }
        
        return icons.get(extension.lower(), '📄')
    
    def _format_size(self, size_bytes: int) -> str:
        """Formatea el tamaño en bytes a una representación legible"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f}TB"


# Instancia global del navegador
directory_browser = DirectoryBrowser()

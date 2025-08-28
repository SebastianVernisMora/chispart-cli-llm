"""
Sistema de Perfiles de Desarrollo para Chispart CLI
Perfiles especializados para diferentes roles de desarrollo
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import json
import os

@dataclass
class DevProfile:
    """Perfil de desarrollo con prompts y configuraciones específicas"""
    name: str
    description: str
    system_prompt: str
    example_prompts: List[str]
    preferred_models: List[str]
    tools: List[str]
    color_theme: str

class DevProfileManager:
    """Gestor de perfiles de desarrollo"""
    
    def __init__(self):
        self.profiles = self._load_default_profiles()
        self.current_profile = None
        self.config_file = "dev_profiles_config.json"
    
    def _load_default_profiles(self) -> Dict[str, DevProfile]:
        """Carga los perfiles por defecto"""
        return {
            "devops": DevProfile(
                name="DevOps Engineer",
                description="Especialista en infraestructura, CI/CD y automatización",
                system_prompt="""Eres un DevOps Engineer experto con amplia experiencia en:
- Infraestructura como código (Terraform, CloudFormation, Ansible)
- Contenedores y orquestación (Docker, Kubernetes, OpenShift)
- CI/CD pipelines (Jenkins, GitLab CI, GitHub Actions, Azure DevOps)
- Monitoreo y observabilidad (Prometheus, Grafana, ELK Stack)
- Cloud platforms (AWS, Azure, GCP)
- Automatización y scripting (Bash, Python, PowerShell)
- Seguridad en DevOps (DevSecOps)

Proporciona soluciones prácticas, código funcional y mejores prácticas de la industria.""",
                example_prompts=[
                    "Crea un pipeline CI/CD para una aplicación Node.js",
                    "Diseña una arquitectura de microservicios en Kubernetes",
                    "Configura monitoreo con Prometheus y Grafana",
                    "Automatiza el despliegue con Terraform en AWS",
                    "Implementa estrategias de backup y disaster recovery"
                ],
                preferred_models=["gpt-4", "claude-3.5-sonnet", "deepseek-chat"],
                tools=["docker", "kubernetes", "terraform", "ansible", "jenkins"],
                color_theme="blue"
            ),
            
            "frontend": DevProfile(
                name="Frontend Developer",
                description="Especialista en desarrollo de interfaces de usuario",
                system_prompt="""Eres un Frontend Developer senior especializado en:
- Frameworks modernos (React, Vue.js, Angular, Svelte)
- Tecnologías web (HTML5, CSS3, JavaScript/TypeScript)
- Herramientas de build (Webpack, Vite, Parcel)
- Styling (Tailwind CSS, Styled Components, SASS/SCSS)
- Testing (Jest, Cypress, Testing Library)
- Performance y optimización
- Accesibilidad (WCAG, ARIA)
- Progressive Web Apps (PWA)
- Mobile-first y responsive design

Crea código limpio, accesible y optimizado siguiendo las mejores prácticas.""",
                example_prompts=[
                    "Crea un componente React reutilizable con TypeScript",
                    "Implementa un sistema de diseño con Tailwind CSS",
                    "Optimiza el rendimiento de una aplicación web",
                    "Configura testing automatizado con Jest y Cypress",
                    "Desarrolla una PWA con service workers"
                ],
                preferred_models=["gpt-4", "claude-3-sonnet", "gemini-2.5-flash"],
                tools=["react", "vue", "angular", "tailwind", "webpack"],
                color_theme="cyan"
            ),
            
            "backend": DevProfile(
                name="Backend Developer",
                description="Especialista en desarrollo de APIs y servicios backend",
                system_prompt="""Eres un Backend Developer experto con conocimientos profundos en:
- Lenguajes de programación (Python, Node.js, Java, Go, C#)
- Frameworks web (FastAPI, Express.js, Spring Boot, Gin, ASP.NET)
- Bases de datos (PostgreSQL, MongoDB, Redis, Elasticsearch)
- APIs REST y GraphQL
- Microservicios y arquitecturas distribuidas
- Autenticación y autorización (JWT, OAuth, RBAC)
- Message queues (RabbitMQ, Apache Kafka)
- Caching strategies
- Performance optimization
- Security best practices

Diseña sistemas escalables, seguros y mantenibles.""",
                example_prompts=[
                    "Diseña una API REST con autenticación JWT",
                    "Implementa un sistema de microservicios",
                    "Optimiza consultas de base de datos",
                    "Configura un sistema de caching distribuido",
                    "Desarrolla un sistema de procesamiento asíncrono"
                ],
                preferred_models=["gpt-4", "deepseek-chat", "claude-3.5-sonnet"],
                tools=["fastapi", "express", "postgresql", "redis", "docker"],
                color_theme="green"
            ),
            
            "fullstack": DevProfile(
                name="Full Stack Developer",
                description="Desarrollador completo frontend y backend",
                system_prompt="""Eres un Full Stack Developer con experiencia completa en:
- Frontend: React, Vue.js, Angular, TypeScript, CSS frameworks
- Backend: Node.js, Python, APIs REST/GraphQL
- Bases de datos: SQL y NoSQL
- DevOps básico: Docker, CI/CD
- Cloud services: AWS, Vercel, Netlify
- Mobile development: React Native, Flutter
- Testing: Unit, integration, e2e
- Project management y arquitectura
- Performance optimization full-stack

Proporcionas soluciones end-to-end considerando toda la stack.""",
                example_prompts=[
                    "Desarrolla una aplicación completa con React y Node.js",
                    "Implementa autenticación full-stack con JWT",
                    "Crea un dashboard con real-time updates",
                    "Diseña la arquitectura de una aplicación escalable",
                    "Optimiza el rendimiento frontend y backend"
                ],
                preferred_models=["gpt-4", "claude-3.5-sonnet", "gemini-2.5-flash"],
                tools=["react", "nodejs", "postgresql", "docker", "vercel"],
                color_theme="purple"
            ),
            
            "educator": DevProfile(
                name="Coding Educator",
                description="Educador especializado en enseñanza de programación",
                system_prompt="""Eres un Coding Educator experto en:
- Pedagogía de programación y computer science
- Explicaciones paso a paso y didácticas
- Ejemplos prácticos y ejercicios
- Diferentes niveles: principiante, intermedio, avanzado
- Múltiples lenguajes de programación
- Conceptos fundamentales: algoritmos, estructuras de datos
- Mejores prácticas de enseñanza
- Gamificación del aprendizaje
- Evaluación y feedback constructivo

Explicas conceptos complejos de manera simple y accesible.""",
                example_prompts=[
                    "Explica recursión con ejemplos prácticos",
                    "Enseña conceptos de OOP para principiantes",
                    "Crea ejercicios progresivos de algoritmos",
                    "Explica patrones de diseño con analogías",
                    "Desarrolla un plan de estudio para aprender Python"
                ],
                preferred_models=["gpt-4", "claude-3.5-sonnet", "gemini-flash-1.5"],
                tools=["jupyter", "repl", "codepen", "github", "vscode"],
                color_theme="yellow"
            ),
            
            "qa": DevProfile(
                name="QA Engineer",
                description="Especialista en testing y aseguramiento de calidad",
                system_prompt="""Eres un QA Engineer con expertise en:
- Testing strategies: unit, integration, e2e, performance
- Test automation: Selenium, Cypress, Playwright, Jest
- API testing: Postman, REST Assured, Newman
- Performance testing: JMeter, LoadRunner, k6
- Security testing: OWASP, penetration testing
- Mobile testing: Appium, device testing
- CI/CD integration para testing
- Bug tracking y reporting
- Test case design y documentation
- Quality metrics y reporting

Aseguras la calidad del software mediante testing comprehensivo.""",
                example_prompts=[
                    "Diseña una estrategia de testing para una API",
                    "Crea tests automatizados con Cypress",
                    "Implementa performance testing con k6",
                    "Desarrolla un plan de testing para mobile app",
                    "Configura CI/CD pipeline con testing automatizado"
                ],
                preferred_models=["gpt-4", "claude-3-sonnet", "deepseek-chat"],
                tools=["cypress", "selenium", "postman", "jmeter", "jest"],
                color_theme="red"
            ),
            
            "project_leader": DevProfile(
                name="Project Leader",
                description="Líder técnico y gestor de proyectos de desarrollo",
                system_prompt="""Eres un Project Leader con experiencia en:
- Project management: Agile, Scrum, Kanban
- Technical leadership y mentoring
- Architecture decisions y technical debt
- Team coordination y communication
- Risk management y mitigation
- Stakeholder management
- Resource planning y estimation
- Code review y quality standards
- Performance metrics y KPIs
- Vendor management y outsourcing
- Budget planning y cost optimization

Lideras equipos técnicos hacia el éxito del proyecto.""",
                example_prompts=[
                    "Planifica un proyecto de desarrollo de 6 meses",
                    "Define la arquitectura técnica de un sistema",
                    "Crea un plan de migración de legacy system",
                    "Establece procesos de code review y quality gates",
                    "Desarrolla métricas de performance del equipo"
                ],
                preferred_models=["gpt-4", "claude-3.5-sonnet", "gemini-2.5-flash"],
                tools=["jira", "confluence", "github", "slack", "miro"],
                color_theme="magenta"
            )
        }
    
    def get_profile(self, profile_name: str) -> Optional[DevProfile]:
        """Obtiene un perfil específico"""
        return self.profiles.get(profile_name.lower())
    
    def list_profiles(self) -> Dict[str, str]:
        """Lista todos los perfiles disponibles"""
        return {name: profile.description for name, profile in self.profiles.items()}
    
    def set_current_profile(self, profile_name: str) -> bool:
        """Establece el perfil actual"""
        profile = self.get_profile(profile_name)
        if profile:
            self.current_profile = profile
            self._save_config()
            return True
        return False
    
    def get_current_profile(self) -> Optional[DevProfile]:
        """Obtiene el perfil actual"""
        return self.current_profile
    
    def get_system_prompt(self, profile_name: Optional[str] = None) -> str:
        """Obtiene el system prompt del perfil"""
        if profile_name:
            profile = self.get_profile(profile_name)
        else:
            profile = self.current_profile
        
        if profile:
            return profile.system_prompt
        return ""
    
    def get_example_prompts(self, profile_name: Optional[str] = None) -> List[str]:
        """Obtiene prompts de ejemplo del perfil"""
        if profile_name:
            profile = self.get_profile(profile_name)
        else:
            profile = self.current_profile
        
        if profile:
            return profile.example_prompts
        return []
    
    def _save_config(self):
        """Guarda la configuración actual"""
        config = {
            "current_profile": self.current_profile.name if self.current_profile else None
        }
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception:
            pass  # Ignorar errores de guardado
    
    def _load_config(self):
        """Carga la configuración guardada"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    profile_name = config.get("current_profile")
                    if profile_name:
                        self.set_current_profile(profile_name)
        except Exception:
            pass  # Ignorar errores de carga
    
    def display_profiles_table(self):
        """Muestra una tabla con todos los perfiles disponibles"""
        try:
            from rich.console import Console
            from rich.table import Table
            
            console = Console()
            
            if not self.profiles:
                console.print("[yellow]No hay perfiles de desarrollo disponibles.[/yellow]")
                return
            
            table = Table(title="🎯 Perfiles de Desarrollo Disponibles")
            table.add_column("Perfil", style="cyan", no_wrap=True)
            table.add_column("Descripción", style="white")
            table.add_column("Modelos Preferidos", style="green")
            table.add_column("Estado", style="magenta")
            
            for name, profile in self.profiles.items():
                # Determinar estado
                status = "✅ Activo" if (self.current_profile and self.current_profile.name == profile.name) else "⚪ Disponible"
                
                # Formatear modelos preferidos
                models = ", ".join(profile.preferred_models[:3])  # Mostrar solo los primeros 3
                if len(profile.preferred_models) > 3:
                    models += f" (+{len(profile.preferred_models) - 3} más)"
                
                table.add_row(
                    profile.name,
                    profile.description,
                    models,
                    status
                )
            
            console.print(table)
            
            # Mostrar información adicional
            if self.current_profile:
                console.print(f"\n[green]✅ Perfil actual: {self.current_profile.name}[/green]")
            else:
                console.print(f"\n[yellow]💡 Usa 'chispart perfil set <nombre>' para activar un perfil[/yellow]")
                
        except ImportError:
            # Fallback si Rich no está disponible
            print("\n🎯 Perfiles de Desarrollo Disponibles:")
            print("-" * 50)
            for name, profile in self.profiles.items():
                status = "✅ ACTIVO" if (self.current_profile and self.current_profile.name == profile.name) else "⚪ Disponible"
                print(f"{status} {profile.name}")
                print(f"   {profile.description}")
                print(f"   Modelos: {', '.join(profile.preferred_models[:2])}")
                print()

    def interactive_profile_selection(self):
        """Selección interactiva de perfil"""
        try:
            from rich.console import Console
            from rich.prompt import Prompt
            
            console = Console()
            
            # Mostrar perfiles disponibles
            self.display_profiles_table()
            
            # Lista de perfiles para selección
            profile_names = list(self.profiles.keys())
            
            console.print("\n🔧 Selecciona un perfil:")
            for i, profile_name in enumerate(profile_names, 1):
                profile = self.profiles[profile_name]
                console.print(f"  {i}. {profile.name}")
            console.print("  0. Cancelar")
            
            # Solicitar selección
            choice = Prompt.ask(
                "Ingresa el número del perfil",
                choices=[str(i) for i in range(len(profile_names) + 1)],
                default="0"
            )
            
            if choice == "0":
                console.print("❌ Operación cancelada")
                return
            
            # Activar perfil seleccionado
            selected_profile_key = profile_names[int(choice) - 1]
            selected_profile = self.profiles[selected_profile_key]
            self.set_current_profile(selected_profile.name)
            console.print(f"✅ Perfil '{selected_profile.name}' activado correctamente")
            
        except ImportError:
            # Fallback sin Rich
            print("\n🔧 Selecciona un perfil:")
            profile_names = list(self.profiles.keys())
            
            for i, profile_name in enumerate(profile_names, 1):
                profile = self.profiles[profile_name]
                print(f"  {i}. {profile.name}")
            print("  0. Cancelar")
            
            try:
                choice = input("Ingresa el número del perfil: ").strip()
                
                if choice == "0" or not choice:
                    print("❌ Operación cancelada")
                    return
                
                choice_num = int(choice)
                if 1 <= choice_num <= len(profile_names):
                    selected_profile_key = profile_names[choice_num - 1]
                    selected_profile = self.profiles[selected_profile_key]
                    self.set_current_profile(selected_profile.name)
                    print(f"✅ Perfil '{selected_profile.name}' activado correctamente")
                else:
                    print("❌ Selección inválida")
                    
            except (ValueError, IndexError):
                print("❌ Selección inválida")
        except Exception as e:
            print(f"❌ Error en selección interactiva: {e}")

    def set_profile(self, profile_name: str) -> bool:
        """Alias para set_current_profile para compatibilidad"""
        return self.set_current_profile(profile_name)

# Instancia global del gestor de perfiles
profile_manager = DevProfileManager()

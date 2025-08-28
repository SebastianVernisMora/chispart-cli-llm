import os
from pathlib import Path
import pypdf
from typing import List, Dict, Tuple

# Directorios a ignorar
IGNORE_DIRS = {
    '__pycache__', '.git', '.svn', '.hg', 'node_modules',
    '.venv', 'venv', 'env', '.env', 'build', 'dist',
    '.pytest_cache', '.coverage', 'htmlcov', '.tox',
    '.idea', '.vscode', '.vs', 'target', 'bin', 'obj'
}

# Archivos de documentación priorizados, en orden de importancia
DOC_FILES_PRIORITY = [
    "readme.md", "readme.rst", "readme.txt", "readme",
    "contributing.md", "contributing.rst",
    "license", "license.md", "license.txt",
    "changelog.md", "changelog.rst",
    "changes.md", "changes.rst",
]

# Directorios de documentación
DOC_DIRS = ["docs", "documentation"]

class DirectoryAnalyzer:
    def __init__(self, directory_path: str):
        self.directory_path = Path(directory_path).resolve()
        if not self.directory_path.is_dir():
            raise ValueError(f"Path '{self.directory_path}' is not a valid directory.")

    def analyze(self) -> Dict[str, str]:
        """
        Analiza el directorio, priorizando documentación y muestreando contenido.
        """
        all_files = self._get_all_files()

        prioritized_docs, other_files = self._prioritize_files(all_files)

        documentation_content = self._analyze_documentation(prioritized_docs)
        sampled_content = self._sample_content_bundle(other_files)

        result = {}
        if documentation_content:
            result["documentation_summary"] = documentation_content
        if sampled_content:
            result["content_samples"] = sampled_content

        return result

    def _get_all_files(self) -> List[Path]:
        """
        Obtiene todos los archivos del directorio, respetando IGNORE_DIRS.
        """
        all_files = []
        for root, dirs, files in os.walk(self.directory_path, topdown=True):
            dirs[:] = [d for d in dirs if d.lower() not in IGNORE_DIRS]

            for file in files:
                all_files.append(Path(root) / file)
        return all_files

    def _prioritize_files(self, files: List[Path]) -> Tuple[List[Path], List[Path]]:
        """
        Separa los archivos en documentación prioritaria y el resto.
        """
        docs = []
        others = []
        for file in files:
            priority = self._get_item_priority(file)
            if priority is not None:
                docs.append((file, priority))
            else:
                others.append(file)

        # Ordenar documentos por prioridad (número más bajo es mejor)
        docs.sort(key=lambda item: item[1])

        return [file for file, prio in docs], others

    def _get_item_priority(self, file_path: Path) -> int or None:
        """
        Devuelve la prioridad de un archivo. None si no es prioritario.
        Un número más bajo indica mayor prioridad.
        """
        file_name_lower = file_path.name.lower()

        # Prioridad por nombre de archivo
        if file_name_lower in DOC_FILES_PRIORITY:
            return DOC_FILES_PRIORITY.index(file_name_lower)

        # Prioridad por directorio de documentación
        for part in file_path.parts:
            if part.lower() in DOC_DIRS:
                return len(DOC_FILES_PRIORITY) + 1 # Menor prioridad que los archivos raíz

        return None

    def _read_file_content(self, file_path: Path) -> str:
        """Lee el contenido de un archivo, manejando PDFs."""
        if file_path.suffix.lower() == '.pdf':
            try:
                reader = pypdf.PdfReader(file_path)
                return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
            except Exception:
                # pypdf puede fallar en PDFs corruptos o protegidos
                return f"[Error al leer el PDF: {file_path.name}]"
        else:
            try:
                return file_path.read_text(encoding='utf-8', errors='ignore')
            except Exception:
                return f"[Error al leer el archivo: {file_path.name}]"

    def _analyze_documentation(self, doc_files: List[Path]) -> str:
        """
        Lee y concatena el contenido de los archivos de documentación.
        """
        content = []
        for file in doc_files:
            text = self._read_file_content(file)
            relative_path = file.relative_to(self.directory_path)
            content.append(f"--- Contenido de {relative_path} ---\n{text}\n")

        return "\n".join(content)

    def _sample_content_bundle(self, files: List[Path], max_total_chars: int = 15000, max_file_chars: int = 2000) -> str:
        """
        Crea un "bundle" de contenido muestreado de varios archivos.
        """
        bundle = []
        total_chars = 0

        for file in files:
            if total_chars >= max_total_chars:
                break

            text = self._read_file_content(file)
            if not text.strip():
                continue

            snippet = self._create_snippet(text, max_file_chars)

            if snippet:
                relative_path = file.relative_to(self.directory_path)
                bundle.append(f"--- Snippet de {relative_path} ---\n{snippet}\n")
                total_chars += len(snippet)

        return "\n".join(bundle)

    def _create_snippet(self, text: str, max_chars: int) -> str:
        """
        Crea un snippet de un texto, tomando del inicio.
        """
        if len(text) <= max_chars:
            return text

        return text[:max_chars] + "\n\n[... CONTENIDO TRUNCADO ...]"

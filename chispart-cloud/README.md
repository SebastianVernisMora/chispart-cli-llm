# Chispart Cloud Tools

Herramientas de backend para análisis de código y shell interactivo, optimizadas para ser consumidas por clientes ligeros como Termux.

## Descripción

Este proyecto proporciona una API de Flask que expone dos funcionalidades principales:

1.  **Shell Interactivo**: Un entorno de shell seguro y con estado que permite ejecutar comandos básicos, gestionar el historial y cambiar de directorio.
2.  **Análisis Jerárquico de Directorios**: Una herramienta que analiza una estructura de directorios, prioriza la documentación (`README`, etc.) y extrae fragmentos de código de otros archivos para proporcionar un contexto rápido a un LLM.

## Instalación

1.  Clona este repositorio.
2.  Navega al directorio `chispart-cloud`.
3.  Instala las dependencias de Python:

    ```bash
    pip install -r requirements.txt
    ```

## Ejecución

Para iniciar el servidor de desarrollo de Flask, ejecuta:

```bash
python3 app.py
```

El servidor estará disponible en `http://0.0.0.0:8080`.

## Uso de la API

Puedes interactuar con la API enviando peticiones `POST` al endpoint `/api/interactive`.

**Ejemplo con `curl`:**

```bash
curl -X POST -H "Content-Type: application/json" -d '{"input": "!ls -l"}' http://localhost:8080/api/interactive
```

### Comandos del Shell

-   `! <comando>`: Ejecuta un comando de la lista blanca (ej. `!ls`, `!pwd`).
-   `!!`: Repite el último comando.
-   `!run <n>`: Ejecuta el n-ésimo comando del historial.
-   `!? /regex/i`: Busca y ejecuta un comando del historial por regex.
-   `history [-n <num>] [/regex/]`: Muestra el historial.
-   `cd <directorio>`: Cambia el directorio de trabajo actual.
-   `set <var> <val>`: Establece variables de sesión (`timeout`, `outmax`, `histmax`).

### Comando de Análisis

-   `@analizar <directorio>`: Analiza el directorio especificado.

    ```bash
    curl -X POST -H "Content-Type: application/json" -d '{"input": "@analizar ."}' http://localhost:8080/api/interactive
    ```

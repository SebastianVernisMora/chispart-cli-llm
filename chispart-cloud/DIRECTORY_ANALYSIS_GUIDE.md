# Guía de Análisis de Directorios en Chispart Cloud Tools

Esta guía explica cómo funciona el analizador de directorios y qué puedes esperar de él.

## Propósito

El objetivo del comando `@analizar` es proporcionar rápidamente un contexto rico y relevante sobre un codebase a un Large Language Model (LLM). En lugar de simplemente listar archivos, el analizador realiza un análisis inteligente para extraer la información más útil.

## Proceso de Análisis

Cuando ejecutas `@analizar <directorio>`, el analizador sigue estos pasos:

1.  **Recolección de Archivos**: Se escanea el directorio de forma recursiva para encontrar todos los archivos. Se ignoran automáticamente directorios comunes que no suelen ser relevantes para el análisis de código (ej. `.git`, `node_modules`, `venv`, `dist`).

2.  **Priorización de Documentación**: Los archivos se dividen en dos grupos:
    *   **Documentación Prioritaria**: Archivos que típicamente describen el proyecto. Esto incluye `README.md`, `CONTRIBUTING.md`, `LICENSE`, `CHANGELOG.md`, y cualquier archivo dentro de un directorio `docs/`.
    *   **Otros Archivos**: El resto de los archivos del proyecto (código fuente, configuraciones, etc.).

3.  **Extracción de Contenido de Documentación**: El contenido completo de los archivos de documentación prioritaria se lee y se concatena. Esto asegura que la información más importante sobre el proyecto se incluya en su totalidad.

4.  **Muestreo de Contenido (Snippets)**: Para el resto de los archivos, se extraen "snippets" o fragmentos de su contenido. Esto se hace para dar una idea del código sin exceder los límites de tokens del LLM.
    *   Se lee el inicio de cada archivo.
    *   Hay un límite de caracteres por archivo (por defecto 2000) y un límite total para todo el muestreo (por defecto 15000) para mantener la salida manejable.

## Salida

El resultado del análisis se presenta en dos secciones:

-   `--- Documentación Detectada ---`: Contiene el texto completo de los archivos de documentación, uno tras otro.
-   `--- Fragmentos de Archivos ---`: Contiene los snippets del resto de los archivos.

Este formato está diseñado para ser fácilmente parseado por un LLM, permitiéndole distinguir entre la documentación general del proyecto y ejemplos específicos de código.

## Compatibilidad con Termux

El analizador está diseñado para ser compatible con Termux:

-   No utiliza `PyMuPDF`, que puede fallar al compilar en Android. En su lugar, usa `pypdf`, una biblioteca de Python puro para la extracción de texto de archivos PDF.
-   No depende de `cryptography` ni de otras bibliotecas con dependencias de compilación complejas.

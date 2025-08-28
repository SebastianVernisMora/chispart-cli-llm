# Plan de Cierre y Próximos Pasos

Este documento resume los hallazgos clave de la auditoría y propone un plan de acción para cerrar las brechas identificadas.

---

## 🚀 Quick Wins (Próximas 48 horas)

Acciones de alto impacto y bajo esfuerzo que se pueden completar de inmediato para mejorar el estado del proyecto.

1.  **Estructurar `chispart-cloud-agents`:**
    - **Acción:** Crear la estructura de directorios para `chispart-cloud-agents` y añadir los archivos de configuración (`docker-compose.yml`, `Makefile`, `.env.example`, `scripts/dev.sh`) basados en el documento `prompt_de_arranque_chispart_cli_cloud_agents_blackbox_vnc_desde_termux.md`.
    - **Impacto:** Alinea el repositorio con la documentación, desbloqueando el desarrollo y la validación de la infraestructura.

2.  **Validar Pruebas Unitarias de `chispart-cli`:**
    - **Acción:** Ejecutar las pruebas existentes en `chispar-cli-llm/tests/` para establecer una línea base de la funcionalidad actual. Específicamente, ejecutar `pytest chispar-cli-llm/tests/test_security.py` para validar el cifrado (SEC-E2E-002).
    - **Impacto:** Confirma que las características de seguridad core de la CLI funcionan como se espera.

3.  **Archivar Código Obsoleto:**
    - **Acción:** Renombrar el directorio `chispart-cloud` a `archive/chispart-cloud-legacy` para evitar confusiones con la nueva implementación de `chispart-cloud-agents`.
    - **Impacto:** Reduce la confusión y asegura que los desarrolladores trabajen sobre la arquitectura correcta.

---

## 🛑 Bloqueadores

Problemas críticos que impiden el progreso en áreas clave del proyecto.

1.  **Implementación Inexistente de `chispart-cloud-agents`:**
    - **Descripción:** El principal bloqueador es que el componente `chispart-cloud-agents` no está implementado. Toda la validación para el orquestador, el runtime MCP y los workers se basa en especificaciones y no en código funcional.
    - **Desbloqueo:** Se debe iniciar el desarrollo de `chispart-cloud-agents` comenzando por los componentes P0 definidos en `VALIDATION_MATRIX.json` (ORCH-API-001, RT-MCP-001, INF-DOCKER-001).

---

## ⚠️ Riesgos y Mitigaciones

Factores que podrían poner en peligro el éxito del proyecto y cómo abordarlos.

1.  **Riesgo: Brecha entre Especificación y Realidad.**
    - **Descripción:** La diferencia entre la ambiciosa especificación de `chispart-cloud-agents` y la falta de código es significativa, lo que podría llevar a retrasos en el proyecto.
    - **Mitigación:**
        - **Enfoque por Fases:** Implementar y validar los componentes en orden de prioridad (P0 → P1 → P2) utilizando la `VALIDATION_MATRIX.json` como una hoja de ruta.
        - **MVP Estricto:** Enfocarse primero en el flujo end-to-end más simple: un workflow que ejecuta un comando `shell.exec` en un worker y devuelve el resultado.

2.  **Riesgo: Vulnerabilidades de Seguridad.**
    - **Descripción:** Las dependencias (`requirements.txt`, `package.json`) pueden tener vulnerabilidades conocidas. El control de egress y la allowlist de comandos en la CLI pueden no ser robustos.
    - **Mitigación:**
        - **Análisis de Dependencias:** Utilizar herramientas como `pip-audit` o `npm audit` para escanear y actualizar paquetes vulnerables.
        - **Pruebas de Seguridad:** Realizar pruebas de penetración básicas en la CLI para intentar evadir la allowlist y el control de egress.

3.  **Riesgo: Falta de Integración Continua (CI).**
    - **Descripción:** Sin un pipeline de CI, la calidad del código y la detección de regresiones dependen de procesos manuales, que son propensos a errores.
    - **Mitigación:**
        - **Implementar CI Básica:** Configurar un pipeline simple (ej. GitHub Actions) que ejecute linters y las pruebas unitarias de `chispart-cli` en cada pull request.

---

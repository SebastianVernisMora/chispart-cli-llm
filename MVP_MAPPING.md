# Mapeo de Criterios de Aceptación del MVP

Este documento mapea los ítems de validación de la auditoría directamente a los criterios de aceptación implícitos del Minimum Viable Product (MVP). El objetivo del MVP es demostrar un flujo funcional y seguro desde la CLI local hasta la ejecución de una tarea en un agente en la nube.

---

## Criterio de Aceptación del MVP 1: La CLI puede iniciar y operar de forma segura.

Un usuario debe poder utilizar la `chispart-cli` para ejecutar comandos locales y comunicarse de forma segura, sentando las bases para la interacción con la nube.

| ID de Validación | Título                                        | Justificación del Mapeo                                                                 |
| ---------------- | --------------------------------------------- | --------------------------------------------------------------------------------------- |
| `CLI-PTY-002`    | PTY real con streaming, timeouts y exit codes | **Core:** La capacidad de ejecutar comandos locales de forma fiable es la base de la CLI.   |
| `SEC-LOG-001`    | Redacción de secretos en logs                 | **Seguridad:** Garantiza que la operación básica no exponga credenciales sensibles.       |
| `SEC-E2E-002`    | Cifrado AES-GCM con Argon2id validado         | **Seguridad:** El cifrado de extremo a extremo es fundamental para toda comunicación futura. |

---

## Criterio de Aceptación del MVP 2: La infraestructura de Cloud Agents es desplegable y está lista para el desarrollo.

El equipo de desarrollo debe poder levantar un entorno local completo de `chispart-cloud-agents` que sirva como base para implementar la lógica de los agentes.

| ID de Validación | Título                                              | Justificación del Mapeo                                                                |
| ---------------- | --------------------------------------------------- | -------------------------------------------------------------------------------------- |
| `INF-DOCKER-001` | `docker-compose` levanta servicios base (DB, Redis) | **Core:** Sin una infraestructura funcional, no se puede desarrollar ni probar ningún agente. |
| `INF-ENV-002`    | Scripts y `.env` cargan variables correctamente     | **DevX:** Un sistema de configuración funcional es crucial para el desarrollo eficiente.     |

---

## Criterio de Aceptación del MVP 3: Un flujo de trabajo end-to-end puede ser ejecutado desde la CLI hasta un agente en la nube.

Este es el criterio principal del MVP: demostrar que la CLI puede solicitar la ejecución de una tarea, que el orquestador puede procesarla y que un agente puede ejecutarla.

| ID de Validación | Título                                                  | Justificación del Mapeo                                                                                              |
| ---------------- | ------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `CLI-WS-001`     | WS RPC operativo con pairing y autenticación            | **Comunicación:** El WebSocket RPC es el canal de comunicación entre la CLI y el orquestador.                        |
| `ORCH-API-001`   | API/WS del orchestrator (`/workflows`, `/runs`)         | **Core Cloud:** El orquestador es el cerebro del sistema en la nube; su API es el punto de entrada para todas las tareas. |
| `RT-MCP-001`     | Runtime MCP estable con adapters (`shell.exec`, etc.)   | **Core Cloud:** El runtime es el encargado de ejecutar las tareas; el MCP es el protocolo que lo hace posible.         |
| `WRK-MIN-001`    | Workers mínimos operativos (`shell`, `git`, `llm`)      | **Ejecución:** Demuestra que las tareas pueden ser delegadas y ejecutadas en entornos aislados.                        |

---

## Conclusión del Mapeo

Para cumplir con los requisitos del MVP, el esfuerzo de desarrollo debe centrarse en implementar y estabilizar los **9 ítems de validación** listados anteriormente. Estos ítems representan la ruta crítica hacia un producto funcional y demostrable. Los ítems de prioridad P1 y P2 pueden ser abordados en iteraciones posteriores.

# Checklist de Validación Integral: Chispart CLI y Cloud Agents

Este checklist audita el estado de `chispart-cli` y `chispart-cloud-agents`, priorizando las tareas de validación de P0 (crítico) a P2 (deseable).

---

## P0: Funcionalidad Crítica y Seguridad Core

| ID        | Componente              | Título                                                  | Estado      |
| --------- | ----------------------- | ------------------------------------------------------- | ----------- |
| `CLI-WS-001` | `chispart-cli`          | WS RPC operativo con pairing y autenticación            | `to_do`     |
| `CLI-PTY-002` | `chispart-cli`          | PTY real con streaming, timeouts y exit codes           | `to_do`     |
| `SEC-LOG-001` | `cli` & `orchestrator`  | Redacción de secretos en logs (CLI y orchestrator)      | `to_do`     |
| `SEC-E2E-002` | `chispart-cli`          | Cifrado AES-GCM con Argon2id validado                   | `to_do`     |
| `ORCH-API-001`| `chispart-cloud-agents` | API/WS del orchestrator (`/workflows`, `/runs`)         | `to_do`     |
| `RT-MCP-001`  | `chispart-cloud-agents` | Runtime MCP estable con adapters (`shell.exec`, etc.)   | `to_do`     |
| `INF-DOCKER-001`| Infraestructura       | `docker-compose` levanta servicios base (DB, Redis)     | `to_do`     |

---

## P1: Integraciones y Flujos de Trabajo Clave

| ID        | Componente              | Título                                                  | Estado      |
| --------- | ----------------------- | ------------------------------------------------------- | ----------- |
| `CLI-AWL-003` | `chispart-cli`          | Allowlist de comandos activa y logs de auditoría        | `to_do`     |
| `CLI-LLM-004` | `chispart-cli`          | Router LLM con Blackbox (BYOK) y fallback               | `to_do`     |
| `CLI-GIT-005` | `chispart-cli`          | Integración funcional con PR de GitHub                  | `to_do`     |
| `WRK-MIN-001` | `chispart-cloud-agents` | Workers mínimos operativos (`shell`, `git`, `llm`)      | `to_do`     |
| `RT-DSL-002`  | `chispart-cloud-agents` | DSL YAML con DAG, `if/retries/backoff`                  | `to_do`     |
| `UI-CONSOLE-001`| `chispart-cloud-agents` | Console UI muestra runs, logs en vivo y artefactos      | `to_do`     |
| `SEC-EGR-003` | `chispart-cli`          | Egress limitado según allowlist                         | `to_do`     |

---

## P2: Mejoras de DevX y Entornos Específicos

| ID        | Componente              | Título                                                  | Estado      |
| --------- | ----------------------- | ------------------------------------------------------- | ----------- |
| `INF-ENV-002` | Infraestructura       | Scripts y `.env` cargan variables correctamente         | `to_do`     |
| `SEC-CONT-004`| `chispart-cloud-agents` | Seguridad en contenedores (no-root, cgroups, seccomp)   | `to_do`     |
| `VNC-SSH-001` | VNC / Termux          | Túnel SSH y acceso VNC solo en `localhost`              | `to_do`     |

---

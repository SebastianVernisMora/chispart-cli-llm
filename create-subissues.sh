#!/usr/bin/env bash
set -euo pipefail

# Requisitos:
#  - GitHub CLI: https://cli.github.com/
#  - Autenticado: gh auth login
# Uso:
#  REPO="owner/repo" ./create-subissues.sh
# Opcional:
#  LABELS="project:chispart,area:multi-agent" ASSIGNEES="tu-usuario" REPO="owner/repo" ./create-subissues.sh
#  DRY_RUN=1  # solo imprime comandos sin crear issues

REPO="${REPO:?Define REPO, ej: owner/repo}"
LABELS="${LABELS:-roadmap,auto,validacion}"
ASSIGNEES="${ASSIGNEES:-}"   # ej: "sebastianvernis"
DRY_RUN="${DRY_RUN:-0}"

# Helper para crear con idempotencia básica (si existe título exacto, no duplica)
create_issue () {
  local ref="$1" section="$2" title="$3" purpose="$4" acceptance="$5"

  local full_title="(Ref #${ref}) ${title}"
  local body
  body="$(cat <<'MD'
### Propósito
{{PURPOSE}}

### Criterios de Aceptación (resumen)
{{ACCEPTANCE}}

### Entregables / Evidencia
- Logs y artefactos en MinIO/S3 cuando aplique
- Registro de comando(s) de verificación
- Checklist de tareas en el propio issue

> **Notas**: Añadir subtareas, responsables y tiempos. Respetar deny-by-default, redacción de secretos y límites de egress.
MD
)"
  body="${body//'{{PURPOSE}}'/$purpose}"
  body="${body//'{{ACCEPTANCE}}'/$acceptance}"

  # Etiquetas base + sección + ref
  local labels_csv="${LABELS},section:${section},ref:${ref}"

  if [[ "$DRY_RUN" == "1" ]]; then
    echo "gh issue create -R \"$REPO\" --title \"$full_title\" --body <<MD ... MD --label \"$labels_csv\" ${ASSIGNEES:+--assignee \"$ASSIGNEES\"}"
  else
    # Evitar duplicados si ya existe un issue con mismo título
    if gh issue list -R "$REPO" --search "in:title \"$full_title\"" --json number,title | jq -e 'length>0' >/dev/null 2>&1; then
      echo "🔁 Ya existe: $full_title (omitido)"
      return 0
    fi
    gh issue create -R "$REPO" \
      --title "$full_title" \
      --body "$body" \
      --label "$labels_csv" \
      ${ASSIGNEES:+--assignee "$ASSIGNEES"}
  fi
}

# --------------------------
# Definición de sub-issues
# --------------------------

# SECCIÓN A: Core CLI (Python)
create_issue 24 "A-core-cli" \
  "CLI WS RPC Foundation" \
  "Servidor WS RPC con pairing y auth JWT (E2EE opcional)." \
  "- Handshake estable; ping/pong <100ms; logs sin secretos."

create_issue 25 "A-core-cli" \
  "CLI PTY Execution & Streaming" \
  "Ejecución con PTY real (stdout/stderr streaming, timeout, exit code)." \
  "- 'chispart exec -- \"git status\"' emite stream; timeout efectivo; exit code correcto."

create_issue 26 "A-core-cli" \
  "CLI Allowlist & Security Layer" \
  "Política deny-by-default con allowlist por plan y auditoría." \
  "- Comandos fuera de allowlist bloqueados; logs redactados; tests gratis/básico/pro."

create_issue 27 "A-core-cli" \
  "CLI LLM Router (Blackbox/BYOK)" \
  "Router a Blackbox por defecto y BYOK; fallback documentado." \
  "- Respuesta con id/model/usage; ninguna API key en logs."

# SECCIÓN B: Core Cloud Agents
create_issue 28 "B-cloud-agents" \
  "Orchestrator API & WebSocket Core" \
  "Endpoints '/workflows', '/runs' y WS para estados/logs." \
  "- Estados queued→running→(succeeded|failed); WS estable; /health OK."

create_issue 29 "B-cloud-agents" \
  "MCP Runtime Integration" \
  "Runtime con adapters shell.exec, git.*, file.*, llm.chat (contrato MCP)." \
  "- Llamada MCP devuelve stream + exitCode; aislamiento de FS válido."

create_issue 30 "B-cloud-agents" \
  "Workers Básicos (Shell, Git, LLM, QA, Tests, Repo)" \
  "Workers mínimos con colas y reintentos/backoff." \
  "- Cada worker procesa job y publica artefactos; métricas por cola."

create_issue 31 "B-cloud-agents" \
  "YAML DSL & DAG Execution Engine" \
  "Parser YAML + ejecución DAG con 'if', retries y timeouts." \
  "- Workflow demo (plan→build→QA→tests→PR) corre end-to-end."

# SECCIÓN C: Infraestructura & Sandbox
create_issue 32 "C-infra-sandbox" \
  "Docker Compose & Local Environment" \
  "Levantar Postgres, Redis, MinIO, Orchestrator, Console, Workers." \
  "- 'make dev' deja API :4000 y Console :3000; seed/migraciones OK."

create_issue 33 "C-infra-sandbox" \
  "Seguridad Avanzada (Cgroups, Seccomp, Redacción de Logs)" \
  "Límites de CPU/RAM/IO, perfiles seccomp/AppArmor, redacción." \
  "- Límites efectivos bajo estrés; ningún secreto en logs."

create_issue 34 "C-infra-sandbox" \
  "Integración MinIO/S3 para Artefactos" \
  "Subida/descarga de artefactos; políticas de acceso y URLs firmadas." \
  "- Artefactos accesibles desde Console; checksums guardados."

create_issue 35 "C-infra-sandbox" \
  "Cifrado AES-GCM + Argon2id" \
  "Encriptar secretos en repositorio/DB (derive con Argon2id)." \
  "- Tests de cifrado/descifrado; rotación de clave documentada."

# SECCIÓN D: Console & Interfaces
create_issue 36 "D-console-ui" \
  "Next.js Console (Runs & Logs en Vivo)" \
  "Vista de runs; detalle con logs/artefactos en tiempo real." \
  "- Stream <150ms; enlaces de artefacto funcionales."

create_issue 37 "D-console-ui" \
  "WebSocket Streaming para Logs y Artefactos" \
  "Multiplexación por canal; reconexión automática; compresión." \
  "- Reconecta sin pérdida; métricas de ws; compresión activa."

create_issue 38 "D-console-ui" \
  "Configuración UI de Workflows" \
  "Editor YAML/JSON con validación y templates (drag & drop opcional)." \
  "- 10+ templates; validación en tiempo real; preview antes de guardar."

create_issue 39 "D-console-ui" \
  "Panel de Monitoreo de Workers" \
  "Métricas por cola/worker (latencia, throughput, fallos)." \
  "- Dashboard con refresh 15s; alertas básicas."

# SECCIÓN E: Integración & Testing
create_issue 40 "E-integration-testing" \
  "End-to-End Workflow Demo" \
  "Caso completo (plan→build→QA→tests→PR) con artefactos." \
  "- Completa en <30m; PR creado con URL guardada."

create_issue 41 "E-integration-testing" \
  "Pruebas E2E de CLI con Cloud Agents" \
  "CLI invoca orquestador y consume logs/artefactos vía WS/HTTP." \
  "- Scripts reproducibles; exit codes correctos; reporte E2E."

create_issue 42 "E-integration-testing" \
  "Testing de Seguridad (inyección, acceso, egress)" \
  "Pruebas de inyección/autorización; egress allow-list y WS seguro." \
  "- 0 críticas; bloqueo de egress no listado; reporte con mitigaciones."

create_issue 43 "E-integration-testing" \
  "Testing de Performance y Escalabilidad" \
  "Cargas con 100+ agentes; perfiles CPU/RAM/IO." \
  "- Latencia media <150ms; CPU <80% y RAM <2GB; reporte versionado."

# SECCIÓN F: Seguridad Operacional
create_issue 44 "F-operational-security" \
  "Redacción Avanzada de Secretos en Logs" \
  "Máscaras para tokens/keys/URLs sensibles en CLI y cloud." \
  "- Regex/estrategia validada; tests de no-fuga."

create_issue 45 "F-operational-security" \
  "Auditoría de Límites y Cuotas por Plan" \
  "Límites por plan (tiempo, costo, comandos) con métricas." \
  "- Bloqueos y mensajes claros; panel de métricas por plan."

create_issue 46 "F-operational-security" \
  "Alertas de Uso y Health Checks" \
  "Alertas (Webhooks/Email) + endpoints /health y /ready." \
  "- Alertas por umbral; endpoints verdes."

create_issue 47 "F-operational-security" \
  "Backups y Rotación de Claves" \
  "Backups cifrados + rotación de claves/secretos sin downtime." \
  "- Restore probado; rotación documentada."

# SECCIÓN G: Integración Remota
create_issue 48 "G-remote" \
  "Validación de VNC via SSH Túnel (Termux)" \
  "Acceso VNC solo por localhost a través de túnel SSH." \
  "- Conexión localhost:5901; 'ss -tulpn' sin puerto expuesto."

create_issue 49 "G-remote" \
  "Configuración Headless & GUI Ligera" \
  "TigerVNC/x11vnc + XFCE/LXDE minimal en servidor." \
  "- Sesión estable; consumo bajo; scripts de arranque."

create_issue 50 "G-remote" \
  "Validación de Capa de Seguridad Localhost" \
  "Garantizar '-localhost yes' y firewall correcto." \
  "- No accesible desde red externa; pruebas nmap/curl."

create_issue 51 "G-remote" \
  "Documentación de Uso Remoto" \
  "Guía paso a paso de Termux + túnel + visor VNC." \
  "- Manual reproducible con troubleshooting."

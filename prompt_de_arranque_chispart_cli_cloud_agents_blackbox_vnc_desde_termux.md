## 🎯 Rol y objetivo
**Actúa como un Staff Engineer** para crear una base sólida de:
1) **Chispart CLI v1.0** con **WebSocket RPC** y **PTY real** para ejecutar comandos (`exec`, `git.*`, `github.pr.*`, `llm.chat`).
2) **Cloud Agents** (proyecto aparte) con **orquestador**, **runtime de agentes** con terminal propia en contenedor, comunicación **MCP** entre agentes (builder → QA → tests → repo/PR), resiliencia (retries/backoff) y **ruteo LLM** vía **Blackbox API** (soporta BYOK).
3) **Revisión remota vía VNC** usando túnel SSH desde **Termux**.

---

## 🔒 Principios
- **Seguridad primero**: deny‑by‑default, allow‑list de comandos y dominios, redacción de secretos en logs, cifrado AES‑GCM (Argon2id para derivación).
- **Coherencia**: misma semántica de `exec/git/llm` en CLI local y en agentes cloud.
- **Mantenibilidad**: capas finas, tipado fuerte, test E2E mínimos y docs claras.

---

## 🧱 Estructuras mínimas de repos

### A) `chispart-cli/` (Node/TypeScript o Python + Click)
```
chispart-cli/
  src/
    ws/
      server.ts           # WS RPC server (auth, pairing, E2EE opcional)
      handlers/           # exec, git, llm, github
    cli/
      index.ts            # comandos: ws start, exec, git pr create...
    providers/
      router.ts           # Blackbox(BYOK)/otros (OpenAI, Anthropic, Mistral)
    security/
      allowlist.ts        # comandos permitidos por plan
      redact.ts           # redacción de secretos en logs
  test/
  .env.example
  API-RPC.md
  COMMANDS.md
  SECURITY.md
```

**Comandos esperados**
- `chispart ws start --port 8765 --token <JWT>`
- `chispart exec --cwd <ruta> -- "git status"`
- `chispart git pr create --title "..." --body "..." --base main --head feat/x`
- `chispart providers test --provider blackbox`

**RPC mínimo (JSON sobre WS)**
```json
{ "op":"pair.init", "device":"android|ios|web", "nonce":"..." }
{ "op":"pair.confirm", "code":"123456" }
{ "op":"exec", "pty":true, "cwd":"/repo", "cmd":"git status" }
{ "op":"git.status", "repo":"/repo" }
{ "op":"github.pr.create", "repo":"/repo", "base":"main", "head":"feat/x", "title":"...", "body":"..." }
{ "op":"llm.chat", "provider":"blackbox|openai|mistral|...", "model":"...", "messages":[...] }
```

**Env vars**
```
BLACKBOX_API_KEY=...
CHISPART_ALLOWLIST=./config/allowlist.json
CHISPART_LOG_LEVEL=info
GITHUB_TOKEN=...
```

### B) `chispart-cloud-agents/` (monorepo)
```
chispart-cloud-agents/
  apps/
    orchestrator/         # NestJS: REST/WS, scheduler, policy engine, eventos
    console/              # Next.js: UI de runs/logs/artefactos
  packages/
    agents-runtime/       # runtime de agente: WS, PTY, FS sandbox, tool API MCP
    mcp-bridge/           # cliente/servidor MCP, catálogo de tools
    workers/              # code-builder, qa-reviewer, test-runner, repo-manager
    shared/               # tipos, auth, cifrado, utils
  infra/
    docker/               # Dockerfiles, profiles de seccomp/AppArmor
  workflows/
    examples/             # YAML de ejemplo (ver abajo)
  .env.example
  API.md
  SECURITY.md
```

**DSL YAML (ejemplo)**
```yaml
name: feature-branch-ci
on: [manual, github:pull_request.opened]
policy:
  allow_commands: ["git status","npm ci","npm run build","npm test"]
  egress_allow: ["github.com","registry.npmjs.org"]
  max_cost_usd: 2.50
  max_time_ms: 1800000
steps:
  - id: plan
    uses: llm.chat
    with: { provider: blackbox, model: o3-mini, prompt: "Resume issue y plan" }
  - id: build
    uses: shell.exec
    with: { cmd: "npm ci && npm run build", cwd: /work/app, pty: true, timeout: 900000 }
  - id: qa
    uses: qa.review
    with: { ruleset: strict }
  - id: tests
    uses: tests.run
    with: { framework: jest, cwd: /work/app }
  - id: pr
    if: "${{ steps.tests.ok && steps.qa.ok }}"
    uses: repo.pr.create
    with:
      title: "feat: ${context.branch}"
      body:  "${{ steps.plan.output }}\n\nChecks: ✅ QA ✅ Tests"
```

**Contrato MCP mínimo**
```json
{"id":"call-1","tool":"shell.exec","input":{"cmd":"npm run build","cwd":"/work/app","pty":true,"timeout":900000}}
{"id":"call-1","ok":true,"stream":[{"type":"stdout","data":"..."}],"exitCode":0}
```

**Workers mínimos (MVP)**
- `shell.exec` (PTY) con límites, allow‑list.
- `git.clone/status/diff/commit/push`.
- `llm.chat` con ruteo Blackbox/BYOK.
- `qa.review` (linters/semgrep básico).
- `tests.run` (jest/pytest según proyecto).
- `repo.pr.create/comment`.

**Sandbox**
- contenedor sin root, cgroups (CPU/RAM/IO), seccomp/AppArmor, user‑ns, rootfs RO + volumen `/work` con cuota; egress por **allow‑list**.

**Secrets**
- cifrado AES‑GCM; Argon2id para derivar clave; logs con **fingerprint** (nunca plaintext).

---

## ✅ Tareas para Blackbox (pasos concretos)

1) **CLI**
- Implementa WS RPC (`server.ts`) con handlers: `pair.init/confirm`, `exec`, `git.status/diff`, `llm.chat`, `github.pr.create`.
- Soporta **PTY real** (node‑pty) en `exec` y streaming stdout/stderr.
- Añade `allowlist.json` por plan (gratis/básico/pro); aplica **deny‑by‑default**.
- Router LLM: **Blackbox** por defecto; **BYOK** opcional por usuario.
- Comandos CLI y docs (`API-RPC.md`, `COMMANDS.md`).

2) **Cloud Agents**
- Orchestrator REST/WS con `/workflows`, `/runs`, `WS /runs/{id}` y colas (Redis/BullMQ).
- `agents-runtime` con PTY y contrato MCP; tool adapters (`file.*`, `git.*`, `shell.exec`, `llm.chat`).
- Workers `qa-reviewer`, `test-runner`, `repo-manager` básicos.
- DSL YAML parser + ejecución DAG con retries/backoff y `if` condicional.
- Console: vista de runs, logs en tiempo real, artefactos.

3) **Seguridad**
- Redacción de secretos en logs; políticas de egress; timeouts; cuotas por plan.
- Cifrado de secretos (AES‑GCM) y almacenamiento de artefactos en S3/MinIO.

4) **Pruebas y ejemplos**
- Repos de ejemplo (Node/Python) con workflows `feature-branch-ci`.
- Tests de integración (E2E) para un PR ficticio.

**Criterios de aceptación (MVP)**
- `chispart ws start` + `chispart exec` con PTY y streaming.
- Workflow YAML ejecuta: plan → build → QA → tests → PR; reintentos si falla.
- Panel muestra runs/logs/artefactos; políticas y límites activos.

---

## 🧪 Variables y configuración
```
# CLI
BLACKBOX_API_KEY=...
GITHUB_TOKEN=...
CHISPART_ALLOWLIST=./config/allowlist.json

# Cloud Agents
POSTGRES_URL=postgres://...
REDIS_URL=redis://...
S3_ENDPOINT=http://...
S3_ACCESS_KEY=...
S3_SECRET_KEY=...
JWT_SECRET=...
```

---

## 🖥️ Revisión remota por **VNC** desde **Termux** (sin exponer VNC)

**En el servidor (donde corre la consola/VSCode GUI si aplica):**
1. Instala servidor VNC (TigerVNC/x11vnc) y un entorno ligero (XFCE opcional).
2. Crea contraseña VNC: `vncpasswd`.
3. Lanza VNC en :1 (solo localhost):
   - TigerVNC: `vncserver -localhost yes :1`
   - x11vnc: `x11vnc -localhost -display :0 -rfbport 5901`

**En Termux (Android): túnel SSH + visor VNC en localhost**
1. `pkg update && pkg install openssh -y`
2. Crea túnel: `ssh -N -L 5901:localhost:5901 user@tu-servidor`
3. Abre un visor VNC en Android y conéctate a **`localhost:5901`** (el túnel evita exponer el puerto público).

> Mantén VNC **solo** accesible por `localhost` y usa el túnel SSH. No expongas 5901 al exterior.

---

## 🧭 Guías de estilo y calidad
- TypeScript estricto, ESLint + Prettier.
- Commits convencionales (`feat:`, `fix:`, `chore:`) + CHANGELOG.
- Tests mínimos por handler/worker, smoke E2E por workflow demo.

---

## 📦 Entregables esperados
- `chispart-cli` funcional (WS RPC + PTY + git + LLM + PR) con docs.
- `chispart-cloud-agents` con orchestrator, runtime MCP, workers y console básica.
- Workflows YAML de ejemplo y scripts de arranque.

---

## ✍️ Instrucción para Blackbox
> *“Genera el código base y archivos de configuración para las dos carpetas (`chispart-cli/` y `chispart-cloud-agents/`) con las estructuras y contratos anteriores. Implementa primero la capa WS RPC y `exec` con PTY en la CLI. Luego el orchestrator y el `agents-runtime` con MCP y workers mínimos. Añade tests, ejemplos de workflows y documentación. Respeta seguridad (allow‑list/egress/secret‑redaction) y prepara scripts de ejecución local (docker‑compose si aplica).”*



---

# 19) Infra local (docker‑compose) + Scripts de arranque (mismo documento)

> Estos bloques te permiten pedirle a Blackbox que genere **tal cual** la infra y scripts para correr **chispart-cloud-agents** y validar la **CLI** en local. Copia/pega en los repos correspondientes.

## 19.1 `docker-compose.yml` (en `chispart-cloud-agents/`)
```yaml
version: "3.9"
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: chispart
      POSTGRES_PASSWORD: chispart
      POSTGRES_DB: agents
    ports: ["5432:5432"]
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]

  minio:
    image: minio/minio:RELEASE.2024-12-07T00-00-00Z
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    ports: ["9000:9000","9001:9001"]
    volumes:
      - minio:/data

  # job para crear bucket "artifacts" en minio
  minio-mc:
    image: minio/mc:RELEASE.2024-12-07T00-00-00Z
    depends_on: [minio]
    entrypoint: ["/bin/sh","-c"]
    command: >
      "mc alias set local http://minio:9000 minioadmin minioadmin &&
       mc mb -p local/artifacts || true &&
       mc anonymous set download local/artifacts || true &&
       sleep 1"

  orchestrator:
    build: ./apps/orchestrator
    depends_on: [postgres, redis, minio, minio-mc]
    environment:
      NODE_ENV: development
      POSTGRES_URL: postgres://chispart:chispart@postgres:5432/agents
      REDIS_URL: redis://redis:6379
      S3_ENDPOINT: http://minio:9000
      S3_ACCESS_KEY: minioadmin
      S3_SECRET_KEY: minioadmin
      S3_BUCKET: artifacts
      JWT_SECRET: devsecret
      PORT: 4000
    ports: ["4000:4000"]

  console:
    build: ./apps/console
    depends_on: [orchestrator]
    environment:
      NODE_ENV: development
      NEXT_PUBLIC_API_URL: http://localhost:4000
    ports: ["3000:3000"]

  workers:
    build: ./packages/workers
    depends_on: [orchestrator]
    environment:
      NODE_ENV: development
      POSTGRES_URL: postgres://chispart:chispart@postgres:5432/agents
      REDIS_URL: redis://redis:6379
      S3_ENDPOINT: http://minio:9000
      S3_ACCESS_KEY: minioadmin
      S3_SECRET_KEY: minioadmin
      S3_BUCKET: artifacts
      JWT_SECRET: devsecret
      WORKERS: "shell,git,llm,qa,tests,repo"
    deploy:
      replicas: 1

volumes:
  pgdata:
  minio:
```

## 19.2 `.env.example` (raíces de ambos repos)
```env
# chispart-cloud-agents
POSTGRES_URL=postgres://chispart:chispart@localhost:5432/agents
REDIS_URL=redis://localhost:6379
S3_ENDPOINT=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET=artifacts
JWT_SECRET=devsecret
NEXT_PUBLIC_API_URL=http://localhost:4000

# chispart-cli
BLACKBOX_API_KEY=sk-...
GITHUB_TOKEN=ghp_...
CHISPART_ALLOWLIST=./config/allowlist.json
CHISPART_LOG_LEVEL=info
```

## 19.3 `Makefile` (en `chispart-cloud-agents/`)
```make
.PHONY: up down logs ps seed dev fmt lint test build

up:
	docker compose up -d --build

down:
	docker compose down -v

logs:
	docker compose logs -f --tail=200 orchestrator workers console

ps:
	docker compose ps

dev: up logs

seed:
	# ejecutar migraciones si tu ORM lo requiere (ej: prisma/knex/typeorm)
	docker compose exec orchestrator npm run db:migrate || true

fmt:
	npx prettier -w .

lint:
	npm run -w apps/orchestrator lint && npm run -w packages/workers lint

test:
	npm run -w apps/orchestrator test -- --watch=false && npm run -w packages/workers test -- --watch=false

build:
	npm run -w apps/orchestrator build && npm run -w apps/console build && npm run -w packages/workers build
```

## 19.4 `package.json` (snippets)
**CLI (`chispart-cli/package.json`)**
```json
{
  "type":"module",
  "scripts":{
    "dev":"tsx src/cli/index.ts",
    "build":"tsc -p .",
    "ws:start":"node dist/cli/index.js ws start --port 8765",
    "exec":"node dist/cli/index.js exec --cwd . -- \"git status\"",
    "test":"vitest run"
  }
}
```

**Orchestrator (`apps/orchestrator/package.json`)**
```json
{
  "type":"module",
  "scripts":{
    "dev":"nest start --watch",
    "build":"nest build",
    "start":"node dist/main.js",
    "db:migrate":"prisma migrate deploy || true",
    "lint":"eslint ."
  }
}
```

**Workers (`packages/workers/package.json`)**
```json
{
  "type":"module",
  "scripts":{
    "dev":"tsx src/index.ts",
    "build":"tsc -p .",
    "start":"node dist/index.js",
    "lint":"eslint .",
    "test":"vitest run"
  }
}
```

## 19.5 Scripts útiles
**`chispart-cli/scripts/run-cli.sh`**
```bash
#!/usr/bin/env bash
set -euo pipefail
export CHISPART_ALLOWLIST=${CHISPART_ALLOWLIST:-./config/allowlist.json}
export CHISPART_LOG_LEVEL=${CHISPART_LOG_LEVEL:-info}
node dist/cli/index.js ws start --port 8765 --token devtoken
```

**`chispart-cloud-agents/scripts/dev.sh`**
```bash
#!/usr/bin/env bash
set -euo pipefail
make up
sleep 4
make seed || true
make logs
```

**`chispart-cloud-agents/scripts/seed.sh`** (si prefieres fuera de `make`)
```bash
#!/usr/bin/env bash
set -euo pipefail
# ejemplo: crear tablas/indice inicial
npm --prefix apps/orchestrator run db:migrate || true
```

## 19.6 `config/allowlist.json` (para CLI y shell‑worker)
```json
{
  "gratis": ["git status","git diff","ls","cat","grep"],
  "basico": ["git status","git diff","git checkout","git add","git commit","git push","ls","cat","grep","npm ci","npm run build","npm test"],
  "pro": ["git *","npm *","pnpm *","yarn *","pytest *","python *","node *","bash -lc *"]
}
```

## 19.7 Quickstart (local)
1) **Cloud Agents**: `cd chispart-cloud-agents && ./scripts/dev.sh` → abre http://localhost:3000 y API en :4000.
2) **CLI**: `pnpm -C chispart-cli build && ./scripts/run-cli.sh` → luego prueba `pnpm -C chispart-cli exec -- -- \"git status\"`.
3) **VNC desde Termux**: sigue pasos de la sección 18 (túnel SSH + VNC sólo en localhost).

> Con esto, Blackbox puede generar el esqueleto completo y tú puedes levantar todo en minutos. Ajusta ORM/migraciones según el stack que elijas.


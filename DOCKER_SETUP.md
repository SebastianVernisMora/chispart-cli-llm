# Docker-based Local Development Environment

This document describes the setup for a local development environment using Docker Compose. The goal is to provide a consistent and easy-to-use environment for developing and testing the `chispart` services.

## Overview

The local environment is defined in the `docker-compose.yml` file and consists of the following services:

-   **`postgres`**: A PostgreSQL database for data persistence.
-   **`redis`**: A Redis instance for caching and message queuing.
-   **`minio`**: A MinIO instance for S3-compatible object storage.
-   **`console`**: The main user-facing web application, accessible at `http://localhost:3000`. This service uses the `chispart-mobile` application.
-   **`orchestrator`**: The main backend API, accessible at `http://localhost:4000`. This service also uses the `chispart-mobile` application, configured to run as the API.
-   **`worker`**: A worker service, accessible at `http://localhost:8080`. This service uses the `chispart-cloud` application.


## Prerequisites

-   Docker
-   Docker Compose (V2 plugin, i.e., `docker compose`)
-   `make`

## Getting Started

The environment is managed through a `Makefile` in the root of the repository.

To build the Docker images and start all the services, run:

```bash
make dev
```

This command will:
1.  Build the Docker images for the `console`, `orchestrator`, and `worker` services.
2.  Start all the services defined in `docker-compose.yml` in detached mode.
3.  Tail the logs for the `orchestrator`, `console`, and `worker` services.

### Other useful commands

-   **`make down`**: Stops and removes all the containers, networks, and volumes.
-   **`make logs`**: Tails the logs of the running services.
-   **`make ps`**: Lists the running containers.

### Database Migrations

There is no clear database migration mechanism in the provided source code. The `seed` command has been removed from the `Makefile`. If you need to run database migrations, you will need to add a command to the `Makefile` and potentially create migration scripts.

## Important Note: Docker Hub Rate Limit

During the setup of this environment, I encountered a persistent Docker Hub rate limit for unauthenticated users. This prevented the base images for `postgres`, `redis`, and `minio` from being pulled.

I have attempted the following workarounds without success:
-   Waiting for the rate limit to expire.
-   Changing the tags of the images to older versions.
-   Using an alternative registry (`quay.io`) for the `minio` images.

**To resolve this issue, you will likely need to authenticate with Docker Hub before running `make dev`.** You can do this by running `docker login` and providing your Docker Hub credentials.

## Configuration Files

For reference, here are the contents of the configuration files that were created for this setup.

### `docker-compose.yml`

```yaml
version: "3.9"
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: chispart
      POSTGRES_PASSWORD: chispart
      POSTGRES_DB: agents
    ports: ["5432:5432"]
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:6-alpine
    ports: ["6379:6379"]

  minio:
    image: quay.io/minio/minio:stable
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    ports: ["9000:9000","9001:9001"]
    volumes:
      - minio:/data

  # job para crear bucket "artifacts" en minio
  minio-mc:
    image: quay.io/minio/mc:latest
    depends_on: [minio]
    entrypoint: ["/bin/sh","-c"]
    command: >
      "mc alias set local http://minio:9000 minioadmin minioadmin &&
       mc mb -p local/artifacts || true &&
       mc anonymous set download local/artifacts || true &&
       sleep 1"

  orchestrator:
    build:
      context: ./chispart-mobile
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
    command: python3 app.py --host 0.0.0.0 --port 4000

  console:
    build:
      context: ./chispart-mobile
    depends_on: [orchestrator]
    environment:
      NODE_ENV: development
      NEXT_PUBLIC_API_URL: http://localhost:4000
    ports: ["3000:3000"]
    command: python3 app.py --host 0.0.0.0 --port 3000

  worker:
    build:
      context: ./chispart-cloud
    depends_on: [postgres, redis, minio]
    environment:
      NODE_ENV: development
      POSTGRES_URL: postgres://chispart:chispart@postgres:5432/agents
      REDIS_URL: redis://redis:6379
      S3_ENDPOINT: http://minio:9000
      S3_ACCESS_KEY: minioadmin
      S3_SECRET_KEY: minioadmin
      S3_BUCKET: artifacts
      JWT_SECRET: devsecret
    ports: ["8080:8080"]
    command: python3 app.py --host 0.0.0.0 --port 8080

volumes:
  pgdata:
  minio:
```

### `Makefile`

```makefile
.PHONY: up down logs ps dev fmt lint test build

up:
	docker compose up -d --build

down:
	docker compose down -v

logs:
	docker compose logs -f --tail=200 orchestrator console worker

ps:
	docker compose ps

dev: up logs

fmt:
	npx prettier -w .

lint:
	npm run -w apps/orchestrator lint && npm run -w packages/workers lint

test:
	npm run -w apps/orchestrator test -- --watch=false && npm run -w packages/workers test -- --watch=false

build:
	npm run -w apps/orchestrator build && npm run -w apps/console build && npm run -w packages/workers build
```

### `chispart-mobile/Dockerfile`

```dockerfile
# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install Node.js and npm
RUN apt-get update && \
    apt-get install -y curl && \
    curl -sL https://deb.nodesource.com/setup_14.x | bash - && \
    apt-get install -y nodejs

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the package.json and package-lock.json files
COPY package.json ./
COPY package-lock.json ./

# Install Node.js dependencies
RUN npm install

# Copy the rest of the application's code
COPY . .

# The command to run the application will be specified in the docker-compose.yml file
```

### `chispart-cloud/Dockerfile`

```dockerfile
# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code
COPY . .

# The command to run the application will be specified in the docker-compose.yml file
```

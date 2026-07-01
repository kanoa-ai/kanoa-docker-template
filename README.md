# kanoa-docker-template

A template repository for spinning up a local - version controlled [Ignition](https://inductiveautomation.com/)
gateway with KanoaMES and a SQL Server database via Docker Compose. Use it as the
starting point for your own implementation.

> [!WARNING]
> This repository is intended for development use only. Deploying this Docker stack in a production environment violates Microsoft SQL Server's licensing terms.

## Services

| Service | Image | Description |
| --- | --- | --- |
| `db` | `mcr.microsoft.com/mssql/server:2022-latest` | SQL Server (Developer edition) |
| `db-init` | `mcr.microsoft.com/mssql-tools:latest` | One-shot job that creates the application database on startup, then exits |
| `kanoa` | `inductiveautomation/ignition:8.3.7` | Ignition gateway with the Embr Charts(6.0.1) and KanoaMES modules(1.15.0) |

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- (Optional) An external [Traefik](https://traefik.io/) proxy if you want to use
  hostname-based routing instead of direct port access.

## Getting started

1. **Create your environment file.** Copy the example and adjust the values:

   ```bash
   cp .env.example .env
   ```

   The `.env` file is gitignored, so your secrets stay local.

2. **Set the SQL Server SA password** in `.env`. SQL Server requires a strong
   password — at least 8 characters using at least three of: uppercase,
   lowercase, digits, and symbols. Compose will refuse to start if `SA_PASSWORD`
   is unset.

   ```ini
   SA_PASSWORD=YourStrongP@ssw0rd
   ```

3. **Start the stack:**

   ```bash
   docker compose up -d
   ```

   On startup, the `kanoa` gateway waits for the `db` service to pass its
   healthcheck before launching, so Ignition never comes up before SQL Server is
   ready to accept connections.

## Common commands

The most-used Docker Compose commands (the compose file selection, including any
local overrides, is driven by `COMPOSE_FILE` in `.env`):

| Command | Description |
| --- | --- |
| `docker compose up -d` | Start the stack in the background |
| `docker compose down` | Stop and remove the containers |
| `docker compose restart` | Restart the stack |
| `docker compose logs -f` | Tail all logs (`docker compose logs -f kanoa` for one service) |
| `docker compose ps` | Show running services |
| `docker compose exec kanoa bash` | Open a shell in the Ignition container |
| `docker compose exec db bash` | Open a shell in the db container |
| `docker compose config` | Validate and print the merged compose config |
| `docker compose down -v` | Stop the stack and **delete volumes** (wipes the database) |

## Accessing the Ignition gateway

The template supports two mutually exclusive access options. Pick whichever fits
your setup by editing `docker-compose.yaml`.

### Option A — external Traefik proxy (default, preferred)

This is the recommended way to reach the gateway. Instead of juggling host
ports, you get a clean hostname like <http://kanoa-dev.localtest.me> that routes
straight to the container. `*.localtest.me` resolves to `127.0.0.1` for everyone
with no `/etc/hosts` edits, so the same URL works on every machine.

The proxy itself lives in a separate repo,
[`kanoa-ai/traefik-proxy`](https://github.com/kanoa-ai/traefik-proxy) a small
Docker Compose stack that runs a single Traefik container. You run it once and it
serves every project that joins its network.

**One-time setup:**

1. Create the shared `proxy` network (the proxy and this stack both attach to
   it):

   ```bash
   docker network create proxy
   ```

2. Clone and start the proxy (leave it running in the background):

   ```bash
   git clone https://github.com/kanoa-ai/traefik-proxy.git
   cd traefik-proxy
   docker compose up -d
   ```

**How this stack plugs in:** the `kanoa` service is already wired for the proxy —
it joins the external `proxy` network and carries these labels in
`docker-compose.yaml`:

```yaml
labels:
  traefik.enable: "true"
  traefik.hostname: "kanoa-dev"   # → http://kanoa-dev.localtest.me
```

With the proxy running, `docker compose up -d` is all you need; the gateway is
reachable at <http://kanoa-dev.localtest.me>.

**Picking your own subdomain:** the `kanoa-dev` part is just the value of the
`traefik.hostname` label on the `kanoa` service in `docker-compose.yaml`. Change
it to anything you like and the gateway moves to `<your-name>.localtest.me`. For
example, setting it to `traefik.hostname: "acme-line1"` makes the gateway
available at <http://acme-line1.localtest.me> after a `docker compose up -d`.

### Option B — direct host port (no Traefik)

If you are not running Traefik, edit `docker-compose.yaml`:

1. Uncomment the `ports` block under the `kanoa` service:

   ```yaml
   ports:
     - 8088:8088
   ```

2. Remove (or comment out) the `- proxy` entry under the `kanoa` service's
   `networks`, the `traefik.*` labels, and the `proxy` network definition at the
   bottom of the file.

The gateway is then reachable at <http://localhost:8088>.

## Application database

You shouldn't use SQL Server's built-in `master` database for application data,
so the stack provisions a dedicated database automatically — no manual setup
required:

- A one-shot **`db-init`** service runs on `docker compose up`. Once the `db` service is
  healthy, it creates the application database (default name `kanoa`) if it
  doesn't already exist, then exits. It's idempotent, so it's safe on every
  startup.
- The `kanoa` gateway waits for `db-init` to finish successfully before starting.
- The Ignition `kanoaCore` connection is pre-configured to point at this database.

### Changing the database name

Set `DB_NAME` in your `.env` (defaults to `kanoa`). If you change it, also update
the Ignition connection's `connectionProps` so the two stay in sync
(`services/ignition/config/resources/core/ignition/database-connection/kanoaCore/config.json`):

```diff
- "connectionProps": "databaseName=kanoa",
+ "connectionProps": "databaseName=<your-db-name>",
```

After changing either, run `docker compose restart`. You can confirm the connection is
**Valid** on the Gateway's **Config → Databases → Connections** page.

## Database access

By default the `db` service is only reachable from within the Compose network.
To connect to SQL Server directly from your host (e.g. with a SQL client),
uncomment the `ports` block under the `db` service:

```yaml
ports:
  - 1433:1433
```

## Local Compose overrides

You can layer machine-specific changes on top of the base `docker-compose.yaml`
without editing it (and without committing your local tweaks). This is the
recommended way to adapt the stack to your own environment.

Overrides work by stacking Compose files via the `COMPOSE_FILE` variable in
`.env`. The files are merged left-to-right, so later files override earlier
ones:

```ini
COMPOSE_FILE=docker-compose.yaml:.local/docker-compose.override.yaml
```

Keep your overrides under `.local/` — it is gitignored, so they stay on your
machine only. An override file lists just the services and fields you want to
change; everything else is inherited from the base file.

### Example: running on macOS (Apple Silicon)

The full SQL Server image (`mcr.microsoft.com/mssql/server`) does not run on
ARM64 Macs. The included `.local/docker-compose.override.yaml` swaps it for
[Azure SQL Edge](https://learn.microsoft.com/azure/azure-sql-edge/), which
supports ARM64:

```yaml
services:
  db:
    image: mcr.microsoft.com/azure-sql-edge:latest
    environment:
      ACCEPT_EULA: "1"
      MSSQL_SA_PASSWORD: "${SA_PASSWORD}"
      MSSQL_PID: Developer
```

> [!NOTE] Azure SQL Edge reads the password from MSSQL_SA_PASSWORD rather
> than SA_PASSWORD. Referencing ${SA_PASSWORD} keeps a single source of truth in your .env.

With the `COMPOSE_FILE` line above set in `.env`, `docker compose up -d` will
automatically apply the override — no extra flags needed. To run without it,
remove the override path from `COMPOSE_FILE` (or unset it to fall back to just
`docker-compose.yaml`).

## Environment variables

| Variable | Description |
| --- | --- |
| `SA_PASSWORD` | SQL Server SA account password (**required**). |
| `DB_NAME` | Application database created on startup (default `kanoa`). |
| `COMPOSE_PROJECT_NAME` | Docker Compose project name. |
| `COMPOSE_FILE` | Compose files to load, including the local override. |

See `.env.example` for the full list and defaults.

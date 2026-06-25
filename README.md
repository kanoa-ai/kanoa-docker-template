# kanoa-docker-template

A template repository for spinning up a local [Ignition](https://inductiveautomation.com/)
gateway with KanoaMES and a SQL Server database via Docker Compose. Use it as the
starting point for your own project repos.

## Services

| Service | Image | Description |
| --- | --- | --- |
| `db` | `mcr.microsoft.com/mssql/server:2022-latest` | SQL Server (Developer edition) |
| `kanoa` | `inductiveautomation/ignition:8.3.7` | Ignition gateway with the Embr Charts and KanoaMES modules |

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
   make up        # or: docker compose up -d
   ```

   On startup, the `kanoa` gateway waits for the `db` service to pass its
   healthcheck before launching, so Ignition never comes up before SQL Server is
   ready to accept connections.

## Common commands

A `Makefile` wraps the most-used Docker Compose commands. Run `make` (or
`make help`) to see them all:

| Command | Description |
| --- | --- |
| `make up` | Start the stack in the background |
| `make down` | Stop and remove the containers |
| `make restart` | Restart the stack |
| `make logs` | Tail all logs (`make logs s=kanoa` for one service) |
| `make ps` | Show running services |
| `make shell` | Open a shell in the Ignition container |
| `make db-shell` | Open a shell in the db container |
| `make config` | Validate and print the merged compose config |
| `make clean` | Stop the stack and **delete volumes** (wipes the database) |

## Accessing the Ignition gateway

The template supports two mutually exclusive access options. Pick whichever fits
your setup by editing `docker-compose.yaml`.

### Option A — external Traefik proxy (default)

The `kanoa` service is wired to an external Traefik proxy via the `traefik.*`
labels and the external `proxy` network. This network must already exist:

```bash
docker network create proxy
```

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

> **Note:** Azure SQL Edge reads the password from `MSSQL_SA_PASSWORD` rather
> than `SA_PASSWORD`. Referencing `${SA_PASSWORD}` keeps a single source of
> truth in your `.env`.

With the `COMPOSE_FILE` line above set in `.env`, `docker compose up -d` will
automatically apply the override — no extra flags needed. To run without it,
remove the override path from `COMPOSE_FILE` (or unset it to fall back to just
`docker-compose.yaml`).

## Environment variables

| Variable | Description |
| --- | --- |
| `SA_PASSWORD` | SQL Server SA account password (**required**). |
| `COMPOSE_PROJECT_NAME` | Docker Compose project name. |
| `COMPOSE_FILE` | Compose files to load, including the local override. |

See `.env.example` for the full list and defaults.

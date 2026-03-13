# CHAOS: CHAOS Hosts Absurd Outcome Speculations

This repository currently hosts the REST backend for the CHAOS app.

⚠️ This project is still in development

## Self hosting configuration

### Environment Variables (api)

To configure the backend api, create a new `.env` file in the `api/` directory based on the `.env.example` file.

| Variable | Description | Default |
| :--- | :--- | :--- |
| `SQL_ECHO` | If set to `1`, all SQL queries will be printed to standard output. This is useful for debugging. | `1` |
| `INITIAL_POINTS` | The amount of points a new user has when they are created. | `1000` |
| `ALGORITHM` | The algorithm used to sign the JWTs (JSON Web Tokens). | `HS256` |
| `JWT_EXP_DAYS` | The amount of days a JWT is valid for. | `1` |

### Environment Variables (proxy)

To configure the backend services, create a `.env` file in the `backend/` directory based on the `.env.example` file.

| Variable | Description | Example |
| :--- | :--- | :--- |
| `DOMAIN` | Your full domain name (for SSL and Nginx). | `example.duckdns.org` |
| `BASIC_AUTH` | Enables Basic Auth if set (e.g., "Restricted Area"). Set to `off` to disable. | `Restricted Area` |
| `STAGING` | Use `1` for Certbot staging (test) mode, `0` for production. | `1` |
| `CERTBOT_EMAIL` | Email for Let's Encrypt notifications. | `me@example.com` |
| `DUCKDNS_TOKEN` | Your DuckDNS API token (if using DuckDNS). | `your-token-here` |
| `SUBDOMAIN` | Your DuckDNS subdomain (e.g., "example"). | `example` |

### Running with Docker

1. Configure the `.env` file.
2. If `BASIC_AUTH` is enabled, ensure a valid `.htpasswd` file is in `backend/proxy/`.
3. Run `docker compose up -d`.

The API will be accessible via HTTPS at `https://${DOMAIN}/`.
The proxy service automatically handles SSL certificate generation and renewal via Certbot.
Template files in `backend/proxy/templates/` are processed with `envsubst` on startup, allowing dynamic configuration based on the environment variables defined above.

#### Running with BASIC AUTH

If you intend to run this server with BASIC AUTH enabled (to make the server privately accessible), you need to create a `.htpasswd` file with `htpasswd -c .htpasswd <username>` from package `apache2-utils`, for more ![info](https://nginx.org/en/docs/http/ngx_http_auth_basic_module.html)

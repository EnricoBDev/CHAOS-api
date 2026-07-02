import auth
import auth.routes
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from globals.database import create_db_and_tables
from models import Bet, Event, Market, Outcome, Transaction, User  # noqa: F401
from routes import (
    bet_router,
    event_router,
    outcome_router,
    transaction_router,
    user_router,
)

description = """
CHAOS Project API Documentation.

> **Important**: All code samples in this documentation assume the API is running behind the Nginx proxy.

## Proxy Configuration
When running the project with Docker behind the Nginx proxy, the JWT must be sent using the `X-CHAOS-Auth` header. Nginx is configured to map this header to the standard `Authorization` header before forwarding the request to the API.

## Private Server (Basic Auth)
If the project is running in "private server" mode (with Basic Auth enabled in the proxy), every request must include the `Authorization` header with valid credentials for Basic Authentication.

**Example Basic Auth header:**
`Authorization: Basic <base64_encoded_credentials>`

Where `<base64_encoded_credentials>` is the Base64 encoding of `username:password`.

## General Information
This section contains additional information, usage guides, or legal notes in Markdown format.
"""

app = FastAPI(
    title="CHAOS API",
    description=description,
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,  # ty:ignore[invalid-argument-type]
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    user_router.router,
)
app.include_router(
    auth.routes.router,
)
app.include_router(
    event_router.router,
)
app.include_router(
    transaction_router.router,
)
app.include_router(bet_router.router)
app.include_router(outcome_router.router)


@app.on_event("startup")  # ty:ignore[deprecated]
def on_startup():
    create_db_and_tables()

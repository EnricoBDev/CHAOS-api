from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import auth
import auth.routes
from globals.database import create_db_and_tables
from models import Bet, Event, Market, Outcome, Transaction, User  # noqa: F401
from routes import (
    bet_router,
    event_router,
    outcome_router,
    transaction_router,
    user_router,
)

app = FastAPI()

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

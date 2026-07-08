"""
main.py

FastAPI app serving the Swiss Votes data from MongoDB.

FastAPI gives us, for free:
  - /docs   -> interactive Swagger UI (try requests right in the browser)
  - /redoc  -> alternative auto-generated API reference
  - /openapi.json -> the raw OpenAPI schema

Routes:
    GET /                                  -> API root: name, version, links
    GET /api/votes/  (and /api/votes)      -> list all votes
    GET /api/votes/{anr}                   -> the single vote with this anr
                                               (anr is matched as an exact
                                               string, since some values
                                               contain a dot, e.g. "5.1")
    GET /api/legislatur                    -> list all legislatur periods
                                               (each with a "legisjahr"
                                               string and previous/next refs)
    GET /api/legislatur/latest             -> the legislatur with the
                                               highest number
    GET /api/legislatur/{number}           -> a single legislatur period
                                               (with previous/next refs)
    GET /api/legislatur/{number}/votes/
        (and .../votes)                    -> all votes in that legislatur
"""

from typing import Any

from fastapi import FastAPI, HTTPException

import db

app = FastAPI(
    title="Swissvotes API (unofficial)",
    description="Browse Swiss popular votes, grouped by legislative period (Legislatur).",
    version="0.0.2",
    contact={
        "url": "https://github.com/pascal-huber/swissvotes-api"
    },
    license_info={
        "name": "MIT License",
        "identifier": "MIT"
    }
)


@app.get("/", summary="API root", response_model=dict[str, Any])
def api_root() -> dict[str, Any]:
    """
    Root endpoint: describes the API and links to the documentation and
    main resources, so hitting '/' is never a dead end.
    """
    return {
        "name": app.title,
        "description": app.description,
        "license_info": app.license_info,
        "version": app.version,
        "contact": app.contact,
        "license_data": {
            "name": "CC BY 4.0",
            "source": "Swissvotes, Année Politique Suisse, Universität Bern",
            "url": "https://creativecommons.org/licenses/by/4.0/",
            "attribution": "Swissvotes (2025). Online: www.swissvotes.ch.",
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json",
        },
        "endpoints": {
            "votes": "/api/votes/",
            "vote_by_anr": "/api/votes/{anr}",
            "legislaturen": "/api/legislatur",
            "latest_legislatur": "/api/legislatur/latest",
            "legislatur_by_number": "/api/legislatur/{number}",
            "votes_by_legislatur": "/api/legislatur/{number}/votes/",
        },
    }


# --- Votes ------------------------------------------------------------

@app.get("/api/votes", include_in_schema=False)
@app.get("/api/votes/", summary="List all votes", response_model=list[dict[str, Any]])
def api_list_votes() -> list[dict[str, Any]]:
    return db.list_votes()


@app.get(
    "/api/votes/{anr}",
    summary="Get a single vote by anr",
    response_model=dict[str, Any],
)
def api_get_vote(anr: str) -> dict[str, Any]:
    # anr is matched as an exact string (not int/float): some votes have
    # sub-numbers like "5.1", and parsing as a number could silently
    # change or mismatch that formatting (e.g. "5.10" vs "5.1").
    vote = db.get_vote_by_anr(anr)
    if vote is None:
        raise HTTPException(status_code=404, detail=f"No vote found with anr '{anr}'")
    return vote


# --- Legislatur ---------------------------------------------------------

@app.get(
    "/api/legislatur",
    summary="List all legislatur periods",
    response_model=list[dict[str, Any]],
)
def api_list_legislaturen() -> list[dict[str, Any]]:
    return db.list_legislaturen()


# NOTE: this must be declared *before* "/api/legislatur/{number}" so that
# "latest" is tried first. In practice this isn't strictly required since
# {number} is int-typed and "latest" can never match that pattern, but
# declaring it first keeps the intent obvious and avoids any ambiguity.
@app.get(
    "/api/legislatur/latest",
    summary="Get the legislatur with the highest number",
    response_model=dict[str, Any],
)
def api_latest_legislatur() -> dict[str, Any]:
    legislatur = db.get_latest_legislatur()
    if legislatur is None:
        raise HTTPException(status_code=404, detail="No legislatur found")
    return legislatur


@app.get(
    "/api/legislatur/{number}",
    summary="Get a single legislatur period",
    response_model=dict[str, Any],
)
def api_get_legislatur(number: int) -> dict[str, Any]:
    legislatur = db.get_legislatur(number)
    if legislatur is None:
        raise HTTPException(status_code=404, detail=f"No legislatur found with number {number}")
    return legislatur


@app.get("/api/legislatur/{number}/votes", include_in_schema=False)
@app.get(
    "/api/legislatur/{number}/votes/",
    summary="List all votes in a given legislatur",
    response_model=list[dict[str, Any]],
)
def api_votes_for_legislatur(number: int) -> list[dict[str, Any]]:
    return db.get_votes_by_legislatur(number)


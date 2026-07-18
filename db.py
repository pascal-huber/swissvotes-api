"""
db.py

Shared database access/query logic, kept separate from the API framework
so it can be tested/reused independently.
"""

import os
from datetime import date

from pymongo import MongoClient

import categories

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.environ.get("MONGO_DB", "votes_db")

# The three Politikbereich (policy area) code groups on a vote document,
# each a 3-level hierarchy: d<n>e1 (top) / d<n>e2 (mid) / d<n>e3 (bottom).
_CATEGORY_FIELDS = [f"d{n}e{level}" for n in (1, 2, 3) for level in (1, 2, 3)]

_client = None


def get_collection():
    global _client
    if _client is None:
        _client = MongoClient(MONGO_URI)
    return _client[MONGO_DB]["votes"]


def _resolve_categories(vote: dict) -> dict:
    """
    Replace the raw Politikbereich fields (d1e1/d1e2/d1e3, d2e1/d2e2/d2e3,
    d3e1/d3e2/d3e3) with a single "categories" field: a list of up to three
    [level1, level2, level3] arrays of resolved text, nested per policy
    area. See categories.extract_categories().
    """
    if vote is None:
        return vote
    vote["categories"] = categories.extract_categories(vote)
    for field in _CATEGORY_FIELDS:
        vote.pop(field, None)
    return vote


def list_votes() -> list:
    """Return all votes."""
    coll = get_collection()
    return [_resolve_categories(v) for v in coll.find({}, {"_id": 0})]


def get_vote_by_anr(anr: str):
    """
    Return the single vote matching this "anr" exactly.

    "anr" is stored (and matched) as a plain string, since some values
    contain a dot (e.g. "5.1") -- matching as a string avoids any
    float-formatting ambiguity (e.g. "5.10" vs "5.1").
    """
    coll = get_collection()
    return _resolve_categories(coll.find_one({"anr": anr}, {"_id": 0}))


def get_votes_by_legislatur(number: int) -> list:
    """Return all votes belonging to the given legislatur."""
    coll = get_collection()
    cursor = coll.find({"legislatur": number}, {"_id": 0})
    return [_resolve_categories(v) for v in cursor]


def _aggregate_legislaturen() -> list:
    """
    Internal helper: returns a list of
        {"legislatur": <int>, "start": <int or None>, "end": <int or None>}
    sorted ascending by legislatur number.

    "start"/"end" are the legisjahr period's start/end years (e.g. 1848 and
    1851 for "1848-1851"), taken from the earliest start year / latest end
    year seen across the legislatur's votes.

    Only legislatur numbers that actually appear on at least one vote are
    included -- some legislatur numbers may have no votes at all and are
    therefore simply absent from this list (not represented as a "gap"
    placeholder). This is intentional: "previous"/"next" neighbours are
    computed relative to this list, not to number +/- 1.
    """
    coll = get_collection()
    pipeline = [
        {"$match": {"legislatur": {"$ne": None}}},
        {"$group": {
            "_id": "$legislatur",
            "start_years": {"$addToSet": "$legisjahr.start"},
            "end_years": {"$addToSet": "$legisjahr.end"},
        }},
    ]
    items = []
    for r in coll.aggregate(pipeline):
        start_years = sorted(v for v in r.get("start_years", []) if v is not None)
        end_years = sorted(v for v in r.get("end_years", []) if v is not None)
        items.append({
            "legislatur": r["_id"],
            "start": start_years[0] if start_years else None,
            "end": end_years[-1] if end_years else None,
        })
    items.sort(key=lambda item: item["legislatur"])
    return items


def _format_legislatur_entry(items: list, index: int) -> dict:
    """
    Build the public representation of one legislatur entry, including a
    "legisjahr" string (built from the "start"/"end" years) and
    "previous"/"next" references to the neighbouring legislatur entries in
    this list, if any.
    """
    item = items[index]
    start, end = item["start"], item["end"]
    if start is not None and end is not None:
        legisjahr_str = f"{start}-{end}"
    else:
        legisjahr_str = None

    entry = {
        "legislatur": item["legislatur"],
        "legisjahr": legisjahr_str,
        "legisjahr_start": start,
        "legisjahr_end": end,
    }

    if index > 0:
        prev_num = items[index - 1]["legislatur"]
        entry["previous"] = {"legislatur": prev_num, "href": f"/api/legislatur/{prev_num}"}
    else:
        entry["previous"] = None

    if index < len(items) - 1:
        next_num = items[index + 1]["legislatur"]
        entry["next"] = {"legislatur": next_num, "href": f"/api/legislatur/{next_num}"}
    else:
        entry["next"] = None

    return entry


def list_legislaturen() -> list:
    """Return all legislatur periods, each with its "legisjahr" string and
    "previous"/"next" neighbour references."""
    items = _aggregate_legislaturen()
    return [_format_legislatur_entry(items, i) for i in range(len(items))]


def get_legislatur(number: int):
    """Return a single legislatur entry by number (with its votes), or None
    if it has no votes."""
    items = _aggregate_legislaturen()
    for i, item in enumerate(items):
        if item["legislatur"] == number:
            entry = _format_legislatur_entry(items, i)
            entry["votes"] = get_votes_by_legislatur(number)
            return entry
    return None


def get_latest_legislatur():
    """Return the legislatur entry with the highest number (with its
    votes), or None if empty."""
    items = _aggregate_legislaturen()
    if not items:
        return None
    entry = _format_legislatur_entry(items, len(items) - 1)
    entry["votes"] = get_votes_by_legislatur(items[-1]["legislatur"])
    return entry


def get_current_legislatur():
    """
    Return the legislatur entry (with its votes) whose period
    (legisjahr_start..legisjahr_end) contains the current year, or None if
    none matches.

    If more than one legislatur's period contains the current year (i.e.
    their periods overlap), the one with the lower start year is picked
    (ties broken by the lower end year).
    """
    year = date.today().year
    items = _aggregate_legislaturen()
    matches = [
        i for i, item in enumerate(items)
        if item["start"] is not None and item["end"] is not None
        and item["start"] <= year <= item["end"]
    ]
    if not matches:
        return None
    best = min(matches, key=lambda i: (items[i]["start"], items[i]["end"]))
    entry = _format_legislatur_entry(items, best)
    entry["votes"] = get_votes_by_legislatur(items[best]["legislatur"])
    return entry


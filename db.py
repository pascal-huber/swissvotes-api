"""
db.py

Shared database access/query logic, kept separate from the API framework
so it can be tested/reused independently.
"""

import os

from pymongo import MongoClient

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.environ.get("MONGO_DB", "votes_db")

_client = None


def get_collection():
    global _client
    if _client is None:
        _client = MongoClient(MONGO_URI)
    return _client[MONGO_DB]["votes"]


def list_votes() -> list:
    """Return all votes."""
    coll = get_collection()
    return list(coll.find({}, {"_id": 0}))


def get_vote_by_anr(anr: str):
    """
    Return the single vote matching this "anr" exactly.

    "anr" is stored (and matched) as a plain string, since some values
    contain a dot (e.g. "5.1") -- matching as a string avoids any
    float-formatting ambiguity (e.g. "5.10" vs "5.1").
    """
    coll = get_collection()
    return coll.find_one({"anr": anr}, {"_id": 0})


def get_votes_by_legislatur(number: int) -> list:
    """Return all votes belonging to the given legislatur."""
    coll = get_collection()
    cursor = coll.find({"legislatur": number}, {"_id": 0})
    return list(cursor)


def _aggregate_legislaturen() -> list:
    """
    Internal helper: returns a list of
        {"legislatur": <int>, "legisjahre": [<sorted distinct ints>]}
    sorted ascending by legislatur number.

    Only legislatur numbers that actually appear on at least one vote are
    included -- some legislatur numbers may have no votes at all and are
    therefore simply absent from this list (not represented as a "gap"
    placeholder). This is intentional: "previous"/"next" neighbours are
    computed relative to this list, not to number +/- 1.
    """
    coll = get_collection()
    pipeline = [
        {"$match": {"legislatur": {"$ne": None}}},
        {"$group": {"_id": "$legislatur", "legisjahre": {"$addToSet": "$legisjahr"}}},
    ]
    items = []
    for r in coll.aggregate(pipeline):
        legisjahre = sorted(v for v in r.get("legisjahre", []) if v is not None)
        items.append({"legislatur": r["_id"], "legisjahre": legisjahre})
    items.sort(key=lambda item: item["legislatur"])
    return items


def _format_legislatur_entry(items: list, index: int) -> dict:
    """
    Build the public representation of one legislatur entry, including a
    "legisjahr" string (not an array) and "previous"/"next" references to
    the neighbouring legislatur entries in this list, if any.
    """
    item = items[index]
    legisjahr_str = ", ".join(str(v) for v in item["legisjahre"])

    entry = {
        "legislatur": item["legislatur"],
        "legisjahr": legisjahr_str,
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
    """Return a single legislatur entry by number, or None if it has no votes."""
    items = _aggregate_legislaturen()
    for i, item in enumerate(items):
        if item["legislatur"] == number:
            return _format_legislatur_entry(items, i)
    return None


def get_latest_legislatur():
    """Return the legislatur entry with the highest number, or None if empty."""
    items = _aggregate_legislaturen()
    if not items:
        return None
    return _format_legislatur_entry(items, len(items) - 1)


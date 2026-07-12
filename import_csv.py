#!/usr/bin/env python3
"""
import_csv.py

Loads/refreshes a "votes" collection in MongoDB from a (regularly
republished) CSV file, e.g. the Swiss Votes dataset.

- Full atomic refresh via a "votes_staging" collection + rename.
- Column names slugified into safe, stable field names.
- Empty CSV cells are dropped entirely (sparse rows only keep real data).
- Field names grouped by their FIRST underscore into nested sub-documents,
  e.g. "titel_kurz_de" -> {"titel": {"kurz_de": ...}}.
- "legislatur" is parsed as int and indexed.
- "legisjahr" (format "<start-year>-<end-year>") is split into
  "legisjahr_start" and "legisjahr_end" int fields, which are then grouped
  (like any other "prefix_rest" field) into a nested
  {"legisjahr": {"start": ..., "end": ...}} sub-document.
- "anr" is kept as the RAW STRING from the CSV (not parsed as a number),
  since some values contain a dot, e.g. "5.1" -- converting to float would
  risk losing/altering that formatting (e.g. "5.10" -> 5.1).

Usage:
    python3 import_csv.py path/to/data.csv \
        --mongo-uri mongodb://localhost:27017 --db votes_db
"""

import argparse
import csv
import os
import re
import sys
from pathlib import Path

from pymongo import MongoClient

INT_FIELDS = {"legislatur"}
LEGISJAHR_RE = re.compile(r"^\s*(\d{4})\s*-\s*(\d{4})\s*$")


def slugify_column(name: str) -> str:
    name = name.strip().lower()
    replacements = {
        "ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss",
        "é": "e", "è": "e", "à": "a",
    }
    for src, dst in replacements.items():
        name = name.replace(src, dst)
    name = re.sub(r"[^a-z0-9]+", "_", name)
    name = name.strip("_")
    if not name:
        name = "col"
    if name[0].isdigit():
        name = f"c_{name}"
    return name


def sniff_dialect(sample: str) -> csv.Dialect:
    try:
        return csv.Sniffer().sniff(sample, delimiters=",;\t")
    except csv.Error:
        class Default(csv.excel):
            delimiter = ","
        return Default()


def read_csv_rows(path: Path):
    last_err = None
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            with open(path, newline="", encoding=encoding) as f:
                sample = f.read(4096)
                f.seek(0)
                dialect = sniff_dialect(sample)
                reader = csv.DictReader(f, dialect=dialect)
                fieldnames = reader.fieldnames
                rows = list(reader)
            return fieldnames, rows
        except UnicodeDecodeError as e:
            last_err = e
            continue
    raise last_err


def group_fields(flat: dict) -> dict:
    """
    Group a flat {slug_field: value} dict into nested sub-documents by
    splitting each field name on its FIRST underscore only.

        "a_b_c_d" -> grouped["a"]["b_c_d"]
        "legislatur" (no underscore) -> grouped["legislatur"] (stays flat)

    Handles the edge case where the same prefix is used both as a flat
    scalar AND as a group elsewhere in the same row: the scalar is kept
    under a "_value" key so no data is silently lost or overwritten.
    """
    grouped: dict = {}
    for key, value in flat.items():
        if "_" in key:
            prefix, rest = key.split("_", 1)
        else:
            prefix, rest = key, None

        if rest is None:
            existing = grouped.get(prefix)
            if isinstance(existing, dict):
                existing["_value"] = value
            else:
                grouped[prefix] = value
        else:
            existing = grouped.get(prefix)
            if isinstance(existing, dict):
                existing[rest] = value
            elif existing is None:
                grouped[prefix] = {rest: value}
            else:
                grouped[prefix] = {"_value": existing, rest: value}
    return grouped


def row_to_document(fieldnames, final_columns, row) -> dict:
    flat = {}
    for orig_col, slug_col in zip(fieldnames, final_columns):
        raw = row.get(orig_col)
        if raw is not None:
            raw = raw.strip()
        if raw == "" or raw is None:
            continue  # drop empty values entirely

        if slug_col == "legisjahr":
            match = LEGISJAHR_RE.match(raw)
            if match:
                flat["legisjahr_start"] = int(match.group(1))
                flat["legisjahr_end"] = int(match.group(2))
            else:
                flat[slug_col] = raw  # fall back to raw string if unparsable
        elif slug_col in INT_FIELDS:
            try:
                flat[slug_col] = int(float(raw))
            except ValueError:
                flat[slug_col] = raw  # fall back to raw string if unparsable
        else:
            # "anr" and everything else: keep as the exact raw string,
            # so values like "5.1" are preserved exactly as published.
            flat[slug_col] = raw
    return group_fields(flat)


def build_final_columns(fieldnames):
    slug_columns = [slugify_column(f) for f in fieldnames]
    seen = {}
    final_columns = []
    for c in slug_columns:
        if c in seen:
            seen[c] += 1
            c = f"{c}_{seen[c]}"
        else:
            seen[c] = 0
        final_columns.append(c)
    return final_columns


def import_csv(csv_path: Path, mongo_uri: str, db_name: str):
    fieldnames, rows = read_csv_rows(csv_path)
    if not fieldnames:
        print("ERROR: could not read any columns from the CSV.", file=sys.stderr)
        sys.exit(1)

    final_columns = build_final_columns(fieldnames)
    documents = [row_to_document(fieldnames, final_columns, row) for row in rows]

    client = MongoClient(mongo_uri)
    try:
        db = client[db_name]

        staging = db["votes_staging"]
        staging.drop()
        if documents:
            staging.insert_many(documents)
        staging.create_index("legislatur")
        staging.create_index("anr")

        staging.rename("votes", dropTarget=True)

        print(f"Imported {len(documents)} documents, "
              f"{len(final_columns)} source columns into "
              f"'{db_name}.votes' at {mongo_uri}.")
    finally:
        client.close()


def main():
    parser = argparse.ArgumentParser(description="Import/update the votes CSV into MongoDB.")
    parser.add_argument("csv_path", type=Path, help="Path to the CSV file")
    parser.add_argument(
        "--mongo-uri",
        default=os.environ.get("MONGO_URI", "mongodb://localhost:27017"),
        help="MongoDB connection URI",
    )
    parser.add_argument(
        "--db",
        default=os.environ.get("MONGO_DB", "votes_db"),
        help="MongoDB database name",
    )
    args = parser.parse_args()

    if not args.csv_path.exists():
        print(f"ERROR: CSV file not found: {args.csv_path}", file=sys.stderr)
        sys.exit(1)

    import_csv(args.csv_path, args.mongo_uri, args.db)


if __name__ == "__main__":
    main()


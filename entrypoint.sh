#!/bin/bash
set -e

echo "Starting MongoDB..."
mongod --dbpath /data/db --bind_ip_all --fork --logpath /var/log/mongod.log

echo "Waiting for MongoDB to accept connections..."
until mongosh --quiet --eval "db.runCommand({ ping: 1 })" >/dev/null 2>&1; do
  sleep 1
done
echo "MongoDB is up."

if [ -n "$CSV_PATH" ] && [ -f "$CSV_PATH" ]; then
  echo "Importing $CSV_PATH into MongoDB..."
  python3 import_csv.py "$CSV_PATH"
else
  echo "No CSV_PATH set or file not found, skipping import."
fi

echo "Starting API on port ${PORT:-5000}..."
exec python3 -m uvicorn main:app --host 0.0.0.0 --port "${PORT:-5000}"

# Single container running both MongoDB and the API.
# Based on the official MongoDB image (which already contains mongod +
# mongosh), with Python/FastAPI layered on top.
FROM mongo:7

# --- Python + API dependencies -----------------------------------------
RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Belt-and-suspenders: make sure pip-installed console scripts are
# findable regardless of what PATH the base image sets.
ENV PATH="/usr/local/bin:${PATH}"

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY import_csv.py db.py main.py categories.py entrypoint.sh ./
RUN chmod +x entrypoint.sh

COPY data/swissvotes.ch.csv /data/data.csv

ENV MONGO_URI=mongodb://localhost:27017
ENV MONGO_DB=votes_db
ENV PORT=5000
ENV CSV_PATH=/data/data.csv

VOLUME ["/data/db"]

EXPOSE 5000

ENTRYPOINT ["./entrypoint.sh"]


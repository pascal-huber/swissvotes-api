# Swissvotes API

This repo contains an unofficial API for the *Swissvotes-Datensatz* published
on swissvotes.ch. 

Demo: https://swissvotes-api.resolved.ch

## Disclaimer

This is a first version and the API is still subject to breaking changes.

## License

- **Code** in this repository is licensed under the [MIT License](LICENSE).
- **Data** in `data/swissvotes.ch.csv` is third-party data from
  [Swissvotes](https://swissvotes.ch) (Année Politique Suisse, Universität
  Bern), licensed under [CC BY
  4.0](https://creativecommons.org/licenses/by/4.0/) — see
  [`LICENSE-DATA`](data/LICENSE-DATA.md) for the required attribution.
  This data is not created by this project's authors.

## Data

The data from the (official) swissvotes CSV is changed as follows:

 - Field names with an underscore are split (for example `"info\_br\_de":
   "..."` becomes `"info": {"br": {"de": "..."}}}`).
 - Fields without a value are omitted.
 - The raw `d1e1`/`d1e2`/`d1e3`, `d2e1`/`d2e2`/`d2e3` and `d3e1`/`d3e2`/`d3e3`
   Politikbereich (policy area) codes are replaced by a single `categories`
   field: a list of up to three `[level1, level2, level3]` arrays (one per
   policy area the vote is tagged with), most-general-first, holding the
   resolved German text as deep as it's assigned, e.g.:
   ```json
   "categories": [
     ["Staatsordnung", "Politisches System", "Bundesverfassung"],
     ["Staatsordnung", "Föderalismus"]
   ]
   ```
   See [`categories.py`](categories.py) for the full code table,
   transcribed from the Swissvotes codebook.

## Running it

```
docker pull ghcr.io/pascal-huber/swissvotes-api:latest
docker run -d --name votes-api -p 5000:5000 ghcr.io/pascal-huber/swissvotes-api:latest
```

## Build Instructions

```
docker build -t votes-api .
docker run -d --name votes-api -p 5000:5000 votes-api

```



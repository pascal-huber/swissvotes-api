# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Fixed

### Changed

### Removed

## [0.1.0] - 2026-07-18

### Changed

- The raw `d1e1`/`d1e2`/`d1e3`, `d2e1`/`d2e2`/`d2e3` and `d3e1`/`d3e2`/`d3e3`
  Politikbereich fields on votes are replaced by a single `categories`
  field: a list of up to three `[level1, level2, level3]` arrays holding
  the resolved German category text, nested per policy area. See
  `categories.py`. **Breaking**: consumers reading the old `d*e*` fields
  need to switch to `categories`.

## [0.0.4] - 2026-07-12

### Changed

 - Split field names by all underscores (not just the first)

## [0.0.3] - 2026-07-12

### Added

 - Add /api/legislatur/current endpiont

### Changed

 - Include votes data on legislatur endpoints
 - Add fields for start- and end year of each legislatur

### Removed

 - Endpoint /api/legislatur/.../votes

## [0.0.2] - 2026-07-08

### Changed

 - Refined info on API root page

## [0.0.1] - 2026-07-08

### Added

 - Initial version of the API
 - Write data from CSV into MongoDB
 - License Information
 - Build Instructions
 - Github pipeline to publish the image


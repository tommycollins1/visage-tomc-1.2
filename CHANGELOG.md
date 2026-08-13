# Changelog — ViSAGE

All notable changes to this project will be documented here.

## [1.2.0-dev] — 2026-08-12
### Changed
- Renamed `main_cfg.py` to `paths_cfg.py` (paths only) and added `params_cfg.py`
  for model parameters (`VISITS_PER_PERSON`, `BASELINE_LAMBDA_VALUE`,
  `BETA_QUALITY`, Oxford North scenario constants). Every example script now
  imports from these instead of redefining its own local placeholders.
- Consolidated data into a single canonical `data/` folder at the repo root:
  `data/` for active model inputs, `data/_archive/` for superseded v1.1-format
  files (kept for reference, not deleted), `data/external/` for
  validation/reference datasets (ORVal join, Overture POI join, Strava
  timeseries), `data/boundaries/` for the Oxford LAD 10-mile buffer.
- Removed `examples/VISAGE-1.2/`, a nested duplicate of the entire v1.2
  snapshot (confirmed byte-identical to `src/model_v12/`, the data files, and
  `notebooks/`, except one empty stub notebook). The unique bit of its
  README was preserved at `data/_archive/VISAGE-1.2-snapshot-README.md`.
- Reconciled the distance-decay convention (`lambda_m` / `exp(-d/lambda_m)`
  -> `lambda_value` / `exp(-lambda_value*d)`) in `src/model/spatial_interaction.py`
  and `src/model_v12/spatial_interaction.py`, matching v1.1's fix.
- Consolidated the Euclidean distance calculation, previously duplicated in
  four places, into `src/model/distance.py` (`bng_distance`,
  `build_distance_matrix`). `src/model_v12/spatial_interaction.py`,
  `src/scenario/add_origin.py`, `examples/run_quality.py`, and
  `examples/run_quality_v12.py` now all use the shared implementation.

### Fixed
- `examples/run_oxford_north.py`: corrected imports from the non-existent
  `src.scenarios` package to `src.scenario`, and from `scenario_triptych` to
  the actual module `scenario_tryptych`; corrected the `compute_scenario_visits`
  call, which passed `lambda_value` to `run_gravity_with_pans_lambda` (doesn't
  accept it) - switched to `run_gravity_with_lambda`.
- `examples/run_quality.py`, `examples/run_oxford_north.py`,
  `examples/run_quality_v12.py`: pointed at the now-consolidated data paths
  via `paths_cfg` (previously pointed at `data/raw/...` or `src/data/raw/...`,
  neither of which matched where the files actually were).

### Notes
- `run_quality.py`, `run_oxford_north.py`, and `run_quality_v12.py`
  currently run against the archived v1.1-format destinations
  (`ARCHIVED_SITE_CATALOGUE_WITH_QUALITY`) rather than the new
  `site_cat_access_union.csv`, since the new file doesn't yet have
  QualityScore or a clean one-row-per-site structure. Update once that
  work lands.
- `run_baseline.py` is the one script already wired to the new access-point
  level data; it's mid-experiment (SSSI-only filter, `id_col="access_pt_id"`)
  and was left untouched here.

## [1.1.0] — 2026-03-20
### Added
- Full baseline spatial interaction model
- PaNS-calibrated distance-decay module
- Quality-sensitive model (QualityScore attractor)
- Oxford North scenario engine
- Publication-grade visualisation modules
- Example scripts: baseline, quality, scenario
- Clean modular architecture aligned with NE technical report

### Removed
- Deprecated exploratory modules
- Duplicate quality attractor
- Unused scenario engines
- Unused visualisation files

### Notes
This is the first stable, complete release of ViSAGE.
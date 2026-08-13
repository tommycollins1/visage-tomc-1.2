# visage-1.2

# 🌿 **README.md — ViSAGE v1.2**

# **ViSAGE v1.2 — Visitation, Spatial Accessibility & Greenspace Exposure**  
*A modular spatial‑interaction modelling framework for greenspace visitation*  
**Natural England Technical Report (2024–2025)**

---

## 🌱 **Overview**

**ViSAGE v1.2** is a modular, open, and reproducible spatial‑interaction modelling framework designed to estimate:

- baseline greenspace visitation  
- quality‑sensitive visitation  
- scenario‑based changes (e.g., Oxford North development)  

It implements the full modelling workflow described in the **Natural England Technical Report**, including:

- behavioural distance‑decay calibration (PaNS)  
- origin–destination gravity modelling  
- quality‑based attractiveness  
- ranking comparisons  
- scenario impacts  
- publication‑grade visualisations  

The codebase is structured for clarity, extensibility, and scientific transparency.

---

## 🌳 **Repository Structure**

```
visage-tomc-1.2/
│
├── paths_cfg.py          # every filesystem path used by the project - single source of truth
├── params_cfg.py         # model parameters (visits/person, lambda, beta, Oxford North scenario)
│
├── data/
│   ├── ox_synthetic_pop_origin.csv        # active origins input
│   ├── site_cat_access_union.csv          # active destinations input (access-point level, has_agi/has_sac/has_sssi booleans)
│   ├── _archive/          # superseded v1.1-format files, kept for reference (not deleted)
│   ├── external/          # reference/validation data: ORVal join, Overture POI join, Strava
│   └── boundaries/        # oxford_lad_buffer_10mi.gpkg (edge-effect buffer extent)
│
├── docs/
│
├── examples/
│   ├── run_baseline.py       # baseline distance-only model (model_2)
│   ├── run_quality.py        # PaNS-calibrated baseline vs. quality-sensitive model
│   ├── run_oxford_north.py   # Oxford North scenario + triptych
│   └── run_quality_v12.py    # v1.2 quality model variant (src/model_v12)
│
├── figures/
├── notebooks/
│
└── src/
    ├── behaviour/
    │   └── distance_decay.py
    │
    ├── data/
    │   ├── load_origins.py
    │   └── load_destinations.py
    │
    ├── model/
    │   ├── spatial_interaction.py
    │   ├── quality_attractor.py
    │   ├── attractiveness.py
    │   └── distance.py        # shared Euclidean distance calc (bng_distance, build_distance_matrix)
    │
    ├── model_v12/             # in-development v1.2 model variant
    │   ├── spatial_interaction.py
    │   ├── quality_attractor.py
    │   └── attractiveness.py
    │
    ├── scenario/
    │   ├── add_origin.py
    │   └── run_scenario.py
    │
    └── visualisation/
        ├── baseline_maps.py
        ├── ranking_comparisons.py
        └── scenario_tryptych.py
```

This structure mirrors the conceptual workflow:

**Data → Behaviour → Model → Scenario → Visualisation → Examples**

Note: `run_quality.py`, `run_oxford_north.py`, and `run_quality_v12.py` currently
run against the archived v1.1-format destinations (via `paths_cfg.ARCHIVED_*`),
not `site_cat_access_union.csv` - the new file doesn't yet have QualityScore
or a clean one-row-per-site structure. `run_baseline.py` is the one script
already wired to the new data.

---

## 🌿 **Installation**

ViSAGE v1.2 requires:

- Python 3.10+
- geopandas
- pandas
- numpy
- matplotlib
- contextily
- scikit‑learn

Install dependencies:

```bash
pip install -r requirements.txt
```

*(If you want, I can generate this file for you.)*

---

## 🌼 **Data Inputs**

Active model inputs live directly in `data/` (see `paths_cfg.py` for the
canonical paths - don't hardcode paths in new scripts, import them from there):

| File | Description |
|------|-------------|
| `data/ox_synthetic_pop_origin.csv` | Synthetic population origins, wider extent (296 origins, ~40km domain) - part of the edge-effect buffer work |
| `data/site_cat_access_union.csv` | Access-point-level union of AGI/SSSI/SAC greenspace sites, one row per access point with `has_agi`/`has_sac`/`has_sssi` boolean flags (2,926 access points across 458 sites) |

Superseded v1.1-format files (Oxford-only extent, one row per site, includes
QualityScore) are kept in `data/_archive/` for reference - not part of the
active pipeline, but still needed by `run_quality.py`, `run_oxford_north.py`,
and `run_quality_v12.py` until quality scores exist against the new schema:

| File | Description |
|------|-------------|
| `synthetic_pop(in).csv` | v1.1-format origins |
| `site_catalogue(in).csv` | v1.1-format greenspace catalogue (centroids only) |
| `site_catalogue_with_quality.csv` | v1.1-format catalogue with QualityScore |
| `site_catalogue_polygons.csv` | Site boundary polygons |
| `site_catalogue_full.parquet` | v1.1-format catalogue, parquet |

Reference/validation data (not model inputs) lives in `data/external/`:
ORVal join (`join_orval.gpkg`), Overture POI join (`join_with_oxford.gpkg`),
and aggregated Strava visit timeseries. The 10-mile Oxford LAD buffer used to
define the expanded (edge-effect-reducing) study area lives in
`data/boundaries/oxford_lad_buffer_10mi.gpkg`.

---

## 🌳 **How to Run the Models**

### **1. Baseline Model (Distance‑Only)**  
Reproduces **Figure 3** in the NE report.

```bash
python examples/run_baseline.py
```

Outputs:

- baseline OD matrix  
- baseline site‑level visits  
- baseline proportional‑symbol map  

---

### **2. Quality‑Sensitive Model**  
Reproduces **Figure 5** (rank changes).

```bash
python examples/run_quality.py
```

Outputs:

- quality‑sensitive OD matrix  
- baseline vs quality visit comparison  
- ranking comparison table  
- top‑N rank‑change plot  

---

### **3. Oxford North Scenario Model**  
Reproduces **Figure 6** (triptych).

```bash
python examples/run_oxford_north.py
```

Outputs:

- extended origins (with Oxford North)  
- scenario OD matrix  
- site‑level impacts (Δ visits, % change)  
- OD flows from Oxford North  
- full triptych visualisation  

---

## 🌱 **Core Concepts**

### **Distance Decay (PaNS‑Calibrated)**  
Implemented in:

```
src/behaviour/distance_decay.py
```

Calibrated using PaNS M2AQ6 distance–probability pairs.

---

### **Spatial Interaction Model**  
Implemented in:

```
src/model/spatial_interaction.py
```

Baseline model:

\[
w_{ij} = e^{-\lambda d_{ij}}
\]

---

### **Quality Attractor**  
Implemented in:

```
src/model/quality_attractor.py
```

\[
A_j = (\text{QualityScore}_j)^\beta
\]

---

### **Scenario Engine**  
Implemented in:

```
src/scenario/add_origin.py
src/scenario/run_scenario.py
```

Allows new origins (e.g., Oxford North) to be added and evaluated.

---

### **Visualisation Modules**

- Baseline map → `baseline_maps.py`  
- Ranking comparison → `ranking_comparisons.py`  
- Scenario triptych → `scenario_tryptych.py`  

All produce publication‑grade figures.

---

## 🌿 **Reproducibility**

All outputs in the NE technical report can be reproduced by running:

```
python examples/run_baseline.py
python examples/run_quality.py
python examples/run_oxford_north.py
```

Figures will be saved to:

```
figures/
```

---

## 🌼 **Versioning**

**ViSAGE v1.2** (in development)
- Everything from v1.1 (baseline model, quality-sensitive model, Oxford
  North scenario engine, full visualisation suite)
- `paths_cfg.py` / `params_cfg.py` config split
- Wider-extent origins/destinations data (edge-effect buffer work, see
  `data/boundaries/`) - buffer extent defined, data not yet fully populated
  to match
- Access-point-level greenspace destinations (`data/site_site_cat_access_union.csv`)
  in progress - see `CHANGELOG.md` for current caveats
- Network-distance integration (OSRM) - planned, not yet wired in

---

## 🌳 **License**

This project is released under the MIT License.  
See `LICENSE` for details.

---

## 🌟 **Acknowledgements**

Developed in collaboration with colleagues and guidance from:

- **Natural England**   
- University of Exeter
- University of Glasgow


---



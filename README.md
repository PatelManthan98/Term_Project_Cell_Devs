# Asymmetric Cell-DEVS Wildfire Spread Model
**SYSC 5104/4906G — Term Project, Carleton University, April 2026**
**Author:** Manthan Patel

## Overview
An Asymmetric Cell-DEVS wildfire simulation using Cadmium v2. Each cell has a
unique terrain-derived neighbourhood where vicinity weights encode wind direction,
Rothermel slope, fuel-type adjacency, and firebreak blocking — pre-computed by
a QGIS data pipeline and stored in the scenario JSON topology.

## Prerequisites
- CMake 3.10+, GCC 13+ (C++17)
- Python 3 with: numpy, scipy, matplotlib, pandas, pillow

## Quick Start
```bash
# 1. Get Cadmium v2
git clone https://github.com/SimulationEverywhere/cadmium_v2.git cadmium_v2

# 2. Build
bash build_sim.sh

# 3. Generate all 5 scenarios (QGIS pipeline)
python3 generate_scenarios.py

# 4. Run all scenarios + visualize
bash run_all_scenarios.sh
```

## Run Individual Scenario
```bash
./build/wildfire_sim scenarios/scenario_calm.json 500 42
# Args: <scenario.json> <sim_time> [rng_seed]
# Output: grid_log.csv
```

## Visualize
```bash
LOG_FILE=results/grid_log_calm.csv SCENARIO=calm python3 visualize_wildfire.py
# Output: results/wildfire_calm.gif
```

## Scenarios
| File | Description | Wind | Notes |
|------|-------------|------|-------|
| scenario_calm.json | Uniform boreal forest | 0 km/h | Baseline radial spread |
| scenario_windy.json | Grass/shrub | 35 km/h E | Asymmetric east corridor |
| scenario_firebreak.json | Forest + river + road | 10 km/h | Topology-based containment |
| scenario_urban.json | Forest + urban | 15 km/h S | Road gap breach |
| scenario_fortmcmurray.json | Real terrain | 65 km/h SW | May 3 2016 reconstruction |

## Cell States
| Value | Meaning |
|-------|---------|
| 0 | Non-flammable (water/road) |
| 1 | Unburned |
| 2 | Burning |
| 3 | Ash |

## File Structure
```
include/wildfire_state.hpp   Cell state struct + JSON deserialiser
include/wildfire_cell.hpp    AsymmCell transition function
main.cpp                     AsymmCellDEVSCoupled driver
generate_scenarios.py        QGIS pipeline: terrain → asymmetric JSON
visualize_wildfire.py        Animated GIF visualiser
run_all_scenarios.sh         Build + run + visualise all scenarios
scenarios/                   Generated scenario JSON files
results/                     Output logs, GIFs, terrain maps
```

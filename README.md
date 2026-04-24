# Wildfire Spread Simulation — Asymmetric Cell-DEVS

**SYSC 5104 / 4906G Term Project — Carleton University**
**Author:** Manthan Patel

An Asymmetric Cell-DEVS wildfire spread model implemented in the Cadmium v2 simulator. Per-cell terrain-derived neighbourhood topologies encode Rothermel wind and slope physics, five-category NLCMS-2015 fuel classification, and a novel ember-spotting mechanism. Validated against the May 3, 2016 Fort McMurray Horse River fire.

---

## 1. Prerequisites

Install these on your machine **before** cloning.

| Tool | Minimum version | Purpose |
|------|-----------------|---------|
| git | 2.0+ | Cloning the repo and Cadmium v2 |
| C++ compiler | GCC 11+ or Clang 13+ (C++23 support) | Compiling the simulator |
| CMake | 3.16+ | Generate build files |
| make | any | Build the project |
| Python | 3.8+ | Scenario generation and visualization |
| ffmpeg | any (optional) | Convert GIFs to MP4 |

Python libraries needed:
```
numpy  pandas  matplotlib  scipy  Pillow  imageio
```

### 1.1 Install prerequisites on Ubuntu / Debian / WSL2

```bash
sudo apt update
sudo apt install -y build-essential cmake git python3 python3-pip ffmpeg
python3 -m pip install --upgrade pip
python3 -m pip install numpy pandas matplotlib scipy Pillow imageio
```

### 1.2 Install prerequisites on macOS (Homebrew)

```bash
brew install cmake git python ffmpeg
python3 -m pip install numpy pandas matplotlib scipy Pillow imageio
```

### 1.3 Windows users

Use **WSL2 (Ubuntu)** and follow §1.1. Native Windows + C++23 + Cadmium v2 is not supported.

### 1.4 Check versions

```bash
g++ --version       # must be 11 or higher
cmake --version     # must be 3.16 or higher
python3 --version   # must be 3.8 or higher
git --version
```

---

## 2. Clone the project

```bash
git clone https://github.com/PatelManthan98/Term_Project_Cell_Devs.git
cd Term_Project_Cell_Devs
```

### 2.1 Cadmium v2 dependency

The project's CMakeLists tries these locations in order:

1. The `$CADMIUM` environment variable (already set on the Carleton `devsim` server).
2. A local `cadmium_v2/include/` folder inside the project.

If you are **not** on the devsim server and the `cadmium_v2/` folder is missing, clone it once:

```bash
git clone https://github.com/SimulationEverywhere/cadmium_v2.git cadmium_v2
```

### 2.2 nlohmann/json dependency (fallback only)

Cadmium v2 already ships with nlohmann/json. If CMake complains it cannot find `nlohmann/json.hpp`, drop the single-header file into `libraries/nlohmann/`:

```bash
mkdir -p libraries/nlohmann
curl -L https://github.com/nlohmann/json/releases/download/v3.11.3/json.hpp \
     -o libraries/nlohmann/json.hpp
```

---

## 3. Build the simulator

### 3.1 Recommended: use the helper script

```bash
chmod +x build_sim.sh
./build_sim.sh
```

On success the last line reads:
```
Compilation done. Executable in the bin folder
```
and the binary is at `bin/wildfire_sim`.

### 3.2 Manual build (if the script fails)

```bash
rm -rf build
mkdir -p build
cd build
cmake ..
make
cd ..
```

The binary will be at `bin/wildfire_sim`.

### 3.3 Build troubleshooting

| Error message | Fix |
|---------------|-----|
| `fatal error: cadmium/...: No such file or directory` | `cadmium_v2/` is missing — see §2.1 |
| `fatal error: nlohmann/json.hpp: No such file or directory` | See §2.2 |
| `error: 'concept' was not declared in this scope` | Compiler too old — install GCC 11+ |
| `-std=gnu++2b: unrecognized` | Compiler too old — install GCC 11+ |
| `CMake 3.16 or higher is required` | Upgrade CMake |
| `Permission denied: ./build_sim.sh` | Run `chmod +x build_sim.sh` |

---

## 4. Generate scenario files

The seven scenario JSONs are already committed in `scenarios/`. To regenerate them yourself:

```bash
python3 generate_scenarios.py
```

This writes:
```
scenarios/scenario_calm.json
scenarios/scenario_windy.json
scenarios/scenario_firebreak.json
scenarios/scenario_firebreak_spot.json
scenarios/scenario_urban.json
scenarios/scenario_fortmcmurray_nospot.json
scenarios/scenario_fortmcmurray_spot.json
```

Typical runtime: about 25 seconds for all seven.

---

## 5. Run the simulations

### 5.1 Recommended: run everything at once

```bash
chmod +x run_all_scenarios.sh
./run_all_scenarios.sh
```

This single command:

1. runs `build_sim.sh` to make sure the binary is up to date,
2. runs `bin/wildfire_sim` on each of the seven scenarios with seed = 42 and sim_time = 500,
3. moves each `grid_log.csv` into `results/grid_log_<scenario>.csv`,
4. runs `visualize_wildfire.py` to produce GIFs (and MP4s if ffmpeg is installed).

Total wall time: **8–12 minutes** on a modern laptop.

### 5.2 Run a single scenario manually

```bash
./bin/wildfire_sim scenarios/scenario_calm.json 500 42
```

Arguments, in order:

```
1.  path to scenario JSON
2.  simulation end time       (500 is the standard choice)
3.  RNG seed                  (42 gives the reported results; omit for a random seed)
```

The run writes `grid_log.csv` to the current directory. Move it manually if you want to keep it:

```bash
mv grid_log.csv results/grid_log_calm.csv
```

### 5.3 Run all scenarios manually

```bash
mkdir -p results
for s in calm windy firebreak firebreak_spot urban fortmcmurray_nospot fortmcmurray_spot; do
    echo "=== $s ==="
    ./bin/wildfire_sim scenarios/scenario_${s}.json 500 42
    mv grid_log.csv results/grid_log_${s}.csv
done
```

---

## 6. Generate visualizations

```bash
python3 visualize_wildfire.py
```

This reads every `results/grid_log_*.csv` and writes:

```
results/wildfire_<scenario>.gif          (animated GIF for every scenario)
results/videos/wildfire_<scenario>.mp4   (if ffmpeg is installed)
```

---

## 7. Complete one-shot reproduction

On a fresh machine that already has the tools from §1.1 installed:

```bash
# 1. Clone
git clone https://github.com/PatelManthan98/Term_Project_Cell_Devs.git
cd Term_Project_Cell_Devs

# 2. Cadmium v2 (skip if you are on the devsim server)
git clone https://github.com/SimulationEverywhere/cadmium_v2.git cadmium_v2

# 3. Python libraries
python3 -m pip install numpy pandas matplotlib scipy Pillow imageio

# 4. Scenarios (optional — committed copies already exist)
python3 generate_scenarios.py

# 5. Build, run all seven scenarios, visualize — one command
chmod +x build_sim.sh run_all_scenarios.sh
./run_all_scenarios.sh
```

The Fort McMurray 2016 ember-crossing validation run is at `results/wildfire_fortmcmurray_spot.gif`.

---

## 8. Project layout

```
Term_Project_Cell_Devs/
├── CMakeLists.txt
├── build_sim.sh                # builds the simulator
├── run_all_scenarios.sh        # end-to-end: build → simulate 7 scenarios → visualize
├── main.cpp                    # Cadmium v2 driver
├── include/
│   ├── wildfire_state.hpp      # cell state struct + JSON deserializer
│   ├── wildfire_cell.hpp       # AsymmCell<WildfireCellState, double>
├── scenarios/                  # seven committed scenario JSONs
│   └── scenario_*.json
├── results/                    # generated by simulation + visualization
│   ├── grid_log_*.csv
│   ├── wildfire_*.gif
│   └── videos/wildfire_*.mp4
├── generate_scenarios.py       # terrain pipeline → asymmetric JSON
├── visualize_wildfire.py       # CSV logs → GIFs + MP4s
├── cadmium_v2/                 # submodule (cloned once — see §2.1)
├── libraries/                  # optional nlohmann/json fallback (§2.2)
├── build/                      # build output (auto-generated)
└── README.md                   # this file
```

---

## 9. Running on the Carleton devsim server

The `CADMIUM` environment variable is already set on the server:

```bash
echo $CADMIUM
# prints: /path/to/cadmium_v2/include
```

When set, the CMake configuration picks up the server's Cadmium automatically. Skip §2.1 entirely:

```bash
./build_sim.sh
./run_all_scenarios.sh
```

---

## 10. Cleaning up

```bash
# remove build artifacts
rm -rf build bin

# remove all simulation outputs
rm -rf results

# remove regenerated scenarios (if you want a clean regeneration)
rm scenarios/scenario_*.json
```

---

## 11. Expected results (seed = 42)

| # | Scenario | Burned | % Grid | Pattern |
|---|----------|-------:|------:|---------|
| 1 | Calm Forest | 2,447 | 97.9% | Radial symmetric |
| 2 | Windy Grassland | 2,323 | 92.9% | Eastward plume |
| 3 | Firebreaks | 1,124 | 45.0% | Contained west of river |
| 4 | Firebreaks + Spotting | 1,143 | 45.7% | No river crossing (threshold) |
| 5 | Urban Interface | 2,383 | 95.3% | WUI breach |
| 6 | Fort McMurray (no spot) | 807 | 32.3% | River contains fire |
| 7 | **Fort McMurray (spot)** | **1,791** | **71.6%** | **River crossed — 222 urban cells** |

If you see these numbers after running `./run_all_scenarios.sh`, the reproduction is successful.

---

## 12. License

Academic coursework submission — see the course handout for use and distribution terms.

# Asymmetric Cell-DEVS Wildfire Simulation

This project implements a physics-informed wildfire spread model using the **Asymmetric Cell-DEVS** formalism within the **Cadmium v2** discrete-event simulation library. The model accounts for heterogeneous terrain, wind forcing, and probabilistic ember spotting.

## 🚀 Key Features
- **Structural Asymmetry:** Wind and slope effects are structurally embedded into the topology via asymmetric vicinity weights.
- **Ember Spotting:** Uses sparse, long-range directed edges to simulate river-crossing behavior during extreme weather events.
- **Real-World Data:** Integrated with **NRCan CDEM** (Elevation) and **NLCMS-2015** (Land Cover) geospatial data.
- **Cadmium v2 Engine:** Leverages asynchronous discrete-event execution for high computational efficiency and scalability.

---

## 🛠 Prerequisites & Environment Setup

This project was developed and tested on the `devsim` server. To manage Python dependencies without administrative privileges, a virtual environment is used.

### 1. Python Environment

Create the virtual environment #
python3 -m venv .venv

# Activate the environment
source .venv/bin/activate

# Install required libraries for visualization
pip install numpy matplotlib pandas

2. C++ Requirements
Compiler: C++17 (GCC 9+)

Build Tool: CMake 3.10+

Library: Cadmium v2 (included in /libraries)

🏗 Build and Compilation
Follow these exact steps to compile the simulation. This process ensures the linker correctly identifies all dependencies.

Bash
# Prepare build directory
rm -rf build
mkdir build
cd build

# Configure and compile
cmake ..
make
Technical Note: If you encounter an "undefined reference to main" error during the make process, ensure that main.cpp does not contain #pragma once at the very top of the file.

🏃 Running the Simulation
Execute the simulation from the project root directory. The executable requires a scenario configuration, total time steps, and a random seed.

Bash
# Usage: ./build/wildfire_sim <scenario_file> <time_steps> <seed>
./build/wildfire_sim scenario.json 500 42
scenario.json: Input file containing fuel parameters, grid setup, and weather conditions.

500: Total simulation time steps.

42: Random seed (ensures results are reproducible for scientific validation).

📊 Visualization & Analysis
Once the simulation completes, a grid_log.csv file is generated in the build directory. To generate an animated GIF and statistical plots:

Bash
# Ensure the virtual environment is active
source .venv/bin/activate

# Run the visualization script
python3 visualize_wildfire.py
The script will produce wildfire_spread.gif and statistical charts (PNG) showing the rate of spread and active burning cells.

🧪 Validated Scenarios
The model has been tested against several critical wildfire behaviors:

Scenario 1 (Calm): Isotropic spread under no-wind conditions.

Scenario 3 (Firebreak): Total containment by a wide river barrier (No spotting).

Scenario 4 (Moderate Wind): Spotting is active but insufficient for a sustained breach.

Scenario 7 (Fort McMurray): Successful reconstruction of the 2016 breach under 65 km/h wind with high-intensity urban ignition.

✍️ Author
Manthan Patel Department of Systems and Computer Engineering, Carleton University

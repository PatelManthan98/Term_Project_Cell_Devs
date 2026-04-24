# Asymmetric Cell-DEVS Wildfire Simulation

This project implements a physics-informed wildfire spread model using the **Asymmetric Cell-DEVS** formalism within the **Cadmium v2** discrete-event simulation library. The model accounts for heterogeneous terrain, wind forcing, and probabilistic ember spotting.

## 🚀 Key Features
- **Structural Asymmetry:** Wind and slope effects are structurally embedded into the topology via asymmetric vicinity weights.
- **Ember Spotting:** Uses sparse, long-range directed edges to simulate river-crossing behavior during extreme weather events.
- **Real-World Data:** Integrated with **NRCan CDEM** (Elevation) and **NLCMS-2015** (Land Cover) geospatial data.
- **Cadmium v2 Engine:** Leverages asynchronous discrete-event execution for high computational efficiency.

---

## 🛠 Prerequisites & Environment Setup

This project was developed and tested on the `devsim` server. Follow these steps to prepare the environment and install dependencies without root access.

###1. Ensure Cadmium v2 is available at $CADMIUM or clone locally
```
git clone https://github.com/SimulationEverywhere/cadmium_v2.git cadmium_v2
```
### 2. Python Environment Setup
```bash
# Create the virtual environment
python3 -m venv .venv

# Activate the environment
source .venv/bin/activate

# Upgrade pip and install required libraries
pip install --upgrade pip
pip install numpy matplotlib pandas
````
###🏗 Build and Compilation
Use the following commands to compile the simulation engine. This process handles the linking of the Cadmium headers.
# Navigate to project root, then create and enter build directory
```
source build.sh
```
## 🏃 Running the Simulation
1. Scenario Generation
Before running the model, generate the specific scenario JSON files using the provided Python script:
```
# Ensure venv is active
source .venv/bin/activate
python3 generate_scenarios.py
```
2. Execution
   Run the simulation from the project root. The executable requires the scenario file, total time steps, and a random seed.
   # Usage to run scenarios individuall: ./build/wildfire_sim <scenario_file> <time_steps> <seed>
```
./build/wildfire_sim scenarios/scenario_fortmcmurray.json 500 42
```
## To run all the scenarios at Once
```
source run_all_scenario.sh
 ```
###📊 Visualization & Analysis
After the simulation finishes, a grid_log.csv file is created. Use the Python script to generate the animated GIF and statistical plots.  
```
python3 visualize_wildfire.py
```
🧪 Validated Scenarios
The model demonstrates critical wildfire behaviors through these four primary scenarios:

Scenario 1 (Calm): Baseline isotropic spread under no-wind conditions, confirming the core model logic.

Scenario 3 (Firebreak): Structural containment by a wide river barrier (spotting disabled), verifying topology integrity.

Scenario 4 (Moderate Wind): Spotting is active at 25 km/h, but ignitions remain isolated, demonstrating the wind-speed threshold required for a breach.

Scenario 7 (Fort McMurray): Reconstruction of the 2016 breach under 65 km/h wind. The fire bypasses the Athabasca River via long-range spotting and escalates into urban fuels.

✍️ Author
Manthan Patel Department of Systems and Computer Engineering, Carleton University

**Asymmetric Cell-DEVS Wildfire Spread Simulation**

**📖 Project Overview**
This project implements an advanced wildfire spread model using the Asymmetric Cell-DEVS formalism. Unlike traditional symmetric grid models (Cellular Automata), this simulator utilizes a unique neighborhood for every cell.
Each neighbor link is assigned a pre-computed directional weight that encodes:

Wind Vectors: Influencing spread based on May 2016 Fort McMurray weather data.

Slope Gradients: Derived from Digital Elevation Models (DEM).

Fuel Adjacency: Accounting for firebreaks (rivers, roads) and fuel types.

**🚀 Key Features**
Asymmetric Topology: Moves beyond the Moore neighborhood to a weighted graph-based spatial model.
Fort McMurray 2016 Case Study: Validated against the "Horse River" wildfire using historical weather: 65 km/h SW winds, 32°C, and 13% humidity.
GIS-Inspired Pipeline: A Python-based scenario generator that mimics a QGIS data pipeline to create asymmetric JSON configurations.
Event-Driven Efficiency: Built on the Cadmium v2 framework for high-performance discrete-event execution.

**🛠️ Installation & Build**
1. Prerequisites
C++ Compiler: GCC 13+ (supporting C++20)
Build System: CMake 3.10+
Framework: Cadmium v2 (Included as a submodule/cloned directory)

2. Setup Dependencies
From the project root, ensure the Cadmium library is present:
git clone https://github.com/SimulationEverywhere/cadmium_v2.git cadmium_v2

4. Compilation
Run the provided build script:
chmod +x build_sim.sh
./build_sim.sh
**
🏃 Running the Simulation**
1. Scenario Generation
   
Generate the asymmetric neighborhood files (mimicking the QGIS export process described in the project requirements):
python3 generate_scenarios.py
This creates five distinct scenarios in the scenarios/ folder: calm, windy, firebreak, urban, and fortmcmurray

3. Execute All Models
Run the automated batch script to simulate all scenarios and extract logs:

Bash
chmod +x run_all_scenarios.sh
./run_all_scenarios.sh

**📊 Results and Visualization**
The simulation generates CSV logs in the results/ directory. You can visualize the spread using the following states:

🟩 Green: Unburned Fuel

🟥 Red: Actively Burning

⬛ Black: Burned Out (Ash)

**📂 Deliverables Structure**
include/: Contains wildfire_cell.hpp (Asymmetric Cell definition) and wildfire_state.hpp.

main.cpp: The AsymmCellDEVSCoupled model entry point.

generate_scenarios.py: The GIS-emulation pipeline for asymmetric weights.

Wildfire_CellDEVS_Report.pdf: The 15-20 page IEEE-formatted Term Paper.

⬜ Grey: Non-combustible (Rivers/Roads)

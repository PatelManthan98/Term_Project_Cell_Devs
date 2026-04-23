====================================================================
        🔥 ASYMMETRIC CELL-DEVS WILDFIRE SIMULATION 🔥
====================================================================

A physics-informed wildfire spread model built using the
Asymmetric Cell-DEVS formalism and executed on the
Cadmium v2 discrete-event simulation engine.

This model integrates:
• Heterogeneous terrain
• Wind forcing
• Fuel structure
• Probabilistic ember spotting

→ Designed to reproduce realistic wildfire behavior.

--------------------------------------------------------------------
🚀 KEY FEATURES
--------------------------------------------------------------------

◆ Asymmetric Topology
  Wind and slope effects embedded directly into directional weights.

◆ Ember Spotting
  Sparse long-range ignition (e.g., river crossing, extreme winds).

◆ Real Geospatial Data
  • NRCan CDEM  → elevation & slope
  • NLCMS-2015  → land cover & fuel classification

◆ High-Performance Execution
  Built on Cadmium v2 for asynchronous, event-driven simulation.

--------------------------------------------------------------------
⚙️ PREREQUISITES & SETUP
--------------------------------------------------------------------

Developed on: devsim server  
Uses: Python virtual environment

1) Create environment
   python3 -m venv .venv

2) Activate environment
   source .venv/bin/activate

3) Install dependencies
   pip install numpy matplotlib pandas

--------------------------------------------------------------------
🏃 RUNNING THE SIMULATION
--------------------------------------------------------------------

From the project root:

   ./build/wildfire_sim <scenario_file> <time_steps> <seed>

Example:
   ./build/wildfire_sim scenario.json 500 42

Parameters:
   scenario.json  → configuration (grid, fuel, weather, topology)
   500            → number of simulation steps
   42             → random seed (reproducibility)

--------------------------------------------------------------------
📊 VISUALIZATION & OUTPUTS
--------------------------------------------------------------------

After running, a file is generated:
   /build/grid_log.csv

To visualize:

   source .venv/bin/activate
   python3 visualize_wildfire.py

Outputs:
   • wildfire_spread.gif   → animated fire progression
   • PNG charts:
       - rate of spread
       - active burning cells
       - cumulative burn area

--------------------------------------------------------------------
🧪 VALIDATED SCENARIOS
--------------------------------------------------------------------

[1] Calm
    → Isotropic spread (no wind)

[3] Firebreak
    → River fully contains fire (no spotting)

[4] Moderate Wind
    → Spotting occurs but fails to breach barrier

[7] Fort McMurray (2016)
    → Reproduces Horse River wildfire breach
      under ~65 km/h winds

--------------------------------------------------------------------
✍️ AUTHOR
--------------------------------------------------------------------

Manthan Patel
Department of Systems and Computer Engineering
Carleton University

====================================================================

**🔥 ASYMMETRIC CELL-DEVS WILDFIRE SIMULATION 🔥 **


A physics-informed wildfire spread model built using the
Asymmetric Cell-DEVS formalism and executed on the
Cadmium v2 discrete-event simulation engine.

The model integrates heterogeneous terrain, wind forcing,
fuel structure, and probabilistic ember spotting to
reproduce realistic wildfire behavior.


----------------------------------------------------------------------
🔥 KEY FEATURES
----------------------------------------------------------------------

[ Asymmetric Topology ]
  Wind and slope effects embedded into directional weights.

[ Ember Spotting ]
  Long-range ignition (river crossing, extreme wind events).

[ Real Geospatial Data ]
  - NRCan CDEM      → elevation & slope
  - NLCMS-2015      → land cover & fuel classification

[ High-Performance Execution ]
  Built on Cadmium v2 (event-driven, asynchronous).


----------------------------------------------------------------------
⚙️ SETUP & ENVIRONMENT
----------------------------------------------------------------------

Developed on: devsim server

Create environment:
  python3 -m venv .venv

Activate:
  source .venv/bin/activate

Install dependencies:
  pip install numpy matplotlib pandas


----------------------------------------------------------------------
🏃 RUN SIMULATION
----------------------------------------------------------------------

Command:
  ./build/wildfire_sim <scenario_file> <time_steps> <seed>

Example:
  ./build/wildfire_sim scenario.json 500 42

Parameters:
  scenario.json  → configuration file
  500            → simulation steps
  42             → random seed


----------------------------------------------------------------------
📊 VISUALIZATION
----------------------------------------------------------------------

Generated file:
  /build/grid_log.csv

Run:
  source .venv/bin/activate
  python3 visualize_wildfire.py

Outputs:
  - wildfire_spread.gif
  - rate of spread (PNG)
  - active burning cells (PNG)
  - cumulative burn area (PNG)


----------------------------------------------------------------------
🧪 VALIDATED SCENARIOS
----------------------------------------------------------------------

[1] Calm
    Isotropic spread (no wind)

[3] Firebreak
    Full containment (no spotting)

[4] Moderate Wind
    Spotting occurs but fails to breach

[7] Fort McMurray (2016)
    Reproduces Horse River wildfire breach (~65 km/h wind)


----------------------------------------------------------------------
✍️ AUTHOR
----------------------------------------------------------------------

Manthan Patel
School of Information Technology


======================================================================

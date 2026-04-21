"""
qgis_pipeline.py
================
Standalone QGIS-style data pipeline for the Wildfire Cell-DEVS model.

This script replicates what the QGIS plugin does, but runs from the
command line without needing QGIS installed. It reads real NRCan raster
files (.tif) if available, or uses the synthetic Fort McMurray terrain.

Usage with real data:
    python3 qgis_pipeline.py \\
        --dem     /path/to/nrcan_cdem.tif \\
        --lc      /path/to/nlcms_2015.tif \\
        --output  scenarios/scenario_qgis_real.json \\
        --cell-m  20 \\
        --wind-speed 65 --wind-dir 45 \\
        --temp 32 --humidity 13 --ffmc 97

Usage without real data (synthetic Fort McMurray):
    python3 qgis_pipeline.py --synthetic

How to get real NRCan data:
    1. Go to https://maps.canada.ca/czs/index-en.html
    2. Search "Fort McMurray"
    3. Download CDEM (elevation) and NLCMS-2015 (land cover) for the area
    4. Save as .tif files and pass to this script

NLCMS-2015 → BehavePlus fuel mapping (Murphy 2025, Figure 6):
    1  Temperate needleleaf  → FM10 Forest      (fuel_type=3)
    2  Sub-polar needleleaf  → FM10 Forest      (fuel_type=3)
    3  Sub-polar taiga       → FM13 Taiga       (fuel_type=4)
    4  Broadleaf deciduous   → FM9  Deciduous   (fuel_type=5)
    5  Mixed forest          → FM10 Forest      (fuel_type=3)
    6  Temperate shrubland   → SH1  Shrub       (fuel_type=2)
    8  Temperate grassland   → GR1  Grass       (fuel_type=1)
    11 Wetland               → NB4  Wetland     (fuel_type=7)
    14 Urban                 → NB1  Urban/WUI   (fuel_type=6)
    15 Water                 → NB8  Water       (fuel_type=0)
"""

import argparse, json, math, os, sys
import numpy as np
from pathlib import Path
from scipy.ndimage import gaussian_filter, zoom

# ── Fuel type constants ───────────────────────────────────────────────────────
NLCMS_TO_FUEL = {
    1:3, 2:3, 3:4, 4:5, 5:3,
    6:2, 7:2, 8:1, 9:1, 10:1,
    11:7, 12:0, 13:0, 14:6, 15:0, 16:0
}
FUEL_BURNABLE  = {0:False,1:True,2:True,3:True,4:True,5:True,6:True,7:False}
FUEL_MOISTURE  = {0:1.0,1:0.10,2:0.25,3:0.18,4:0.20,5:0.22,6:0.12,7:0.80}
FUEL_LABEL     = {0:"Water/NB",1:"Grass(GR1)",2:"Shrub(SH1)",3:"Forest(FM10)",
                  4:"Taiga(FM13)",5:"Deciduous(FM9)",6:"Urban(WUI)",7:"Wetland(NB4)"}

def cid(r, c): return f"r{r}_c{c}"

def wind_factor(dr, dc, spd, wdir):
    if spd == 0: return 1.0
    ang  = math.atan2(-dr, dc) * 180 / math.pi
    diff = abs(ang - wdir)
    if diff > 180: diff = 360 - diff
    return max(0.2, 1.0 + (spd/30.0) * math.cos(math.radians(diff)))

def slope_factor(my_e, nbr_e, cell_m):
    diff = my_e - nbr_e
    ts   = abs(diff) / cell_m
    return (1.0 + 5.275*ts*ts) if diff <= 0 else max(0.4, 1.0-1.5*ts)

def build_from_arrays(fuel_grid, elev_grid,
                      wind_speed, wind_dir, temperature, humidity, ffmc,
                      ignition_prob, ignition_rc,
                      cell_size_m, spot_range, spot_base, output_path):
    R, C   = fuel_grid.shape
    MOORE  = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
    cells  = {}

    print(f"  Building {R}×{C} = {R*C} cells ...")

    for r in range(R):
        for c in range(C):
            ft  = int(fuel_grid[r, c])
            elv = round(float(elev_grid[r, c]), 1)
            mst = round(FUEL_MOISTURE.get(ft, 0.18), 3)
            nbhd = {}

            if FUEL_BURNABLE.get(ft, False):
                for dr, dc in MOORE:
                    nr, nc = r+dr, c+dc
                    if not (0<=nr<R and 0<=nc<C): continue
                    nft = int(fuel_grid[nr, nc])
                    if not FUEL_BURNABLE.get(nft, False): continue
                    wf  = wind_factor(dr, dc, wind_speed, wind_dir)
                    sf  = slope_factor(elv, float(elev_grid[nr,nc]), cell_size_m)
                    d   = 1.0 if (dr==0 or dc==0) else 0.707
                    vic = round(wf * sf * d, 4)
                    if vic > 0.05: nbhd[cid(nr,nc)] = vic

                if spot_range > 0:
                    for dist in range(2, spot_range+1):
                        for dr, dc in MOORE:
                            nr, nc = r+dr*dist, c+dc*dist
                            if not (0<=nr<R and 0<=nc<C): continue
                            nft = int(fuel_grid[nr, nc])
                            if not FUEL_BURNABLE.get(nft, False): continue
                            wf = wind_factor(dr, dc, wind_speed, wind_dir)
                            if wf < 1.1: continue
                            actual_d = math.sqrt((dr*dist)**2+(dc*dist)**2)
                            vic = round(spot_base * wf / (actual_d**1.5), 5)
                            if vic < 0.003: continue
                            k = cid(nr, nc)
                            nbhd[k] = max(nbhd.get(k,0), vic)

            cells[cid(r,c)] = {
                "delay": "inertial",
                "state": {"state":1,"fuel_type":ft,"elevation":elv,
                          "moisture":mst,"intensity":0.0,"burn_steps_remaining":0},
                "config": {"ignition_prob":ignition_prob,"temperature":temperature,
                           "humidity":humidity,"ffmc":ffmc},
                "neighborhood": nbhd
            }

    # Set ignition
    for r0, c0 in ignition_rc:
        k = cid(r0, c0)
        if k in cells and FUEL_BURNABLE.get(cells[k]["state"]["fuel_type"], False):
            cells[k]["state"].update({"state":2,"intensity":0.9,"burn_steps_remaining":10})
            print(f"  Ignition: {k} (fuel={FUEL_LABEL[cells[k]['state']['fuel_type']]})")

    with open(output_path, "w") as f:
        json.dump({"cells": cells}, f, separators=(',',':'))
    print(f"  Written: {output_path}  ({os.path.getsize(output_path)//1024}KB)")

def load_real_rasters(dem_path, lc_path, target_rows=50, target_cols=50):
    """Load real NRCan .tif files using rasterio."""
    try:
        import rasterio
        from scipy.ndimage import zoom as scipy_zoom
    except ImportError:
        print("ERROR: rasterio required for real data. pip install rasterio")
        sys.exit(1)

    print(f"  Reading elevation: {dem_path}")
    with rasterio.open(dem_path) as src:
        elev_raw = src.read(1).astype(float)
        elev_raw[elev_raw < -1000] = 300.0  # fill nodata

    print(f"  Reading land cover: {lc_path}")
    with rasterio.open(lc_path) as src:
        lc_raw = src.read(1).astype(int)

    # Resample to target grid
    s_r = target_rows / elev_raw.shape[0]
    s_c = target_cols / elev_raw.shape[1]
    elev = scipy_zoom(elev_raw, (s_r, s_c), order=1)
    elev = gaussian_filter(elev, sigma=1.5)

    s_r2 = target_rows / lc_raw.shape[0]
    s_c2 = target_cols / lc_raw.shape[1]
    lc   = scipy_zoom(lc_raw, (s_r2, s_c2), order=0).astype(int)

    fuel = np.vectorize(lambda x: NLCMS_TO_FUEL.get(x, 3))(lc).astype(int)
    print(f"  Grid: {target_rows}×{target_cols}, elev range: {elev.min():.0f}–{elev.max():.0f}m")
    print("  Fuel distribution:")
    for ft, label in FUEL_LABEL.items():
        count = int((fuel == ft).sum())
        if count > 0:
            print(f"    {label}: {count} cells ({count/(target_rows*target_cols)*100:.1f}%)")
    return fuel, elev

def synthetic_fortmcmurray(G=50):
    """Analytical reproduction of Fort McMurray terrain (NRCan CDEM + NLCMS-2015)."""
    print("  Using validated synthetic terrain (NRCan CDEM documented values)")
    elev = np.zeros((G,G))
    for r in range(G):
        for c in range(G):
            base   = 278 + (G-c)*4.5
            rc     = 8 + r*0.55
            valley = max(0, 50 - abs(c-rc)*7)
            beacon = max(0, 35 - math.sqrt((r-20)**2+(c-15)**2)*3)
            elev[r,c] = base - valley + beacon
    elev = gaussian_filter(elev, 2.5)
    elev = np.clip(elev, 240, 700)

    from generate_scenarios import WATER, GRASS, SHRUB, FOREST, URBAN, WETLAND
    fuel = np.full((G,G), FOREST, dtype=int)
    for r in range(G):
        cc = int(8+r*0.55)
        for dc in range(-2,3):
            nc = cc+dc
            if 0<=nc<G:
                if abs(dc)<=1: fuel[r,nc]=WATER
    fuel[24:27,25:]=WATER
    fuel[12:25,28:46]=URBAN; fuel[8:13,25:35]=URBAN
    fuel[20:35,5:20]=GRASS
    fuel[35:,30:]=WETLAND
    fuel[0:15,0:12]=SHRUB
    return fuel, elev

# ── CLI ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="QGIS-style Cell-DEVS pipeline")
    parser.add_argument("--dem",         help="NRCan CDEM elevation .tif")
    parser.add_argument("--lc",          help="NLCMS-2015 land cover .tif")
    parser.add_argument("--synthetic",   action="store_true", help="Use synthetic Fort McMurray terrain")
    parser.add_argument("--output",      default="scenarios/scenario_qgis.json")
    parser.add_argument("--cell-m",      type=int,   default=100)
    parser.add_argument("--grid-size",   type=int,   default=50)
    parser.add_argument("--wind-speed",  type=float, default=65.0)
    parser.add_argument("--wind-dir",    type=float, default=45.0)
    parser.add_argument("--temp",        type=float, default=32.0)
    parser.add_argument("--humidity",    type=float, default=13.0)
    parser.add_argument("--ffmc",        type=float, default=97.0)
    parser.add_argument("--ignition-prob", type=float, default=0.25)
    parser.add_argument("--spot-range",  type=int,   default=0)
    parser.add_argument("--spot-base",   type=float, default=0.08)
    args = parser.parse_args()

    os.makedirs("scenarios", exist_ok=True)
    print("=== QGIS Cell-DEVS Pipeline ===")

    if args.dem and args.lc:
        print("Loading real NRCan raster data...")
        fuel, elev = load_real_rasters(args.dem, args.lc, args.grid_size, args.grid_size)
        ign = [(args.grid_size//2, args.grid_size//2)]
    elif args.synthetic:
        print("Using synthetic Fort McMurray terrain...")
        fuel, elev = synthetic_fortmcmurray(args.grid_size)
        ign = [(20, 15)]
    else:
        print("No data source specified. Use --dem + --lc for real data or --synthetic")
        parser.print_help()
        sys.exit(1)

    build_from_arrays(
        fuel, elev,
        args.wind_speed, args.wind_dir, args.temp, args.humidity, args.ffmc,
        args.ignition_prob, ign,
        args.cell_m, args.spot_range, args.spot_base, args.output
    )
    print(f"\nDone! Run: ./build/wildfire_sim {args.output} 500 42")
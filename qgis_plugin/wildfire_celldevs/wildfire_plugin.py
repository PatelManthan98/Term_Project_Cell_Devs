"""
wildfire_plugin.py
==================
QGIS Plugin: Asymmetric Cell-DEVS Wildfire Scenario Generator
SYSC 5104 Term Project — Carleton University

Workflow:
  1. User loads NRCan CDEM elevation .tif and NLCMS-2015 land cover .tif
  2. User draws a simulation polygon (study area)
  3. User draws an ignition polygon (fire start)
  4. Plugin samples both rasters at grid resolution
  5. Computes asymmetric neighbourhood with wind + slope vicinity weights
  6. Outputs Cadmium-compatible JSON scenario file

References:
  Murphy (2025) — Asynchronous Cell-DEVS Wildfire Spread Using GIS Data
  Cardenas & Wainer (2022) — Asymmetric Cell-DEVS Models with Cadmium
  NRCan CDEM / NLCMS-2015
"""

import os
import math
import json

from qgis.PyQt.QtWidgets import (
    QAction, QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox,
    QDoubleSpinBox, QSpinBox, QCheckBox,
    QFileDialog, QGroupBox, QMessageBox, QProgressBar
)
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import Qt

from qgis.core import (
    QgsProject, QgsRasterLayer, QgsVectorLayer,
    QgsPointXY, QgsGeometry, QgsFeature,
    QgsSpatialIndex, QgsCoordinateReferenceSystem,
    QgsCoordinateTransform, QgsRectangle
)

import numpy as np

# ── NLCMS-2015 → fuel type mapping (Murphy 2025 Figure 6) ───────────────────
NLCMS_TO_FUEL = {
    1: 3,   # Temperate needleleaf forest → FM10 Forest
    2: 3,   # Sub-polar needleleaf → FM10 Forest
    3: 4,   # Sub-polar taiga → FM13
    4: 5,   # Temperate broadleaf → FM9
    5: 3,   # Mixed forest → FM10
    6: 2,   # Temperate shrubland → SH1
    7: 2,   # Sub-polar shrubland → SH1
    8: 1,   # Temperate grassland → GR1
    9: 1,   # Sub-polar grassland → GR1
    10: 1,  # Polar grassland → GR1
    11: 7,  # Wetland → NB4 non-burnable
    12: 0,  # Cropland → non-burnable
    13: 0,  # Barren → non-burnable
    14: 0,  # Urban → NB1 (set separately)
    15: 0,  # Water → NB8
    16: 0,  # Snow/Ice → non-burnable
}

FUEL_LABEL = {
    0: "Non-burnable", 1: "Grass(GR1)", 2: "Shrub(SH1)",
    3: "Forest(FM10)", 4: "Taiga(FM13)", 5: "Deciduous(FM9)",
    6: "Urban(WUI)", 7: "Wetland(NB4)"
}

FUEL_MOISTURE = {0:1.0, 1:0.10, 2:0.25, 3:0.18, 4:0.20, 5:0.22, 6:0.12, 7:0.80}
FUEL_BURNABLE = {0:False,1:True,2:True,3:True,4:True,5:True,6:True,7:False}


class WildfireDialog(QDialog):
    def __init__(self, iface, parent=None):
        super().__init__(parent)
        self.iface = iface
        self.setWindowTitle("Wildfire Cell-DEVS Scenario Generator")
        self.setMinimumWidth(480)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()

        # ── Raster inputs ────────────────────────────────────────────────────
        raster_group = QGroupBox("NRCan Raster Layers")
        rg = QVBoxLayout()

        # Elevation
        elev_row = QHBoxLayout()
        elev_row.addWidget(QLabel("Elevation (CDEM .tif):"))
        self.elev_path = QLineEdit(); self.elev_path.setPlaceholderText("Path to DEM .tif")
        elev_row.addWidget(self.elev_path)
        elev_btn = QPushButton("Browse")
        elev_btn.clicked.connect(lambda: self._browse(self.elev_path, "DEM (*.tif *.tiff)"))
        elev_row.addWidget(elev_btn)
        rg.addLayout(elev_row)

        # Land cover
        lc_row = QHBoxLayout()
        lc_row.addWidget(QLabel("Land Cover (NLCMS .tif):"))
        self.lc_path = QLineEdit(); self.lc_path.setPlaceholderText("Path to NLCMS-2015 .tif")
        lc_row.addWidget(self.lc_path)
        lc_btn = QPushButton("Browse")
        lc_btn.clicked.connect(lambda: self._browse(self.lc_path, "Land Cover (*.tif *.tiff)"))
        lc_row.addWidget(lc_btn)
        rg.addLayout(lc_row)
        raster_group.setLayout(rg)
        layout.addWidget(raster_group)

        # ── Polygon layers ────────────────────────────────────────────────────
        poly_group = QGroupBox("Simulation Polygons")
        pg = QVBoxLayout()
        pg.addWidget(QLabel("Draw polygons in QGIS then select layers:"))

        sim_row = QHBoxLayout()
        sim_row.addWidget(QLabel("Simulation area:"))
        self.sim_layer = QComboBox()
        self._populate_vector_layers(self.sim_layer)
        sim_row.addWidget(self.sim_layer)
        pg.addLayout(sim_row)

        ign_row = QHBoxLayout()
        ign_row.addWidget(QLabel("Ignition area:"))
        self.ign_layer = QComboBox()
        self._populate_vector_layers(self.ign_layer)
        ign_row.addWidget(self.ign_layer)
        pg.addLayout(ign_row)
        poly_group.setLayout(pg)
        layout.addWidget(poly_group)

        # ── Simulation parameters ─────────────────────────────────────────────
        param_group = QGroupBox("Simulation Parameters")
        pg2 = QVBoxLayout()

        # Resolution
        res_row = QHBoxLayout()
        res_row.addWidget(QLabel("Cell size (m):"))
        self.cell_size = QSpinBox(); self.cell_size.setRange(10, 5000)
        self.cell_size.setValue(20); self.cell_size.setSuffix(" m")
        res_row.addWidget(self.cell_size)
        pg2.addLayout(res_row)

        # Wind
        wind_row = QHBoxLayout()
        wind_row.addWidget(QLabel("Wind speed (km/h):"))
        self.wind_speed = QDoubleSpinBox(); self.wind_speed.setRange(0, 150)
        self.wind_speed.setValue(0); self.wind_speed.setSuffix(" km/h")
        wind_row.addWidget(self.wind_speed)
        wind_row.addWidget(QLabel("Wind direction (°):"))
        self.wind_dir = QDoubleSpinBox(); self.wind_dir.setRange(0, 360)
        self.wind_dir.setValue(0); self.wind_dir.setSuffix("°")
        wind_row.addWidget(self.wind_dir)
        pg2.addLayout(wind_row)

        # Weather
        wx_row = QHBoxLayout()
        wx_row.addWidget(QLabel("Temperature (°C):"))
        self.temp = QDoubleSpinBox(); self.temp.setRange(-30, 50)
        self.temp.setValue(22)
        wx_row.addWidget(self.temp)
        wx_row.addWidget(QLabel("Humidity (%):"))
        self.humidity = QDoubleSpinBox(); self.humidity.setRange(0, 100)
        self.humidity.setValue(40); self.humidity.setSuffix("%")
        wx_row.addWidget(self.humidity)
        wx_row.addWidget(QLabel("FFMC:"))
        self.ffmc = QDoubleSpinBox(); self.ffmc.setRange(0, 101)
        self.ffmc.setValue(85)
        wx_row.addWidget(self.ffmc)
        pg2.addLayout(wx_row)

        # Ignition prob
        ign_row2 = QHBoxLayout()
        ign_row2.addWidget(QLabel("Base ignition prob:"))
        self.ign_prob = QDoubleSpinBox(); self.ign_prob.setRange(0.01, 1.0)
        self.ign_prob.setValue(0.25); self.ign_prob.setSingleStep(0.01)
        ign_row2.addWidget(self.ign_prob)
        pg2.addLayout(ign_row2)

        # Spotting
        spot_row = QHBoxLayout()
        self.spotting_cb = QCheckBox("Enable spotting (ember transport)")
        self.spotting_cb.setChecked(False)
        spot_row.addWidget(self.spotting_cb)
        spot_row.addWidget(QLabel("Range (cells):"))
        self.spot_range = QSpinBox(); self.spot_range.setRange(2, 20)
        self.spot_range.setValue(5)
        spot_row.addWidget(self.spot_range)
        pg2.addLayout(spot_row)

        param_group.setLayout(pg2)
        layout.addWidget(param_group)

        # ── Output ────────────────────────────────────────────────────────────
        out_group = QGroupBox("Output")
        og = QHBoxLayout()
        og.addWidget(QLabel("Output JSON:"))
        self.out_path = QLineEdit(); self.out_path.setText("scenario_qgis.json")
        og.addWidget(self.out_path)
        out_btn = QPushButton("Browse")
        out_btn.clicked.connect(lambda: self._browse_save(self.out_path))
        og.addWidget(out_btn)
        out_group.setLayout(og)
        layout.addWidget(out_group)

        # Progress
        self.progress = QProgressBar(); self.progress.setValue(0)
        layout.addWidget(self.progress)

        # Buttons
        btn_row = QHBoxLayout()
        run_btn = QPushButton("Generate Scenario")
        run_btn.setStyleSheet("background-color: #2E5496; color: white; font-weight: bold; padding: 6px;")
        run_btn.clicked.connect(self._run)
        btn_row.addWidget(run_btn)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

        self.setLayout(layout)

    def _browse(self, field, filt):
        path, _ = QFileDialog.getOpenFileName(self, "Select file", "", filt)
        if path: field.setText(path)

    def _browse_save(self, field):
        path, _ = QFileDialog.getSaveFileName(self, "Save JSON", "", "JSON (*.json)")
        if path: field.setText(path)

    def _populate_vector_layers(self, combo):
        combo.addItem("-- select layer --", None)
        for name, layer in QgsProject.instance().mapLayers().items():
            if isinstance(layer, QgsVectorLayer):
                combo.addItem(layer.name(), layer.id())

    def _run(self):
        """Main generation pipeline."""
        try:
            self._generate_scenario()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _generate_scenario(self):
        """
        Core QGIS pipeline:
        1. Read DEM and land cover rasters at user-specified resolution
        2. Clip to simulation polygon
        3. Map NLCMS classes to fuel types
        4. Compute asymmetric neighbourhood with wind/slope vicinity weights
        5. Mark ignition cells
        6. Write Cadmium JSON
        """
        import rasterio
        from rasterio.mask import mask as rasterio_mask
        from rasterio.warp import reproject, Resampling
        from shapely.geometry import shape, mapping
        import numpy as np

        # ── Get parameters ────────────────────────────────────────────────────
        cell_m    = self.cell_size.value()
        wind_spd  = self.wind_speed.value()
        wind_dir  = self.wind_dir.value()
        temp      = self.temp.value()
        hum       = self.humidity.value()
        ffmc_val  = self.ffmc.value()
        ign_prob  = self.ign_prob.value()
        spotting  = self.spotting_cb.isChecked()
        spot_rng  = self.spot_range.value() if spotting else 0
        out_path  = self.out_path.text()

        elev_file = self.elev_path.text()
        lc_file   = self.lc_path.text()

        if not elev_file or not lc_file:
            QMessageBox.warning(self, "Missing input", "Please select elevation and land cover rasters.")
            return

        self.progress.setValue(10)

        # ── Read rasters ──────────────────────────────────────────────────────
        with rasterio.open(elev_file) as dem_src:
            elev_data = dem_src.read(1).astype(float)
            elev_transform = dem_src.transform
            elev_crs = dem_src.crs
            elev_bounds = dem_src.bounds

        with rasterio.open(lc_file) as lc_src:
            lc_data  = lc_src.read(1).astype(int)
            lc_transform = lc_src.transform

        self.progress.setValue(30)

        # ── Get simulation polygon ────────────────────────────────────────────
        sim_id  = self.sim_layer.currentData()
        ign_id  = self.ign_layer.currentData()

        sim_layer = QgsProject.instance().mapLayer(sim_id) if sim_id else None
        ign_layer = QgsProject.instance().mapLayer(ign_id) if ign_id else None

        # ── Build grid from raster bounds (or polygon extent) ─────────────────
        bounds = elev_bounds
        cols = max(10, int((bounds.right - bounds.left) / cell_m))
        rows = max(10, int((bounds.top  - bounds.bottom) / cell_m))

        # Limit grid size for performance
        if rows * cols > 200 * 200:
            scale = math.sqrt(rows * cols / (200 * 200))
            rows = int(rows / scale)
            cols = int(cols / scale)

        self.progress.setValue(50)

        # ── Sample elevation and land cover at grid points ─────────────────────
        from scipy.ndimage import zoom, gaussian_filter

        scale_r = rows / elev_data.shape[0]
        scale_c = cols / elev_data.shape[1]
        elev_grid = zoom(elev_data, (scale_r, scale_c), order=1)
        elev_grid = gaussian_filter(elev_grid, sigma=1.5)

        scale_r2 = rows / lc_data.shape[0]
        scale_c2 = cols / lc_data.shape[1]
        lc_grid  = zoom(lc_data, (scale_r2, scale_c2), order=0).astype(int)

        # Map NLCMS to fuel types
        fuel_grid = np.vectorize(lambda x: NLCMS_TO_FUEL.get(x, 3))(lc_grid)

        self.progress.setValue(65)

        # ── Build asymmetric neighbourhood ────────────────────────────────────
        def wf(dr, dc):
            if wind_spd == 0: return 1.0
            ang  = math.atan2(-dr, dc) * 180 / math.pi
            diff = abs(ang - wind_dir)
            if diff > 180: diff = 360 - diff
            return max(0.2, 1.0 + (wind_spd / 30.0) * math.cos(math.radians(diff)))

        def sf(my_e, nbr_e):
            diff = my_e - nbr_e
            ts   = abs(diff) / cell_m
            return (1.0 + 5.275*ts*ts) if diff <= 0 else max(0.4, 1.0 - 1.5*ts)

        MOORE = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
        cells = {}

        for r in range(rows):
            for c in range(cols):
                ft  = int(fuel_grid[r, c])
                elv = round(float(elev_grid[r, c]), 1)
                mst = round(FUEL_MOISTURE.get(ft, 0.18), 3)
                nbhd = {}

                if FUEL_BURNABLE.get(ft, False):
                    for dr, dc in MOORE:
                        nr, nc = r+dr, c+dc
                        if not (0<=nr<rows and 0<=nc<cols): continue
                        nft = int(fuel_grid[nr, nc])
                        if not FUEL_BURNABLE.get(nft, False): continue
                        w   = wf(dr, dc)
                        s   = sf(elv, float(elev_grid[nr, nc]))
                        d   = 1.0 if (dr==0 or dc==0) else 0.707
                        vic = round(w * s * d, 4)
                        if vic > 0.05:
                            nbhd[f"r{nr}_c{nc}"] = vic

                    # Spotting
                    if spot_rng > 0:
                        for dist in range(2, spot_rng+1):
                            for dr, dc in MOORE:
                                nr, nc = r+dr*dist, c+dc*dist
                                if not (0<=nr<rows and 0<=nc<cols): continue
                                nft = int(fuel_grid[nr, nc])
                                if not FUEL_BURNABLE.get(nft, False): continue
                                w = wf(dr, dc)
                                if w < 1.1: continue
                                actual_d = math.sqrt((dr*dist)**2+(dc*dist)**2)
                                vic = round(0.08 * w / (actual_d**1.5), 5)
                                if vic < 0.003: continue
                                k = f"r{nr}_c{nc}"
                                nbhd[k] = max(nbhd.get(k, 0), vic)

                cells[f"r{r}_c{c}"] = {
                    "delay": "inertial",
                    "state": {"state":1,"fuel_type":ft,"elevation":elv,
                              "moisture":mst,"intensity":0.0,"burn_steps_remaining":0},
                    "config": {"ignition_prob":ign_prob,"temperature":temp,
                               "humidity":hum,"ffmc":ffmc_val},
                    "neighborhood": nbhd
                }

        self.progress.setValue(85)

        # ── Mark ignition cells ────────────────────────────────────────────────
        ign_count = 0
        if ign_layer:
            for feat in ign_layer.getFeatures():
                geom = feat.geometry()
                bb = geom.boundingBox()
                cx = (bb.xMinimum() + bb.xMaximum()) / 2
                cy = (bb.yMinimum() + bb.yMaximum()) / 2
                # Convert to grid coordinates
                r0 = int((bounds.top - cy) / cell_m)
                c0 = int((cx - bounds.left) / cell_m)
                r0 = max(0, min(rows-1, r0))
                c0 = max(0, min(cols-1, c0))
                k = f"r{r0}_c{c0}"
                if k in cells and FUEL_BURNABLE.get(cells[k]["state"]["fuel_type"], False):
                    cells[k]["state"].update({"state":2,"intensity":0.9,"burn_steps_remaining":10})
                    ign_count += 1
        else:
            # Default: centre cell
            r0, c0 = rows//2, cols//2
            cells[f"r{r0}_c{c0}"]["state"].update(
                {"state":2,"intensity":0.9,"burn_steps_remaining":10})
            ign_count = 1

        # ── Write JSON ─────────────────────────────────────────────────────────
        scenario = {"cells": cells}
        with open(out_path, "w") as f:
            json.dump(scenario, f, separators=(',',':'))

        self.progress.setValue(100)

        size_kb = os.path.getsize(out_path) // 1024
        QMessageBox.information(self, "Done",
            f"Scenario generated:\n{out_path}\n\n"
            f"Grid: {rows}×{cols} = {len(cells)} cells\n"
            f"Cell size: {cell_m}m\n"
            f"Ignition cells: {ign_count}\n"
            f"File size: {size_kb}KB\n\n"
            f"Run with:\n./wildfire_sim {os.path.basename(out_path)} 500 42")


class WildfirePlugin:
    def __init__(self, iface):
        self.iface = iface
        self.action = None
        self.dialog = None

    def initGui(self):
        self.action = QAction("Wildfire Cell-DEVS", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("&Wildfire Cell-DEVS", self.action)

    def unload(self):
        self.iface.removePluginMenu("&Wildfire Cell-DEVS", self.action)
        self.iface.removeToolBarIcon(self.action)

    def run(self):
        if not self.dialog:
            self.dialog = WildfireDialog(self.iface, self.iface.mainWindow())
        self.dialog.show()
        self.dialog.raise_()
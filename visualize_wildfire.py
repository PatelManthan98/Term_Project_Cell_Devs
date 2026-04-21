import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.colors as mcolors
import re
import os

LOG_FILE = "build/grid_log.csv"
GRID_SIZE = (50, 50)
OUTPUT_GIF = "wildfire.gif"

if not os.path.exists(LOG_FILE):
    raise FileNotFoundError(f"Could not find {LOG_FILE}")

df = pd.read_csv(LOG_FILE, sep=";", header=None, engine="python",
                 names=["time", "model_id", "cell", "event", "state_raw"])

pattern = re.compile(r"\((\d+),(\d+)\).*state:(\d+), burn:(\d+)")

records = []

for _, row in df.iterrows():
    text = f"{row['cell']} {row['state_raw']}"
    m = pattern.search(text)
    if m:
        x, y, s, b = map(int, m.groups())
        records.append((row["time"], x, y, s))

records = pd.DataFrame(records, columns=["time", "x", "y", "state"])

timesteps = sorted(records["time"].unique())
frames = []

for t in timesteps:
    grid = np.zeros(GRID_SIZE, dtype=int)
    subset = records[records["time"] == t]
    for _, r in subset.iterrows():
        grid[r["x"], r["y"]] = r["state"]
    frames.append(grid)

cmap = mcolors.ListedColormap(["white", "green", "red", "black"])
bounds = [0, 1, 2, 3, 4]
norm = mcolors.BoundaryNorm(bounds, cmap.N)

fig, ax = plt.subplots(figsize=(6, 6))

def update(i):
    ax.clear()
    ax.imshow(frames[i], cmap=cmap, norm=norm)
    ax.set_title(f"Wildfire Simulation — t={timesteps[i]}")
    ax.axis("off")

ani = animation.FuncAnimation(fig, update, frames=len(frames), interval=150)

ani.save(OUTPUT_GIF, writer="pillow", fps=6)
print("Saved:", OUTPUT_GIF)

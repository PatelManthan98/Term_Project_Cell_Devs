"""
visualize_wildfire.py — Run: python3 visualize_wildfire.py
Generates GIFs for all scenarios in results/
"""
import numpy as np, pandas as pd, matplotlib.pyplot as plt
import matplotlib.animation as animation, matplotlib.colors as mcolors
import matplotlib.patches as mpatches
import re, os

SCENARIOS = [
    "calm",
    "windy",
    "firebreak",
    "firebreak_spot",
    "urban",
    "fortmcmurray_nospot",
    "fortmcmurray_spot",
]
GRID_SIZE  = (50, 50)
MAX_FRAMES = 80
os.makedirs("results", exist_ok=True)

def make_gif(name):
    log_file = f"results/grid_log_{name}.csv"
    out_gif  = f"results/wildfire_{name}.gif"
    if not os.path.exists(log_file):
        print(f"  SKIP {name} — {log_file} not found"); return

    df = pd.read_csv(log_file, sep=";", header=None, engine="python",
                     names=["time","model_id","cell","event","state_raw"])
    pat = re.compile(r"r(\d+)_c(\d+).*state:(\d+)")
    records = []
    for _, row in df.iterrows():
        m = pat.search(f"{row['cell']} {row['state_raw']}")
        if m:
            records.append((float(row["time"]), int(m.group(1)),
                            int(m.group(2)), int(m.group(3))))
    if not records:
        print(f"  SKIP {name} — no records"); return

    rdf = pd.DataFrame(records, columns=["time","row","col","state"])
    timesteps = sorted(rdf["time"].unique())
    if len(timesteps) > MAX_FRAMES:
        timesteps = timesteps[::len(timesteps)//MAX_FRAMES]

    grid = np.ones(GRID_SIZE, dtype=int)
    frames = []
    for t in timesteps:
        for _, r in rdf[rdf["time"]==t].iterrows():
            ri, ci = int(r.row), int(r.col)
            if 0<=ri<GRID_SIZE[0] and 0<=ci<GRID_SIZE[1]:
                grid[ri, ci] = int(r.state)
        frames.append(grid.copy())

    cmap = mcolors.ListedColormap(["#4a90d9","#2d6a4f","#d62828","#1a1a1a"])
    norm = mcolors.BoundaryNorm([0,1,2,3,4], cmap.N)

    fig, ax = plt.subplots(figsize=(6,6))
    fig.patch.set_facecolor("#0d0d0d")
    ax.set_facecolor("#0d0d0d"); ax.axis("off")
    ax.legend(handles=[
        mpatches.Patch(color="#4a90d9", label="Water/Road"),
        mpatches.Patch(color="#2d6a4f", label="Unburned"),
        mpatches.Patch(color="#d62828", label="Burning"),
        mpatches.Patch(color="#1a1a1a", label="Ash"),
    ], loc="lower left", fontsize=7, facecolor="#222", labelcolor="white")

    im    = ax.imshow(frames[0], cmap=cmap, norm=norm, origin="upper")
    title = ax.set_title("", color="white", fontsize=10, pad=8)
    total = GRID_SIZE[0] * GRID_SIZE[1]

    def update(i):
        im.set_data(frames[i])
        burning = int((frames[i]==2).sum())
        burned  = int((frames[i]==3).sum())
        title.set_text(
            f"{name}  t={timesteps[i]:.0f}\n"
            f"Burning:{burning}  Burned:{burned}({burned/total*100:.1f}%)"
        )
        return im, title

    ani = animation.FuncAnimation(fig, update, frames=len(frames),
                                  interval=150, blit=True)
    ani.save(out_gif, writer="pillow", fps=6)
    plt.close()
    print(f"  Saved: {out_gif}")

print("=== Wildfire Visualizer ===\n")
for name in SCENARIOS:
    print(f"[{name}]")
    make_gif(name)
print("\nAll done. GIFs saved to results/")
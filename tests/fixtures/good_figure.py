"""Known-good fixture: a figure that satisfies every checkable rule."""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from pathlib import Path

STYLE = Path(__file__).resolve().parents[2] / "skills" / "scientific-figures" \
    / "assets" / "paper-2col.mplstyle"
plt.style.use(str(STYLE))

rng = np.random.default_rng(0)
x = np.linspace(-3.0, 3.0, 200)
y = np.linspace(-3.0, 3.0, 200)
X, Y = np.meshgrid(x, y)
Z = np.sin(X) * np.cos(Y)

fig, ax = plt.subplots()
im = ax.pcolormesh(
    X, Y, Z, cmap="RdBu_r", shading="auto",
    norm=mcolors.TwoSlopeNorm(vmin=Z.min(), vcenter=0.0, vmax=Z.max()),
)
cs = ax.contour(X, Y, Z, levels=[0.0], colors="k", linewidths=1.2)
cbar = fig.colorbar(im, ax=ax)
cbar.set_label("Displacement [mm]")
ax.set_xlabel("x [m]")
ax.set_ylabel("y [m]")
fig.savefig("field.pdf")

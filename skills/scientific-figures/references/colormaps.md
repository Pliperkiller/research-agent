# Choosing a colormap

## Decision tree

1. The data **crosses zero** and the sign matters (anomaly, divergence,
   residual, field with polarity) -> **diverging**: `RdBu_r`, `coolwarm`,
   `BrBG`, `PuOr`. Centering white on zero is mandatory:

   ```python
   import matplotlib.colors as mcolors
   norm = mcolors.TwoSlopeNorm(vmin=Z.min(), vcenter=0.0, vmax=Z.max())
   ```

   or symmetric limits `vmin=-M, vmax=M` with `M = abs(Z).max()`. Without
   centering, zero lands on an arbitrary color and the figure lies about where
   the sign boundary is.

2. The data is **strictly positive** and monotonic in meaning (magnitude,
   density, absolute temperature, intensity) -> **perceptually uniform
   sequential**: `viridis`, `magma`, `inferno`, `cividis`.
   `cividis` is designed to look nearly identical under deuteranopia.

3. The data is **cyclic** (angle, phase, wind direction, time of day) ->
   `twilight`, `twilight_shifted`. A non-cyclic map introduces a false
   discontinuity at the wrap point.

4. The data is **categorical** (classes, labels) -> a discrete qualitative
   palette (`tab10`, `Set2`) plus a legend. Never a continuous colormap for
   categories: it implies an ordering that does not exist.

## Why `jet` is banned

Kovesi (2015) makes the case: lightness is the dominant factor in how the eye
reads a color map. If the lightness curve is not monotonic (sequential) or
clearly symmetric (diverging), the map will deceive the eye by creating
artificial structure in the data.

`jet` peaks in lightness at yellow and cyan: it produces bright bands where the
data has nothing special, and compresses contrast at the extremes. It also
collapses to near-uniform gray when printed in black and white.

**Ramp test (Kovesi):** apply the colormap to a linear ramp with a low-amplitude
sinusoidal ripple superimposed.
- Good colormap: the ripples are clearly and uniformly visible across the entire
  ramp.
- Bad colormap: the ripples vanish in some regions (dead zones) or appear
  exaggerated in others (artifacts).

`scripts/check_colormap.py` implements this test.

## Number of levels

A continuous colormap shows continuous variation; a discretized one
(`plt.get_cmap('viridis', 8)` or `contourf(..., levels=8)`) makes specific
values easier to read but loses the variation within each band. Choose by the
message: if the reader must **read values**, discretize; if the reader must
**see structure**, stay continuous.

## Colorbar

```python
cbar = fig.colorbar(im, ax=ax, shrink=0.85, pad=0.02)
cbar.set_label(r"Temperature [$^\circ$C]")
cbar.ax.tick_params(labelsize=8)
```

- Always labeled, always with units.
- If the field is signed, mark zero: `cbar.ax.axhline(0, color='k', lw=0.8)`.
- For multiple panels showing the same quantity, use one shared colorbar and the
  **same norm** across all of them. Different norms on panels presented as
  comparable is one of the most frequent deceptions.

## Accessibility

`pip install colorspacious` lets you simulate deuteranopia, protanopia and
tritanopia on any colormap. Rule of thumb: if converting the figure to grayscale
destroys the message, color is doing work it should be sharing with shape,
position or annotation.

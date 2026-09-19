# 2D scalar fields

The data is `z = f(x, y)`. Map x and y to the two screen dimensions, and z to
color or to height. Each representation highlights something different about the
same field; combining two is usually right.

## Which tool

| Tool | Shows well | Main limitation |
|---|---|---|
| `imshow` | rasterized field as an image, fast on pixel-like data | needs a regular grid; y axis is flipped by default |
| `pcolormesh` | real coordinates, non-uniform grids, vectorized | slightly slower than `imshow` |
| `pcolor` | same as `pcolormesh` but draws polygon by polygon | slow on large arrays; avoid it |
| `contour` / `contourf` | level structure, bands of equal value | loses variation inside each band |
| `plot_surface` | topography: peaks, valleys, saddle points | perspective distorts magnitudes and hides the back |

**Rule of thumb:**
- Image or pixel data -> `imshow`.
- Data with physical coordinates (meters, degrees, seconds) -> `pcolormesh`.
- Never `pcolor` on large arrays.

## `imshow` pitfalls

`imshow` reads the array as an image: row 0 is the **top** of the figure, and
the axes are pixel indices. Two mandatory corrections:

```python
im = ax.imshow(Z.T, origin="lower", extent=[x0, x1, y0, y1],
               cmap="RdBu_r", aspect="auto")
```

- `origin='lower'`: puts the origin at bottom left, like a Cartesian plane.
- `extent`: replaces indices with real coordinates.
- The transpose `.T`: if the grid comes from `np.mgrid[x0:x1:nj, y0:y1:nj]`, the
  first index runs along x, but `imshow` reads rows as y. `pcolormesh` does not
  suffer from this because it receives the coordinate arrays explicitly.
- `aspect`: `'equal'` when x and y share physical units, `'auto'` otherwise.

## Grids

```python
X, Y = np.meshgrid(x, y, indexing="xy")   # X.shape == (len(y), len(x))
X, Y = np.mgrid[-3:3:80j, -3:3:80j]       # 80 points, not step 80
```

The `80j` in `mgrid` means **number of points** over the closed interval, not
step size. `meshgrid` with `indexing='ij'` matches `mgrid`'s convention; with
`'xy'` (the default) it produces the transpose. Pick one and stay consistent
across the file: mixing them is the number one source of transposed figures.

## Contours

```python
cs = ax.contour(X, Y, Z, levels=[-2, -1, -0.5, 0, 0.5, 1, 2],
                colors="k", linewidths=0.6)
ax.clabel(cs, inline=True, fontsize=7, fmt="%.1f")
```

- If the field is signed, draw the **zero contour thicker**: it visually
  separates the positive from the negative regions.
- Use explicit `levels` whenever the values carry physical meaning; automatic
  levels land on arbitrary numbers.
- Recommended combination: `pcolormesh` (or `contourf`) for the field, plus thin
  black `contour` on top for the isolines.

## 3D surfaces

Use one only when topography is the message. Perspective distorts magnitudes and
hides the back, so it is never the right representation for reading values. If
you do use one:

```python
ax.view_init(elev=30, azim=-60)   # elev: 0 = side view, 90 = top-down
```

and consider projecting the contours onto the base plane
(`ax.contour(X, Y, Z, zdir='z', offset=Z.min())`) to recover the quantitative
reading that perspective takes away.

## Log scale

When the field spans orders of magnitude (gravitational potential, energy,
cost functions like Himmelblau, spectra):

```python
import matplotlib.colors as mcolors
im = ax.pcolormesh(X, Y, Z, norm=mcolors.LogNorm(vmin=Zpos.min(), vmax=Z.max()),
                   cmap="viridis", shading="auto")
```

`LogNorm` requires strictly positive data. With zeros or negatives, use
`SymLogNorm(linthresh=...)` and declare the `linthresh` in the colorbar label.

## Annotate the phenomenon

A scientific figure annotates what the reader is meant to see: the maximum, the
boundary, the wavefront, the critical point. Use `ax.annotate` with a short
arrow, or `ax.scatter` with a distinct marker over the points of interest.
Do not rely on the reader discovering on their own where the four minima are.

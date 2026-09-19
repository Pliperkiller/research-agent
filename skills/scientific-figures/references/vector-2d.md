# 2D vector fields

The data assigns `(u, v)` to each `(x, y)`: flow velocity, electric or magnetic
field, gradient of a scalar.

## quiver vs streamplot

| | `quiver` | `streamplot` |
|---|---|---|
| Shows | discrete vectors at grid points | continuous lines tangent to the field |
| Magnitude | in arrow length or color | in line color or width |
| Global structure | hard to read with many arrows | excellent: topology is visible |
| Local detail | explicit pointwise value | limited, interpolated |
| Singularities | problematic without normalizing | robust |
| Typical use | smooth fields, few vectors, quantitative physics | fluids, EM, qualitative analysis |

Decide by the message: if the reader must **read a pointwise value**, `quiver`;
if they must **understand the flow structure**, `streamplot`. Combining both in
one panel usually saturates it; two panels are better.

## quiver

```python
s = 3                                   # subsample: one arrow every 3 nodes
M = np.hypot(U, V)
q = ax.quiver(X[::s, ::s], Y[::s, ::s], U[::s, ::s], V[::s, ::s], M[::s, ::s],
              cmap="viridis", scale=None, width=0.004, pivot="mid")
fig.colorbar(q, ax=ax, label=r"$|\mathbf{u}|$ [m/s]")
```

- `scale`: larger value = shorter arrows. The automatic value is almost always
  too large or too small; tune it and check visually.
- `width`: 0.003-0.006 is the useful range.
- `pivot='mid'` centers the arrow on the node; `'tail'` (default) anchors it there.
- **Always subsample.** A quiver with one arrow per pixel is noise.
- If the field has singularities or high dynamic range, **normalize direction and
  encode magnitude in color**: `ax.quiver(X, Y, U/M, V/M, M)`. Without this, a
  few huge arrows flatten everything else.

## streamplot

```python
strm = ax.streamplot(x, y, U, V, color=M, cmap="viridis",
                     linewidth=1.0 + 2.0 * M / M.max(),
                     density=1.2, arrowsize=0.8)
fig.colorbar(strm.lines, ax=ax, label=r"$|\mathbf{u}|$ [m/s]")
```

- `streamplot` requires `x` and `y` to be **1D and strictly increasing** (not the
  2D meshes). This is the most frequent usage error.
- `density`: default 1; raise to 1.5-2 for fields with fine structure.
- `start_points` (Nx2 array) when you want lines from specific positions, e.g.
  from a source or a boundary.
- You cannot read a pointwise magnitude off a streamline: if the user needs it,
  magnitude goes into color **and** gets a colorbar.

## Gradient of a scalar field

```python
dZdy, dZdx = np.gradient(Z, y, x)       # output order follows the array axes
```

`np.gradient` uses centered finite differences. Watch the order: it returns
derivatives in the order of the array axes, not in `(x, y)` order. Verify
against a test field with a known derivative before trusting the result.

The gradient points along the direction of steepest increase, which is why the
canonical combination is the scalar field as `pcolormesh` plus its gradient as
`quiver` on top — it makes visible that the arrows are perpendicular to the
isolines.

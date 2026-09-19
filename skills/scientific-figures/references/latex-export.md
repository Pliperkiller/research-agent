# Export for papers and LaTeX

## Principle

Figure size is decided in Python, not in LaTeX. If you insert with
`\includegraphics[width=0.8\textwidth]{fig.pdf}`, LaTeX scales the PDF and the
typography with it: the figure's fonts stop matching the body text. Generate the
figure at its exact final width and insert it at scale 1.

## Column widths

| Format | Single column | Double column (full width) |
|---|---|---|
| IEEE / two-column journals | 3.5 in (88.9 mm) | 7.16 in (181.9 mm) |
| Single-column journal (A4, 1 in margins) | 6.3 in | -- |
| Nature | 89 mm | 183 mm |

Check the journal's guide before assuming. For a thesis, measure the actual
`\textwidth`:

```latex
\the\textwidth   % prints the width in pt; 1 in = 72.27 pt
```

```python
WIDTH_IN = 3.5
fig, ax = plt.subplots(figsize=(WIDTH_IN, WIDTH_IN / 1.618))
```

The golden ratio or 3:2 are reasonable starting points for height; adjust it to
the content, not the other way around.

## Output format

```python
fig.savefig("fig_field.pdf", bbox_inches="tight", pad_inches=0.02)
```

- **PDF** for anything vector (lines, contours, text). Scales losslessly.
- **PNG at 300-600 dpi** only when the figure is essentially a large rasterized
  image and the vector PDF would weigh tens of MB.
- Hybrid trick: `ax.pcolormesh(..., rasterized=True)` rasterizes only the dense
  field and keeps axes and text vector. Save as PDF with `dpi=300`.
- Never JPG: compression artifacts on high-contrast edges ruin the lines.

`bbox_inches='tight'` trims whitespace, which slightly changes the final width.
If you need the width exact to the millimeter, use
`fig.set_layout_engine('constrained')` and omit `bbox_inches`.

## Typography matching the document

To make the figure's fonts identical to the body text:

```python
plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.serif": ["Computer Modern Roman"],
    "pgf.rcfonts": False,
})
```

This requires a LaTeX installation. Without one, `mathtext` with
`mathtext.fontset='cm'` gets close and has no external dependencies.

For maximum fidelity, use the PGF backend, which exports LaTeX code instead of
an image (`fig.savefig("fig.pgf")`, then `\input{fig.pgf}`). LaTeX itself
typesets the text. It costs compilation time.

## Insertion block

Always deliver the ready-to-paste block alongside the figure:

```latex
\begin{figure}[tb]
  \centering
  \includegraphics{fig_field.pdf}
  \caption{Steady-state temperature field from the analytical solution of
  Laplace's equation. The diverging colormap centers white on the reference
  temperature; the thick line marks the equilibrium isotherm. The four minima
  are indicated with markers.}
  \label{fig:laplace-field}
\end{figure}
```

No `width=` in `includegraphics`: the figure already comes at the right width.

## Multipanel figures

Label panels with letters in the top-left corner, outside the data area:

```python
for ax, letter in zip(axes.flat, "abcd"):
    ax.text(-0.12, 1.02, f"({letter})", transform=ax.transAxes,
            fontweight="bold", va="bottom")
```

Comparable panels share limits and **the same color norm**, with a single
colorbar. Panels with different norms presented as comparable is a rigor error,
not a style one.

## Paper delivery checklist

- Exact column width, inserted unscaled
- Vector PDF (or selectively rasterized)
- Fonts matching the body text in size and family
- Legible when printed in black and white
- Self-contained caption: someone reading only the figure and caption gets the point
- Referenced in the text with `\ref{}`

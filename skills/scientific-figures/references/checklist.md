# Audit checklist

Walk this before delivering any figure. The number is the rule id reported by
`scripts/figure_lint.py`.

## Data and scale

- [ ] **R1** The colormap matches the structure of the data (diverging and
      zero-centered if it crosses zero; sequential if positive; cyclic if
      angular; qualitative if categorical)
- [ ] **R2** No `jet`, `rainbow`, `gist_rainbow`, `hsv` (unless strictly cyclic
      data) or `nipy_spectral`
- [ ] **R5** Bar chart y axis starts at zero; any truncation elsewhere is declared
- [ ] **R6** If the range spans orders of magnitude, a log scale is used and
      declared in the label
- [ ] Comparable panels share limits and color norm
- [ ] Outliers are shown, or their clipping is declared

## Legibility

- [ ] **R3** Every color-to-value mapping has a colorbar with label and units
- [ ] **R4** Both axes are labeled with units; no axis shows pixel indices where
      the data has physical coordinates
- [ ] With `imshow`: `origin='lower'` and `extent` are present
- [ ] Font sizes come from the medium's style sheet, not hardcoded per panel
- [ ] The figure is legible in grayscale, or color is not the only channel
      carrying the message
- [ ] Ticks on round numbers, no scientific-notation offset floating in a corner

## Composition

- [ ] **R7** The figure communicates a single message
- [ ] **R8** No chartjunk: no colored background, no unnecessary borders, no
      dominant grid, no shadows, no decorative 3D, no color without function
- [ ] Points of interest (maxima, boundaries, critical points) are annotated,
      not left for the reader to find
- [ ] Frameless legend, or direct labeling when there are few series
- [ ] `constrained_layout` or `tight_layout` active; nothing clipped

## Delivery

- [ ] **R9** Fixed seed if randomness is involved; explicit data paths; the file
      regenerates the figure exactly
- [ ] **R10** Caption written and delivered (LaTeX block or markdown cell)
- [ ] Output format correct for the medium (vector PDF for papers)
- [ ] Width equals the final insertion width, with no later scaling

## Report

When done, hand the user something in this shape:

```
Rules applied
  R1  field crosses zero -> RdBu_r with TwoSlopeNorm(vcenter=0)
  R4  axes in km, extent=[0, 100, 0, 50], origin='lower'
  R6  range 1e-3..1e2 -> LogNorm
  R10 LaTeX caption included below

Not applicable
  R5  no bar charts in this figure
```

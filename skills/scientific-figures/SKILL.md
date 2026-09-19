---
name: scientific-figures
description: Normative rules for producing correct scientific figures with matplotlib (2D scalar fields, vector fields, statistical and tabular charts, LaTeX/paper export). ALWAYS use this skill before writing any code that generates a figure, plot, chart, heatmap, vector field or data visualization in Python, even when the user just says "plot this", even for a quick exploratory figure, and even when the code is a single notebook cell. Also use it when asked to review, critique or improve an existing figure, prepare figures for a paper or thesis, choose a colormap or a scale, or fix a chart that "looks wrong".
---

# Scientific figures: a design contract

A scientific figure is not decoration: it is an argument. Every choice —
colormap, scale, representation, annotation — either encodes information or
destroys it. This skill turns those choices into verifiable rules instead of
leaving them to taste or to matplotlib's defaults.

Matplotlib's defaults are designed to work in any situation, not to be optimal
in any. Accepting them without judgment is the most common failure.

## Required workflow

Follow these four steps in order. Do not skip step 1: everything else derives
from it.

### Step 1 - Declare before coding

Before writing a single line, emit this block (short, in the chat):

```
DATA     : <2D scalar | 2D vector | time series | categorical | distribution | x-y relation>
SIGN     : <crosses zero | strictly positive | n/a>
RANGE    : <linear | spans orders of magnitude>
MEDIUM   : <paper-1col | paper-2col | slide | notebook>
MESSAGE  : <one sentence: what the reader must see>
PLAN     : <representation(s) and colormap chosen, and why>
```

If the user did not give you enough to fill DATA, SIGN or MEDIUM, inspect the
data first (shape, dtype, min, max, whether negatives exist, max/min ratio)
instead of assuming. If it is still ambiguous, ask — one question only.

This step exists because without it, the path of least resistance is `viridis`
plus defaults, which is almost never the right answer.

### Step 2 - Apply the style for the medium

Never hardcode font sizes or `figsize`. Load the style sheet matching the
declared MEDIUM:

```python
import matplotlib.pyplot as plt
from pathlib import Path

STYLE = Path(__file__).parent / "assets" / "paper-2col.mplstyle"  # whichever applies
plt.style.use(str(STYLE))
```

Available in `assets/`: `paper-1col.mplstyle`, `paper-2col.mplstyle`,
`slide.mplstyle`, `notebook.mplstyle`. If the code will run on another machine,
copy the `.mplstyle` into the user's repo rather than referencing the skill path.

The reason: a paper figure is read closely and the reader can linger; a slide
figure is seen from across a room for 30 seconds. The same figure does not serve
both, and what changes is not the content but the typography and line weights.

### Step 3 - Write the code

Always use the object-oriented API (`fig, ax = plt.subplots()`), never pyplot's
global state beyond `plt.subplots` and `plt.style.use`.

Read the reference matching the declared DATA:

| Declared DATA | Read before coding |
|---|---|
| 2D scalar (field, image, map, PDE solution) | `references/scalar-2d.md` |
| 2D vector (flow, gradient, E/B field) | `references/vector-2d.md` |
| series, categorical, distribution, x-y | `references/statistical.md` |
| any, when choosing color | `references/colormaps.md` |
| destination is a paper or LaTeX | `references/latex-export.md` |

### Step 4 - Audit before delivering

Run the linter on the generated file:

```bash
python scripts/figure_lint.py path/to/code.py
```

Report to the user which rules fired and how you resolved them. If a rule does
not apply to this particular case, say so explicitly rather than skipping it
silently. The full checklist, with rule numbers, is in
`references/checklist.md`.

## Hard rules

These are not negotiable unless the user explicitly asks otherwise.

**R1 - The colormap derives from the data, not from taste.**
If the field crosses zero, use a diverging colormap centered on zero (`RdBu_r`,
`coolwarm`) with `TwoSlopeNorm` or symmetric limits. With a sequential map, zero
gets no special color and the positive/negative structure disappears. If the
data is strictly positive, use a perceptually uniform sequential map (`viridis`,
`magma`, `cividis`). For angles or phase, use a cyclic map (`twilight`; `hsv`
only if the data is strictly cyclic).

**R2 - `jet`, `rainbow` and family are banned.**
Their lightness curve is not monotonic: it creates bands and artificial
structures that are not in the data, and it collapses when printed in
grayscale. A good colormap must remain interpretable in black and white.

**R3 - Every color-to-value mapping needs a colorbar.**
Without one, color carries no quantitative meaning. The colorbar gets a label
with units. Single exception: when color only distinguishes categories and a
legend is present.

**R4 - Axes labeled, with units.**
Never leave pixel indices as coordinates when the data has physical
coordinates. With `imshow` that requires `extent=[xmin, xmax, ymin, ymax]` and
`origin='lower'`.

**R5 - Never truncate the y axis on bar charts.**
Bars encode magnitude by area; truncating turns small differences into chasms.
On line charts truncation is acceptable if the range is visibly declared. Any
non-linear scale (log, symlog) must be declared in the axis label.

**R6 - If the data spans orders of magnitude, use a log scale.**
A linear scale over a wide-ranging quantity misleads as much as a truncated
axis: it flattens all the useful structure against zero. For 2D fields use
`LogNorm`; for axes, `set_xscale('log')`.

**R7 - One figure, one message.**
If there are two ideas, that is two panels or two figures. If the reader does
not know where to look, the figure failed.

**R8 - No chartjunk.**
No colored backgrounds, heavy borders, bright grids, shadows, decorative 3D, or
color without function. Every element must encode information. Color has exactly
two legitimate uses: encoding a scalar value, or highlighting one element above
the rest.

**R9 - Reproducible.**
Fixed seed wherever randomness is involved, explicit data paths, no hidden state
between cells. Running the file must regenerate the figure exactly.

**R10 - Every figure ships with its caption.**
A caption explains what the figure shows, how to read it, and what the reader is
seeing. Without it the figure is incomplete even when visually flawless. Deliver
the caption alongside the code: a LaTeX `figure` block for papers, a markdown
cell above the code cell for notebooks.

## Accessibility

Roughly 8% of men have some form of color vision deficiency. Before delivering a
figure whose message depends on color, check it:

```bash
python scripts/check_colormap.py viridis RdBu_r --out /tmp/cmap_report.png
```

The script plots the lightness profile, applies Kovesi's sinusoidal ramp test
(with a good colormap the ripples appear uniformly across the whole ramp; with a
bad one they vanish in dead zones or get exaggerated elsewhere), and simulates
deuteranopia, protanopia and tritanopia.

Never encode information in hue alone: pair color with marker shape, line style
or direct annotation.

## When asked to review an existing figure

Invert the workflow: run the linter, then walk `references/checklist.md` and
deliver a "Before -> After" report with concrete corrections and their
justification. Prioritize what changes how the data reads (R1, R5, R6) over the
cosmetic (R8).

## What this skill does not do

It is not a matplotlib API manual. If you need to recall how `subplot_mosaic` or
`GridSpec` work, consult the documentation; this skill decides *what* to plot and
*how it must look*, not the syntax.

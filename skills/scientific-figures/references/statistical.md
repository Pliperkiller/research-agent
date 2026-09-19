# Statistical and tabular charts

The standard here is the same as for a physical field: proper scales, labeled
axes with units, color with semantic function, outliers handled explicitly, and
zero redundant elements. A decorative bar chart is not a scientific figure.

## Before plotting: look at the statistics AND the data

Anscombe's quartet (1973) and the Datasaurus of Matejka & Fitzmaurice (2017)
make the same point: datasets with **identical** mean, variance and correlation
can have radically different distributions. Never summarize a distribution with
a mean bar without having looked at its spread first.

Practical consequence: if you show means, show the spread too — confidence
interval, standard deviation, or better, the individual points when `n` is
manageable.

## Which chart for which question

| Question | Chart | Note |
|---|---|---|
| How something changes over time | line | one time axis, no bars |
| Compare magnitudes across categories | bars | y axis from zero, always |
| How a variable is distributed | histogram, KDE, ECDF | declare the bin count |
| Compare distributions | boxplot + points, or violin | a boxplot alone hides the shape |
| Relationship between two variables | scatter | alpha or hexbin when overplotted |
| Part of a whole | stacked bars | never a pie chart |

## Specific rules

**Bars from zero, no exceptions.** A bar encodes magnitude by area; truncating
the axis makes a 2% difference look like 200%. If the useful range is narrow,
switch to points with a baseline, or to a difference chart.

**Complete time windows.** Cropping the x axis to a convenient period turns
moderate growth into a miracle. Show the full available series or declare the
crop in the caption.

**Twin y axes: avoid them.** Two series with different scales in one panel
create visual correlations that do not exist in the data, because the apparent
relationship depends on how you chose the two scales. Alternatives: two stacked
panels with a shared x axis, or normalize both series to a base index.

**Log scale where it belongs.** Algorithm benchmarks, populations, energies,
runtimes: almost always log on y. A linear scale over data spanning orders of
magnitude misleads as much as a truncated axis. Declare it in the label:
`Time [s, log scale]`.

**Outliers: never delete them silently.** Show them, or clip the axis while
declaring it and marking the out-of-range points with an arrow at the edge. A
hidden outlier is falsified data.

**Direct labeling over legends.** With few series, putting the name at the end
of each line (`ax.annotate`) removes the constant eye jump between legend and
plot. With many series, use a frameless legend (`frameon=False`).

**Meaningful ordering.** Categories are ordered by value, not alphabetically,
unless alphabetical is the order the reader will look things up in.

**Highlight one series, mute the rest.** When the message is about one category,
that one gets saturated color and the others gray. Coloring ten series with ten
distinct colors spreads attention instead of directing it.

## Overplotting

With many points, a plain scatter lies about density:

```python
ax.scatter(x, y, s=8, alpha=0.25, edgecolors="none")   # n ~ thousands
ax.hexbin(x, y, gridsize=40, cmap="viridis")           # n ~ tens of thousands
```

## Error bars and uncertainty

Always state **what** they represent: standard deviation, standard error, or
confidence interval. These are three different things, and a bar left
unexplained in the caption communicates nothing.

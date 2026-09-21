# Comments

The thesis of this skill: under-commenting is expensive and over-commenting is
cheap. A comment nobody needed costs two seconds to delete. A comment that was
needed and never written costs an afternoon with the paper open, and sometimes
the reason is simply lost.

So when in doubt, write it.

## What a comment is for

The code already says WHAT it does. If it does not, the names are wrong and
R1 is the fix, not a comment. What the code can never say is WHY: why this
value, why this sign, why this order, why this guard exists at all.

```python
# FTCS is stable while diffusivity * step / spacing**2 stays below one half.
# We sit at 40% of that bound: exactly at it, rounding in the last digit is
# enough to make the scheme grow instead of decay.
STABILITY_SAFETY_FACTOR = 0.4
```

That is three lines to save the next reader from re-deriving a stability
condition, or worse, from "simplifying" the factor to 1.0.

## The language rule

Identifiers and docstrings are English (R2). Comments are in the language the
team thinks in, declared once near the top of the file:

```python
# comment-language: es
```

The marker is not decoration: it is what makes the rule checkable. With it, a
linter can flag the one English comment that slipped into a Spanish file, and a
new contributor knows which language to write in without asking.

What is not acceptable is mixing. A reader who switches language every third
comment is spending attention on translation instead of on the code.

## Three comments that earned their place

```python
# The first node is Dirichlet: updating it would silently change the problem.
updated_temperature_celsius[1:-1] = ...

# detach() here and not below: the adversarial step must not push gradients
# back into the solution network, or the min-max collapses into a min.
test_value = test_network(points).detach()

# 1e-8 and not 1e-6: at 1e-6 the residual plateaus above the discretization
# error, so the run stops while the solution is still improving.
CONVERGENCE_TOLERANCE = 1.0e-8
```

Each one answers a question the reader would otherwise have to answer by
experiment.

## Three comments that must be deleted

```python
counter += 1        # increment the counter
# loop over the points
for point in points:
# old_version = compute(x, y)
```

The first two restate the line. The third is dead code: git already remembers
it, and leaving it in makes the reader wonder whether it is about to be
restored. Delete it.

## Commented-out code is dead code

Every commented-out block is a question the reader cannot answer: is this the
version that failed, the version to come back to, or something abandoned? If it
matters, it belongs in a commit message or a note that says what it was for.

## Docstring or comment?

The docstring is the contract with the outside: what goes in, what comes out,
in which units, with which shapes. The comment is the reason on the inside: why
this implementation, this constant, this order. A caller should never need to
read the comments; a maintainer should never have to guess them.

## Notebooks: markdown cell or `#`

Prose longer than three lines belongs in a markdown cell above the code, where
it can carry a formula and a heading. Inside the cell, keep the `#` comments
for the line-level WHY. A stack of ten `#` lines at the top of a code cell is a
markdown cell that was not written.

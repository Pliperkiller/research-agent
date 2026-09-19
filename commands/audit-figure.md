---
description: Audit a figure, or the code that generates it, against the scientific-figures rules
argument-hint: [path to a .py or .ipynb, or a description of the figure]
---

Audit the figure given in `$ARGUMENTS` using the `scientific-figures` skill.

1. If `$ARGUMENTS` is a path to a `.py` or `.ipynb`, run
   `python scripts/figure_lint.py <path>` from the skill.
2. Read `references/checklist.md` and walk the items the linter cannot decide on
   its own (R1, R6, R7, R10, cross-panel consistency, annotations).
3. Deliver a "Before -> After" report: for each finding, what is wrong, the
   concrete fix, and the rule that justifies it. Prioritize what changes how the
   data reads (colormap, scale, truncated axis) over the cosmetic.
4. Offer the full corrected code, not loose fragments.

---
description: Audit code, or a notebook, against the scientific-code legibility rules
argument-hint: [path to a .py or .ipynb, or the code to review]
---

Audit the code given in `$ARGUMENTS` using the `scientific-code` skill.

1. If `$ARGUMENTS` is a path to a `.py` or `.ipynb`, run
   `python scripts/code_style_lint.py <path>` from the skill.
2. Read `references/checklist.md` and walk the items the linter cannot decide
   on its own (whether each name reads as prose, whether the comments explain
   the why and are true, whether the declared unit is the real one, whether one
   concept carries one name across the file).
3. Deliver a "Before -> After" report: for each finding, what is unreadable,
   the concrete rename or comment, and the rule that justifies it. Prioritize
   what decides whether the code can be understood at all (names, language,
   units) over what makes it more comfortable (type hints, function length).
4. Offer the full corrected file, not loose fragments, and keep renaming
   separate from any change in behaviour — say explicitly which of the two you
   did.

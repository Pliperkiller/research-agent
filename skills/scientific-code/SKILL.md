---
name: scientific-code
description: Normative rules for writing scientific code that a human who did not write it can read: names that read as prose, English identifiers and docstrings, comments that explain why, units carried in the name, typed and documented public interfaces. ALWAYS use this skill before writing or editing any Python for analysis, simulation, numerical methods, model training or data processing, even for a single notebook cell, even for a quick throwaway script, and even when the user just says "write me a function for this". Also use it when asked to clean up, refactor, review, document or explain existing code, when naming anything, when turning notebook cells into a module, and when the user says "make this readable", "add comments", "rename these variables" or "I do not understand this code anymore".
---

# Scientific code: a legibility contract

Scientific code is read far more often than it is written, and almost never by
the person who wrote it — a reviewer, a co-author, a student inheriting the
repository, or the author six months later, who is a stranger with the same
password. Code that was obvious while you held the derivation in your head is
opaque the moment you put it down.

This skill treats legibility as part of correctness. A result nobody can audit
is not a result, and a name that needs the paper open beside it has moved
information out of the code into a place where it rots. Every rule below is
verifiable: either the linter decides it, or a human can point at the line and
say yes or no.

## Required workflow

Follow these four steps in order. Do not skip step 1: the names you choose in
it are most of what the reader will ever see.

### Step 1 - Declare before coding

Before writing a single line, emit this block (short, in the chat):

```
ARTIFACT : <analysis script | notebook cells | simulation module | library function>
READER   : <who opens this next: the author in six months | an advisor | a reviewer | a teammate>
LIFESPAN : <throwaway, one run | reused for weeks | maintained, others will edit it>
DOMAIN   : <one line: what is being computed, and the units in play>
COMMENTS : <language for comments: en | es | ...>
PLAN     : <the names the main objects will carry, written out before the code>
```

If the user did not give you enough to fill DOMAIN or COMMENTS, look first:
read the surrounding files and copy the comment language already in use, and
read the equations or the data to find the units. If it is still ambiguous,
ask — one question only.

PLAN is the load-bearing field. Writing `initial_temperature_celsius,
interior_points, boundary_weight` before coding costs ten seconds and removes
the moment where `u0`, `X` and `lam` appear because the code was faster to type
than to name. LIFESPAN never waives R1, R2 or R3 — those are free at any
lifespan — it only decides what counts as *public* for R4.

### Step 2 - Apply the convention

Load the header template and start from it, instead of typing `import numpy`
and improvising:

```
assets/script-header.py
```

It carries the module docstring skeleton (purpose, inputs, outputs, units), the
`# comment-language: <xx>` marker that records the COMMENTS field inside the
file, the import order, and a `main() -> None` entry point. For a notebook, the
marker goes in the first code cell and the docstring becomes the first markdown
cell.

When the domain has conventional single-letter symbols, load
`assets/naming-glossary.md`: a lookup table from the symbol you were about to
type to the name you should write instead (`u0` -> `initial_condition`,
`lam` -> `penalty_weight`, `n_int` -> `n_interior_points`). Look the symbol up
rather than deciding again each time; that is what makes naming consistent
across a repository instead of consistent within a function.

### Step 3 - Write the code

Read the reference matching what you are writing:

| What you are writing | Read before coding |
|---|---|
| anything with a name in it | `references/naming.md` |
| numerical methods, meshes, tensors, PDE or model code | `references/numerical-code.md` |
| a function another file or cell will call | `references/public-interface.md` |
| deciding what deserves a comment | `references/comments.md` |

### Step 4 - Audit before delivering

Run the linter on the produced file:

```bash
python scripts/code_style_lint.py path/to/code.py
```

Report to the user which rules fired and how you resolved them. The linter is
deliberately noisy on R3: it flags every clip, detach, seed or cast with no
comment beside it, because under-commenting is the expensive failure and
over-commenting is not. If a finding does not apply, say so explicitly rather
than skipping it silently. The full checklist, with rule numbers, is in
`references/checklist.md`.

## Hard rules

These are not negotiable unless the user explicitly asks otherwise.

**R1 - Names read as prose, and length is not a cost.**
`initial_condition`, `interior_points`, `boundary_weight`, `n_interior_points`.
Not `u0`, `X`, `p`, `lam`, `n_int`. The reader has no access to the derivation
where `lam` meant something; what they have is the identifier. Typing a long
name costs one autocompletion, reading a short one costs a scroll back through
the file to find where it was assigned — and that cost is paid on every read,
by every reader. An abbreviation is legible only to the person who chose it.

**R2 - Identifiers and docstrings in English; comments in the declared working language.**
English for identifiers and docstrings because that is the part that travels:
it lands in a paper, a repository, an issue, a thread with a collaborator.
Comments are the part that stays, so they go in the language the author thinks
in, declared once with `# comment-language: es` and held constant inside the
file. Mixing `# calcula el paso` with `# now normalise` in one file makes the
reader switch languages mid-scroll for no benefit. Never translate an
identifier into another language, and never force a comment into English when
it is being written for a team that does not work in English.

**R3 - Over-comment. A comment you can delete is cheaper than one you needed and did not write.**
The comment explains the WHY, never the WHAT: why *that* value, why *that*
sign, why `detach()` there, why the tolerance is `1e-8` and not `1e-6`, why the
loop starts at the second node. `# increment the counter` above `counter += 1`
is noise; `# the first node is Dirichlet, updating it would silently change the
problem` is the reason the line exists. Deleting an excess comment takes two
seconds; reconstructing a missing one takes an afternoon with the paper open,
and sometimes it cannot be done at all.

**R4 - Every public function declares its interface: docstring and type hints.**
Public means something else calls it — another file, another cell, the user.
The docstring says what it returns and in which units; the annotations say what
goes in and what comes out. Without them the only way to call a function is to
read its body, which is exactly the work the function existed to save. Private
helpers (`_name`) and one-off locals are exempt.

**R5 - A number with a physical meaning carries its unit.**
`timestep_seconds`, `rod_length_meters`, `temperature_celsius`. A bare
`timestep` is a question, and the reader answers it by guessing. This is not
pedantry: unit mismatches are the classic silent failure in scientific code,
because the program runs, produces plausible numbers, and is wrong. If the unit
does not fit the name, put it in a trailing bracket comment —
`tolerance = 1e-8  # [dimensionless, relative residual]` — the same `[unit]`
convention the axis labels use in `scientific-figures`.

**R6 - A literal that appears twice, or that decides a branch, is a named constant.**
`if residual < 1e-8` tells the reader nothing about what `1e-8` means, or
whether the `1e-8` three functions below is the same number. Promote it to a
module-level `CONVERGENCE_TOLERANCE = 1e-8` and the comment explaining the
choice finally has somewhere to live. A repeated magic number is also a bug
waiting to happen: someone will tune one of the copies.

**R7 - A function fits on one screen.**
Fifty lines is the ceiling. Past that, the reader is holding more state in
their head than the function has earned, and review degrades into skimming. A
long function is almost never irreducible: it is three named steps that were
never given names. Splitting it is also how the WHY comments find their natural
place, at the top of each piece.

## Notebooks and cells

The rules do not relax in a notebook; the failure mode is worse there, because
a cell is written to be run once and then read for a year. The linter takes
notebooks directly:

```bash
python scripts/code_style_lint.py analysis.ipynb
```

It concatenates the code cells and blanks out `%` and `!` magic lines. Two
notebook-specific habits: the `# comment-language:` marker goes in the first
code cell, and prose longer than three lines belongs in a markdown cell above
the code, not in a stack of `#` lines inside it.

## When asked to review or refactor existing code

Invert the workflow: run the linter first, then walk `references/checklist.md`,
then deliver a "Before -> After" report with concrete renames and the rule that
justifies each one. Prioritize what decides whether the code can be understood
at all (R1, R2, R5) over what makes it more comfortable (R4, R7). Rename
mechanically and completely — a half-applied rename is worse than none, because
now two names mean the same thing. Never change behaviour and naming in the
same step, and say explicitly which of the two you did.

## What this skill does not do

It is not a Python style guide: indentation, line length and import sorting are
a formatter's job, not a rule here. It does not decide whether the algorithm is
correct or efficient. It does not cover reproducibility — seeds, pinned
environments, data paths and separating computation from presentation belong to
the `analysis-scripts` skill. It governs one thing: whether a stranger can read
what you wrote.

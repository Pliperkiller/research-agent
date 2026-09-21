# Audit checklist

Walk this before delivering any code. The number is the rule id reported by
`scripts/code_style_lint.py`.

## Names

- [ ] **R1** Every identifier reads as prose in the line where it is used: no
      `u0`, `X`, `lam`, `tmp`, `n_int`, no single letters, no numbered stems
- [ ] **R5** Every quantity with a physical meaning carries its unit in the
      name, or a trailing `[unit]` comment
- [ ] **R6** No numeric literal repeated across the file; thresholds that decide
      a branch are named module-level constants
- [ ] One concept, one name, across the whole file

## Language

- [ ] **R2** Identifiers and docstrings are in English
- [ ] **R2** Comments are all in one language, declared with
      `# comment-language: <xx>` near the top
- [ ] User-facing strings and log messages follow the project's declared
      language, not the comment language

## Comments

- [ ] **R3** Every non-obvious decision says WHY: the value, the sign, the
      tolerance, the detach, the clip, the cast, the seed
- [ ] **R3** No comment restates the line below it
- [ ] No commented-out code left behind
- [ ] Prose longer than three lines lives in a docstring or a markdown cell

## Interface and shape

- [ ] **R4** Every public function has a docstring saying what it returns and
      in which units
- [ ] **R4** Every public signature is fully annotated, return type included
- [ ] Array shapes are documented for anything that is not a scalar
- [ ] **R7** No function exceeds 50 lines, and the script is not one flat block

## Report

When done, hand the user something in this shape:

```
Rules applied
  R1  u0 -> initial_temperature_celsius, lam -> boundary_weight,
      n_int -> n_interior_points
  R2  identifiers and docstrings in English; comments in es, declared in the header
  R3  16 comments over 90 logical lines; the clip and the detach now say why
  R5  timestep_seconds, rod_length_meters, tolerance [dimensionless]
  R6  1e-8 promoted to CONVERGENCE_TOLERANCE, used in three places

Not applicable
  R4  nothing here is imported elsewhere; every helper is private
  R7  no function reaches 50 lines
```

# Naming

The name is the only documentation that is impossible to skip. It appears at
every use, it survives copy-paste into an issue, and it is the first thing a
reviewer reads. Everything else about legibility is downstream of it.

## The test

Read the line out loud. If it sounds like a sentence about the problem, the
names are right:

```python
timestep_seconds = stable_timestep_seconds(grid_spacing_meters)     # reads
dt = f(h)                                                           # does not
```

The second line is not shorter in any way that matters. It is the same
information with the labels removed, and the reader has to put them back from
memory every time they pass through.

## Anatomy of a name

A good name answers three questions in order: **what** it is, **which** one,
and **in what unit**. `temperature`, `initial_temperature`,
`initial_temperature_celsius`. Stop at the first point where a reader in the
domain would no longer have to ask.

Data is a noun phrase: `boundary_points`, `loss_history`, `stiffness_matrix`.
A function is a verb phrase: `compute_residual`, `load_measurements`,
`stable_timestep_seconds` (the verb is implied by "return the"). Predicates
read as questions: `is_converged`, `has_boundary_nodes`.

## The math-symbol trap

Papers use single letters because a paper has a nomenclature section, a
surrounding paragraph, and a reader who is holding the derivation. Code has
none of that. The symbol belongs in the comment, where it links the code back
to the equation, and the name belongs in the code:

```python
# u_t + H(u)_x = 0, with lambda the penalty on the boundary term (eq. 4.6)
boundary_penalty_weight = 0.3
```

Now the reader can go from the paper to the code and back. With `lam = 0.3`
they can only go one way, and only if they already know the paper.

## Units in the name

| Quantity | Suffix |
|---|---|
| time, duration, period | `_seconds`, `_milliseconds`, `_days` |
| length, distance, spacing | `_meters`, `_millimeters`, `_pixels` |
| temperature | `_celsius`, `_kelvin` |
| angle | `_radians`, `_degrees` |
| ratio | `_percent`, `_fraction` |
| count | `n_` prefix: `n_samples`, `n_iterations` |

The prefix `n_` is the one abbreviation that earns its place: it is universal,
unambiguous, and it puts the noun where the eye looks for it.

## Counts, indices and loops

`for i in range(n)` is the one habit everybody defends. It survives only where
the index means nothing at all — and then `_` says so more honestly. The moment
the index selects something, name it:

```python
for node_index in range(n_interior_points):
    residual[node_index] = ...
```

The payoff is not at the `for`, it is forty lines later when `node_index`
appears inside a nested expression and the reader does not have to scroll up to
learn which of the three loops it belongs to.

## Abbreviations you may keep

An acronym established in the field, written lower case inside a longer name:
`rms_error`, `fft_magnitudes`, `pde_residual`, `cfl_number`. The test is
whether a competent reader in the domain would have to look it up. Invented
contractions never pass it: `calc`, `prm`, `vals`, `tmp`, `res`, `aux`.

Full table of replacements: `assets/naming-glossary.md`.

## Renaming code you inherited

Rename completely or not at all. A half-applied rename leaves two names for one
concept, which is strictly worse than one bad name. Use the editor's rename
symbol rather than find-and-replace, which will happily rewrite a substring
inside an unrelated word.

Keep the rename in its own commit, with no behavioural change in it. Then a
reviewer can read the diff as "nothing happened here" and move on, instead of
hunting for the real change among two hundred renamed lines.

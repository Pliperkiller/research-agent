# Numerical and model code

Numerical code has a specific failure mode: it runs, produces plausible
numbers, and is wrong. Nothing crashes when the units disagree, when a sign is
flipped, or when a gradient flows where it should not. The only defence is that
a human can read the code and see it.

## From equation to code

Name by physical meaning, not by the letter in the paper. Put the letter in the
comment so the two can be matched:

```python
# u_t + (u^2/2)_x = 0 on [-1, 1], Burgers with a moving shock (eq. 18)
def flux_function(solution_values: np.ndarray) -> np.ndarray:
    """Burgers flux H(u) = u^2 / 2, same units as the solution squared."""
    return 0.5 * solution_values ** 2
```

The comment is the bridge. Without it the reader cannot check the code against
the paper; without the names they cannot read the code at all.

## Array shapes belong in the docstring

A shape is part of the contract and Python will not enforce it:

```python
def residual(points: np.ndarray, values: np.ndarray) -> np.ndarray:
    """Pointwise PDE residual.

    points : (n_points, 2) positions as (x, t)
    values : (n_points,) solution sampled at those positions
    returns: (n_points,) residual, same units as u_t
    """
```

Three lines that remove every transposition bug the reader would otherwise find
by running it.

## Comment the sign, the scale and the detach

These are the three decisions that are invisible in the diff and expensive to
reconstruct.

- **Sign.** `-` in a loss, in a flux, or in an adversarial step is a modelling
  decision. Say which convention you are following.
- **Scale.** Every `1e-3`, `0.5` or `clip(-1, 1)` came from somewhere: a
  stability bound, the data range, a tuning run. Write down which.
- **Detach and no_grad.** These change what is being optimised, silently. A
  misplaced `detach()` turns a min-max into a min and the run still converges,
  to the wrong thing.

## Naming a discretization

One vocabulary, used consistently: `mesh` or `grid` for the discretization,
`nodes` or `grid_points` for its points, `interior` and `boundary` for the two
groups, `spacing` for the distance between them. Then `n_interior_points` and
`boundary_values` read themselves, and `n_int` never has to be decoded.

Collocation and sampling follow the same rule: `collocation_points`,
`initial_points`, `boundary_points`, each with its `n_` count.

## Tolerances, epsilons and guards

Every `1e-x` in the file is a decision with consequences, so each one gets a
name (R6) and a sentence (R3):

```python
# Guard against division by zero at t = 0, where the rarefaction fan is a
# single point. 1e-12 is below the smallest timestep we ever take.
RAREFACTION_TIME_FLOOR = 1.0e-12
```

An epsilon without a comment is indistinguishable from an epsilon somebody
typed to make a crash go away.

## Vectorization that hides intent

A vectorized expression is worth writing and worth explaining. When the
one-liner stops being readable, the comment carries the loop it replaced:

```python
# Centred second difference over the interior nodes; this is the loop
# for i in 1..n-2: (u[i+1] - 2u[i] + u[i-1]) / dx^2, written as slices.
second_derivative = (values[2:] - 2.0 * values[1:-1] + values[:-2]) / spacing ** 2
```

Slicing bugs are off-by-one bugs, and off-by-one bugs are exactly what a reader
can catch if they know what the slices were supposed to mean.

## Randomness and device placement

`seed`, `.to(device)`, `.astype(np.float32)` and `requires_grad_()` all change
results and none of them look like they do. Comment the intent: which seed and
why it is fixed, why this tensor moves and that one does not, why single
precision is enough here. In training code, also say what is being held
constant between runs when you compare them.

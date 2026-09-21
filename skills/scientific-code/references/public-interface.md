# Public interfaces

A function exists so the caller does not have to read its body. Everything in
this file serves that one sentence.

## What "public" means here

Public is anything called from outside the function that defines it: another
module, another notebook cell, a test, the user. In a script, the top-level
functions are public even if nothing imports them, because the next cell or the
next reader will call them.

Private is a nested helper, or a name starting with `_`. R4 does not apply to
it — but R1, R2 and R3 still do.

## The docstring contract

One imperative line saying what the function returns, then whatever the caller
cannot guess: units, shapes, error conditions.

```python
def stable_timestep_seconds(grid_spacing_meters: float) -> float:
    """Largest time step the explicit scheme tolerates, in seconds."""
```

The unit is in the name and repeated in the docstring, which is not redundancy:
one of the two is what the reader happens to look at.

## Type hints that carry meaning

Annotate every parameter and the return, including `-> None`. The absent return
annotation is the common miss, and it is the one that tells a reader whether a
function computes something or mutates something.

```python
def save_profile(temperature_celsius: np.ndarray, output_path: Path) -> None:
```

`np.ndarray` and `torch.Tensor` say almost nothing on their own, so the shape
goes in the docstring. When a bare `float` would be ambiguous between two
quantities, the name carries the distinction, not the type.

## One-line docstrings and when to scale up

One line is enough while the signature answers everything else. Scale to a
structured docstring when there is more than one parameter whose meaning is not
obvious from its name, when shapes matter, or when the function can raise.
Copying a numpy-style template onto a two-line helper is ceremony, not
documentation.

## Default arguments are decisions

A numeric default is a magic number in the signature:

```python
def train(n_epochs: int = 5000, learning_rate: float = 1e-3) -> LossHistory:
```

Either the value is standard for the domain and the docstring says so, or it
came from a tuning run and a comment says which. The reader's question is
always the same: may I change this, and what breaks if I do.

## What not to document

Do not restate the body. A docstring that walks through the implementation line
by line goes stale on the first edit and misleads from then on. Document the
contract, which is what callers depend on and what you intend to keep stable.

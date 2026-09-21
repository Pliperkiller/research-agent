# Naming glossary

Look the symbol up instead of deciding again. That is what keeps naming
consistent across a repository rather than consistent within one function.

The left column is what you were about to type. The right column is what to
write instead. When several names are listed, the domain decides which one: a
name is only better than `lam` if it says which of the meanings is in play.

## Numerical methods and PDEs

| About to type | Write instead |
|---|---|
| `u`, `y` | `solution`, `temperature_celsius`, `displacement_meters` — name the quantity, not the letter |
| `u0`, `ic` | `initial_condition`, `initial_temperature_celsius` |
| `ue`, `u_ex` | `exact_solution`, `reference_solution` |
| `x`, `xs` | `position_meters`, `grid_positions`, `sample_positions` |
| `t` | `time_seconds`, `simulated_time_seconds` |
| `dt` | `timestep_seconds` |
| `dx`, `h` | `grid_spacing_meters` |
| `n`, `N` | `n_grid_points`, `n_samples`, `n_iterations` — say what is being counted |
| `n_int` | `n_interior_points` |
| `nb`, `n_bc` | `n_boundary_points` |
| `bc` | `boundary_condition` |
| `tol`, `eps` | `convergence_tolerance`, `regularization_epsilon` |
| `res` | `residual` or `result` — the ambiguity is the reason to spell it |
| `err` | `absolute_error`, `relative_error` — which one matters |
| `f`, `rhs` | `source_term`, `flux_function`, `right_hand_side` |
| `A`, `M` | `stiffness_matrix`, `mass_matrix`, `coefficient_matrix` |
| `b` | `load_vector`, `right_hand_side_vector` |
| `k` | `thermal_conductivity`, `wavenumber`, `iteration_index` |
| `c` | `wave_speed_meters_per_second`, `entropy_level` |
| `phi`, `psi` | `test_function`, `basis_function`, `phase_radians` |
| `cfl` | `courant_number` — a domain acronym, but spell the concept once in the docstring |

## Models and training

| About to type | Write instead |
|---|---|
| `lam`, `lmbda` | `penalty_weight`, `regularization_strength`, `wavelength_meters` |
| `lr` | `learning_rate` |
| `bs` | `batch_size` |
| `opt` | `optimizer` |
| `crit` | `loss_function` |
| `X`, `Xs` | `features`, `input_batch`, `collocation_points` |
| `y`, `ys` | `targets`, `labels` |
| `y_hat`, `pred` | `predictions`, `predicted_temperature_celsius` |
| `net`, `mdl` | `model`, `solution_network`, `test_function_network` |
| `ep`, `ne` | `epoch_index`, `n_epochs` |
| `hist` | `loss_history` |
| `dev` | `compute_device` |

## Data and general code

| About to type | Write instead |
|---|---|
| `df` | `measurements`, `raw_readings` — name the table's content, not its type |
| `arr`, `a` | `values`, `samples`, and put the shape in the docstring |
| `tmp`, `temp` | whatever it holds; `temp` is also a units trap next to `temperature` |
| `val`, `vals` | `value`, `values`, or the quantity itself |
| `cnt` | `count`, `n_failures` |
| `idx`, `i` | `row_index`, `node_index`, `sample_index` |
| `lst`, `dct` | `pending_files`, `weights_by_name` — say the content and the key |
| `cfg`, `conf` | `configuration`, `run_settings` |
| `fn`, `fname` | `input_path`, `output_path` |
| `aux` | the helper's actual job: `normalized_copy`, `padded_signal` |
| `calc`, `proc` | `compute_*`, `process_*` — a function is a verb phrase |
| `data` | almost always too vague: which data, in which state |

## Acronyms you may keep

Established domain acronyms stay as they are, in lower case inside a longer
name: `rms_error`, `fft_magnitudes`, `pde_residual`, `mse_loss`, `cfl_number`,
`svd_components`. The test is whether a reader in the field would have to look
it up. `rms` passes. `lam` does not.

## Suffixes for units

`_seconds`, `_meters`, `_kelvin`, `_celsius`, `_kilograms`, `_joules`,
`_hertz`, `_radians`, `_degrees`, `_percent`, `_fraction`, `_pixels`,
`_samples`, `_steps`. For a compound unit, spell it: `_meters_per_second`,
`_watts_per_square_meter`. For a dimensionless quantity, say so in a trailing
comment rather than leaving the reader guessing.

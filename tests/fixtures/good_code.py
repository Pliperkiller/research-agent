"""Known-good fixture: numerical code that satisfies every checkable rule.

Purpose
    Explicit finite-difference solution of the 1D heat equation on a rod whose
    two ends are held at a fixed temperature.
Inputs
    Grid resolution and simulated duration, given by the caller.
Outputs
    The temperature profile along the rod at the end of the simulation.
Units
    SI: meters, seconds, degrees Celsius.
"""
from __future__ import annotations

import numpy as np

# comment-language: en

ROD_LENGTH_METERS = 1.0
# Diffusivity of a metal bar, order 1e-4. It sets the only timescale in the
# problem, so every step size below is derived from it rather than chosen.
THERMAL_DIFFUSIVITY_M2_PER_SECOND = 1.0e-4
FIXED_END_TEMPERATURE_CELSIUS = 0.0
STABILITY_SAFETY_FACTOR = 0.4


def stable_timestep_seconds(grid_spacing_meters: float) -> float:
    """Largest time step the explicit scheme tolerates, in seconds."""
    # FTCS is stable while diffusivity * step / spacing squared stays below one
    # half. We sit at 40% of that bound: exactly at it, rounding in the last
    # digit is enough to make the scheme grow instead of decay.
    diffusion_number_limit = 0.5
    return (STABILITY_SAFETY_FACTOR * diffusion_number_limit
            * grid_spacing_meters ** 2 / THERMAL_DIFFUSIVITY_M2_PER_SECOND)


def initial_temperature_celsius(position_meters: np.ndarray) -> np.ndarray:
    """Initial condition, in Celsius: a gaussian bump centred on the rod.

    position_meters : (n_grid_points,) node positions along the rod
    returns         : (n_grid_points,) temperature at those positions
    """
    bump_centre_meters = ROD_LENGTH_METERS / 2.0
    bump_width_meters = ROD_LENGTH_METERS / 10.0
    # A gaussian keeps the initial condition smooth. A step would be legal
    # physics, but the first updates would ring, and that ringing looks exactly
    # like an instability that is not actually present.
    return np.exp(-((position_meters - bump_centre_meters)
                    / bump_width_meters) ** 2)


def step_forward(temperature_celsius: np.ndarray,
                 timestep_seconds: float,
                 grid_spacing_meters: float) -> np.ndarray:
    """One explicit FTCS update; the two end nodes keep their fixed value."""
    updated_temperature_celsius = temperature_celsius.copy()
    # Centred second difference over the interior nodes, written as slices.
    second_derivative = (temperature_celsius[2:]
                         - 2.0 * temperature_celsius[1:-1]
                         + temperature_celsius[:-2]) / grid_spacing_meters ** 2
    # Only the interior moves: the end nodes are the Dirichlet boundary, and
    # overwriting them would silently change the problem being solved.
    updated_temperature_celsius[1:-1] = (
        temperature_celsius[1:-1]
        + THERMAL_DIFFUSIVITY_M2_PER_SECOND * timestep_seconds
        * second_derivative)
    return updated_temperature_celsius


def run_simulation(n_grid_points: int,
                   simulated_duration_seconds: float) -> np.ndarray:
    """Return the temperature profile in Celsius after the given duration."""
    position_meters = np.linspace(0.0, ROD_LENGTH_METERS, n_grid_points)
    grid_spacing_meters = float(position_meters[1] - position_meters[0])
    timestep_seconds = stable_timestep_seconds(grid_spacing_meters)
    temperature_celsius = initial_temperature_celsius(position_meters)
    # The ends are pinned before the loop so that the very first update already
    # sees the boundary condition it has to respect.
    temperature_celsius[0] = FIXED_END_TEMPERATURE_CELSIUS
    temperature_celsius[-1] = FIXED_END_TEMPERATURE_CELSIUS
    for _ in range(int(simulated_duration_seconds / timestep_seconds)):
        temperature_celsius = step_forward(
            temperature_celsius, timestep_seconds, grid_spacing_meters)
    return temperature_celsius

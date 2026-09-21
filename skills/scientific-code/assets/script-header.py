"""<One line: what this script computes, in the present tense.>

Purpose
    <Why this file exists, and the question it answers. Two lines at most.>
Inputs
    <Each input: where it comes from and in which units.>
Outputs
    <Each output: what is written or returned, and in which units.>
Units
    <The unit convention the whole file obeys, stated once: SI, CGS, pixels...>
"""
from __future__ import annotations

# comment-language: en
# Declara aqui el idioma de los comentarios y no lo cambies dentro del archivo.
# Replace the two-letter code above with the language this file is commented in.

# Standard library first, third party second, local last: the reader can tell
# at a glance which dependencies are yours and which are the world's.
import numpy as np

# Constants carry their unit in the name (R5) and exist so that no bare literal
# decides a branch further down (R6). The comment records WHY the value is this
# value, which is the one thing the number itself cannot say.
SAMPLE_RATE_HERTZ = 1_000.0
CONVERGENCE_TOLERANCE = 1.0e-8  # [dimensionless] relative residual, tighter than float32 noise


def main() -> None:
    """Run the computation end to end and write its outputs."""
    raise NotImplementedError("replace this with the body of the script")


if __name__ == "__main__":
    main()

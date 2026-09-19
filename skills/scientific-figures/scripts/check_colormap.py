#!/usr/bin/env python3
"""Colormap diagnostics: lightness, Kovesi ramp test and color vision deficiency.

Usage:
    python check_colormap.py viridis RdBu_r jet --out report.png
    python check_colormap.py --list-good

Three panels per colormap:
  1. The color bar as-is.
  2. Ramp test (Kovesi): a linear ramp with a low-amplitude sinusoidal ripple.
     With a good colormap the ripples are equally visible across the whole
     ramp. With a bad one they vanish in dead zones or get exaggerated
     elsewhere.
  3. The same bar converted to grayscale. If the message is lost here, color is
     carrying work it should share with shape, position or annotation.

Plus the lightness profile of all colormaps together.

With colorspacious installed (pip install colorspacious) lightness is computed
in CAM02-UCS, which is perceptually correct, and simulations of deuteranopia,
protanopia and tritanopia are added. Without it, the sRGB -> luma approximation
is used, which is enough to catch the severe cases.
"""
from __future__ import annotations

import argparse
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

try:
    from colorspacious import cspace_convert
    HAS_CS = True
except ImportError:  # pragma: no cover
    HAS_CS = False

GOOD = {
    "sequential (positive, monotonic data)": ["viridis", "magma", "inferno",
                                              "cividis", "Blues", "YlOrRd"],
    "diverging (data that crosses zero)": ["RdBu_r", "coolwarm", "BrBG",
                                           "PuOr", "berlin"],
    "cyclic (angle, phase)": ["twilight", "twilight_shifted"],
    "qualitative (categories)": ["tab10", "Set2", "Dark2"],
}

DEFICIENCIES = [("deuteranomaly", "deuteranopia"),
                ("protanomaly", "protanopia"),
                ("tritanomaly", "tritanopia")]


def lightness(rgb: np.ndarray) -> np.ndarray:
    """Perceptual lightness (CAM02-UCS J\') with sRGB luma as fallback."""
    if HAS_CS:
        return cspace_convert(rgb, "sRGB1", "CAM02-UCS")[:, 0]
    return 100.0 * (0.2126 * rgb[:, 0] + 0.7152 * rgb[:, 1] + 0.0722 * rgb[:, 2])


def simulate(rgb: np.ndarray, kind: str, severity: int = 100) -> np.ndarray:
    if not HAS_CS:
        return rgb
    space = {"name": "sRGB1+CVD", "cvd_type": kind, "severity": severity}
    return np.clip(cspace_convert(rgb, space, "sRGB1"), 0, 1)


def ramp_test(n: int = 512, cycles: int = 40, amp: float = 0.045) -> np.ndarray:
    """Linear ramp with a superimposed sinusoidal ripple (Kovesi)."""
    x = np.linspace(0, 1, n)
    y = np.linspace(0, 1, 96)
    wobble = amp * np.sin(2 * np.pi * cycles * x) * y[:, None] ** 2
    return np.clip(x[None, :] + wobble, 0, 1)


def label(ax, text: str) -> None:
    ax.set_ylabel(text, rotation=0, ha="right", va="center",
                  fontsize=8, labelpad=8)


def report(names: list[str], out: str) -> None:
    ramp = ramp_test()
    grad = np.linspace(0, 1, 512)[None, :]

    per = 3 + (3 if HAS_CS else 0)
    nrows = len(names) * per + 1
    fig, axes = plt.subplots(
        nrows, 1, figsize=(9.5, 0.34 * nrows + 2.6),
        gridspec_kw={"hspace": 0.32, "left": 0.30, "right": 0.97,
                     "top": 0.90, "bottom": 0.07})
    axes = np.atleast_1d(axes)
    i = 0

    for name in names:
        try:
            cmap = plt.get_cmap(name)
        except ValueError:
            print(f"unknown colormap: {name}", file=sys.stderr)
            continue

        axes[i].imshow(grad, aspect="auto", cmap=cmap)
        label(axes[i], f"{name}\ncolor bar")
        i += 1

        axes[i].imshow(ramp, aspect="auto", cmap=cmap)
        label(axes[i], "ramp test")
        i += 1

        rgb = cmap(grad[0])[:, :3]
        gris = lightness(rgb)
        gris = (gris - gris.min()) / max(np.ptp(gris), 1e-9)
        axes[i].imshow(np.repeat(gris[None, :, None], 3, axis=2), aspect="auto")
        label(axes[i], "grayscale")
        i += 1

        if HAS_CS:
            for kind, etiqueta in DEFICIENCIES:
                sim = simulate(rgb, kind)
                axes[i].imshow(sim[None, :, :], aspect="auto")
                label(axes[i], etiqueta)
                i += 1

    for ax in axes[:i]:
        ax.set_xticks([])
        ax.set_yticks([])
    fig.suptitle("In the ramp test the ripples must stay equally visible "
                 "across the full width", fontsize=9, y=0.93)

    ax = axes[i]
    for name in names:
        try:
            cmap = plt.get_cmap(name)
        except ValueError:
            continue
        L = lightness(cmap(grad[0])[:, :3])
        ax.plot(grad[0], L, label=name, lw=1.6)
    ax.set_xlabel("position along the colormap")
    ax.set_ylabel("lightness", rotation=90, ha="center", va="bottom",
                  fontsize=8, labelpad=4)
    ax.set_title("Lightness profile: monotonic if sequential, "
                 "V-symmetric if diverging", loc="left", fontsize=8, pad=14)
    ax.legend(frameon=False, fontsize=8, ncol=min(len(names), 4))
    ax.spines[["top", "right"]].set_visible(False)

    for ax in axes[i + 1:]:
        ax.set_visible(False)

    fig.savefig(out, dpi=140, bbox_inches="tight")
    print(f"report written to {out}")
    if not HAS_CS:
        print("note: colorspacious not installed. `pip install colorspacious` "
              "adds perceptual lightness and color vision deficiency simulation.")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("names", nargs="*", default=["viridis"],
                    help="colormaps to diagnose")
    ap.add_argument("--out", default="colormap_report.png")
    ap.add_argument("--list-good", action="store_true",
                    help="list recommended colormaps by data type")
    args = ap.parse_args()

    if args.list_good:
        for category, cms in GOOD.items():
            print(f"\n{category}:")
            print("  " + ", ".join(cms))
        return 0

    report(args.names or ["viridis"], args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

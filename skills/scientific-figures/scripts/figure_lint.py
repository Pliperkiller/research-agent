#!/usr/bin/env python3
"""Audit matplotlib code against the scientific-figures rules.

Usage:
    python figure_lint.py figure.py
    python figure_lint.py analysis.ipynb
    python figure_lint.py src/*.py --json

This is static analysis: it never runs the code and never sees the data. That is
why some rules (R6 log scale, R7 single message, R10 caption) come out as manual
checks rather than automatic findings.
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

BAD_CMAPS = {
    "jet", "rainbow", "gist_rainbow", "nipy_spectral", "gist_ncar",
    "brg", "CMRmap", "flag", "prism",
}
CYCLIC_OK = {"hsv", "twilight", "twilight_shifted"}

FIELD_CALLS = {"imshow", "pcolormesh", "pcolor", "contourf", "matshow", "hexbin"}
COLORBAR_CALLS = {"colorbar"}


class Finding:
    def __init__(self, rule: str, line: int, message: str, hint: str = ""):
        self.rule, self.line, self.message, self.hint = rule, line, message, hint

    def as_dict(self):
        return {"rule": self.rule, "line": self.line,
                "message": self.message, "hint": self.hint}


def source_from(path: Path) -> str:
    """Return python source; for a notebook, concatenate the code cells."""
    if path.suffix == ".ipynb":
        nb = json.loads(path.read_text(encoding="utf-8"))
        cells = [
            "".join(c.get("source", []))
            for c in nb.get("cells", [])
            if c.get("cell_type") == "code"
        ]
        # magic lines break the parser
        clean = []
        for cell in cells:
            clean.append("\n".join(
                "" if ln.lstrip().startswith(("%", "!")) else ln
                for ln in cell.split("\n")
            ))
        return "\n\n".join(clean)
    return path.read_text(encoding="utf-8")


def call_name(node: ast.Call) -> str:
    f = node.func
    if isinstance(f, ast.Attribute):
        return f.attr
    if isinstance(f, ast.Name):
        return f.id
    return ""


def kwarg(node: ast.Call, name: str):
    for kw in node.keywords:
        if kw.arg == name:
            return kw.value
    return None


def const_str(node) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def analyze(src: str) -> tuple[list[Finding], dict]:
    try:
        tree = ast.parse(src)
    except SyntaxError as exc:
        return [Finding("PARSE", exc.lineno or 0, f"could not parse: {exc.msg}")], {}

    findings: list[Finding] = []
    seen = {
        "field": False, "colorbar": False, "xlabel": False, "ylabel": False,
        "bar": False, "ylim_on_bar": False, "style_use": False,
        "random": False, "seed": False, "savefig": False, "layout": False,
        "fontsize_inline": 0, "imshow": False, "show": False,
    }

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = call_name(node)
        line = getattr(node, "lineno", 0)

        # --- R2: banned colormaps ------------------------------------------
        cm = kwarg(node, "cmap") or kwarg(node, "colormap")
        cm_val = const_str(cm) if cm is not None else None
        if cm_val:
            base = cm_val.rstrip("_r")
            if base in BAD_CMAPS or (base in CYCLIC_OK and base == "hsv"):
                findings.append(Finding(
                    "R2", line,
                    f"colormap '{cm_val}' is not perceptually uniform",
                    "its lightness is not monotonic: it invents bands that are "
                    "not in the data and collapses in grayscale. Use "
                    "viridis/magma for positive data, RdBu_r if it crosses zero."
                    if base != "hsv" else
                    "hsv is only acceptable for strictly cyclic data; "
                    "for phase use twilight.",
                ))
        if name in ("get_cmap", "set_cmap"):
            for a in node.args:
                s = const_str(a)
                if s and s.rstrip("_r") in BAD_CMAPS:
                    findings.append(Finding(
                        "R2", line, f"colormap '{s}' is banned",
                        "see references/colormaps.md"))

        # --- R3 / R4: tracking ----------------------------------------------
        if name in FIELD_CALLS:
            seen["field"] = True
        if name in COLORBAR_CALLS:
            seen["colorbar"] = True
        if name in ("set_xlabel", "set_xlabel"):
            seen["xlabel"] = True
        if name == "xlabel":
            seen["xlabel"] = True
        if name in ("set_ylabel", "ylabel"):
            seen["ylabel"] = True

        # --- R4: imshow without origin/extent --------------------------------
        if name in ("imshow", "matshow"):
            seen["imshow"] = True
            if kwarg(node, "extent") is None:
                findings.append(Finding(
                    "R4", line, "imshow without extent",
                    "the axes stay as pixel indices. Pass "
                    "extent=[xmin, xmax, ymin, ymax] with the real coordinates."))
            origin = kwarg(node, "origin")
            if origin is None or const_str(origin) != "lower":
                findings.append(Finding(
                    "R4", line, "imshow without origin='lower'",
                    "by default row 0 is drawn at the top, which flips the field "
                    "relative to the Cartesian plane."))

        # --- R5: bar chart with truncated axis -------------------------------
        if name in ("bar", "barh"):
            seen["bar"] = True
        if name in ("set_ylim", "ylim") and seen["bar"]:
            bottom = node.args[0] if node.args else kwarg(node, "bottom")
            if isinstance(bottom, ast.Constant) and bottom.value not in (0, 0.0):
                seen["ylim_on_bar"] = True
                findings.append(Finding(
                    "R5", line,
                    f"bar chart y axis truncated at {bottom.value}",
                    "bars encode magnitude by area; truncating exaggerates small "
                    "differences. If the useful range is narrow, use points or a "
                    "difference chart."))

        # --- R8: chartjunk ---------------------------------------------------
        if name == "pie":
            findings.append(Finding(
                "R8", line, "pie chart",
                "the eye compares angles poorly. Use sorted bars."))
        if name == "set_facecolor":
            arg = node.args[0] if node.args else None
            s = const_str(arg)
            if s and s not in ("white", "w", "none", "#ffffff", "#FFFFFF"):
                findings.append(Finding(
                    "R8", line, f"colored background '{s}'",
                    "the background encodes no information."))
        if name == "grid":
            if node.args and isinstance(node.args[0], ast.Constant) and node.args[0].value is True:
                if kwarg(node, "alpha") is None and kwarg(node, "lw") is None \
                        and kwarg(node, "linewidth") is None:
                    findings.append(Finding(
                        "R8", line, "grid not muted",
                        "if you use one, keep it behind the data: "
                        "grid(True, alpha=0.3, linewidth=0.5)."))
        if name == "bar3d" or (name == "add_subplot" and
                               any(const_str(kwarg(node, "projection")) == "3d" for _ in [0])):
            pass

        # --- R9: reproducibility ---------------------------------------------
        if name in ("rand", "randn", "normal", "uniform", "choice",
                    "random", "randint", "permutation", "shuffle"):
            seen["random"] = True
        if name in ("seed", "default_rng", "RandomState"):
            seen["seed"] = True

        # --- output ----------------------------------------------------------
        if name == "savefig":
            seen["savefig"] = True
            target = node.args[0] if node.args else None
            s = const_str(target)
            if s and s.lower().endswith((".jpg", ".jpeg")):
                findings.append(Finding(
                    "OUT", line, "JPG output",
                    "compression artifacts ruin lines and text. "
                    "PDF if vector, PNG if raster."))
        if name == "show":
            seen["show"] = True
        if name in ("tight_layout", "set_layout_engine"):
            seen["layout"] = True
        if name == "style" or (name == "use" and isinstance(node.func, ast.Attribute)
                               and getattr(node.func.value, "attr", "") == "style"):
            seen["style_use"] = True

        # hardcoded fontsize
        if kwarg(node, "fontsize") is not None:
            seen["fontsize_inline"] += 1

    # ---- file-level rules ---------------------------------------------------
    if seen["field"] and not seen["colorbar"]:
        findings.append(Finding(
            "R3", 0, "color-to-value mapping without a colorbar",
            "without one, color carries no quantitative meaning. "
            "Add it with a label and units."))
    if not seen["xlabel"]:
        findings.append(Finding(
            "R4", 0, "missing x axis label",
            "ax.set_xlabel('Distance [km]') - with units."))
    if not seen["ylabel"]:
        findings.append(Finding(
            "R4", 0, "missing y axis label",
            "ax.set_ylabel('Temperature [C]') - with units."))
    if seen["random"] and not seen["seed"]:
        findings.append(Finding(
            "R9", 0, "randomness without a fixed seed",
            "rng = np.random.default_rng(0) - otherwise the figure will not "
            "regenerate identically."))
    if not seen["style_use"]:
        findings.append(Finding(
            "R-STYLE", 0, "no style sheet loaded",
            "plt.style.use('paper-2col.mplstyle') - sizes come from the medium, "
            "not from the defaults."))
    if seen["fontsize_inline"] >= 3:
        findings.append(Finding(
            "R-STYLE", 0,
            f"fontsize hardcoded {seen['fontsize_inline']} times",
            "move sizes into the style sheet; then the same figure serves paper "
            "and slide by changing one line."))
    if seen["savefig"] and not seen["layout"] and "constrained" not in "":
        pass
    if not seen["savefig"] and not seen["show"]:
        findings.append(Finding(
            "OUT", 0, "the figure is neither saved nor shown", ""))

    manual = [
        "R1  the colormap matches the data structure (sign, range, cyclicity)",
        "R6  if the data spans orders of magnitude, LogNorm or a declared log scale is used",
        "R7  the figure communicates a single message",
        "R10 the caption is written and delivered",
        "    comparable panels share limits and color norm",
        "    points of interest are annotated",
    ]
    return findings, {"manual": manual, "seen": seen}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--json", action="store_true", help="JSON output")
    ap.add_argument("--strict", action="store_true",
                    help="exit code 1 when there are findings")
    args = ap.parse_args()

    total = 0
    payload = {}
    for p in args.paths:
        path = Path(p)
        if not path.exists():
            print(f"not found: {p}", file=sys.stderr)
            continue
        findings, extra = analyze(source_from(path))
        total += len(findings)
        payload[p] = [f.as_dict() for f in findings]

        if args.json:
            continue
        print(f"\n=== {p} ===")
        if not findings:
            print("  no automatic findings")
        for f in sorted(findings, key=lambda x: (x.rule, x.line)):
            loc = f"L{f.line}" if f.line else "file"
            print(f"  [{f.rule}] {loc}: {f.message}")
            if f.hint:
                for ln in f.hint.split("\n"):
                    print(f"         {ln}")
        print("\n  manual checks (the linter cannot decide these):")
        for m in extra["manual"]:
            print(f"    - {m}")

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 1 if (args.strict and total) else 0


if __name__ == "__main__":
    raise SystemExit(main())

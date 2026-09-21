#!/usr/bin/env python3
"""Audit scientific Python against the scientific-code rules.

Usage:
    python code_style_lint.py analysis.py
    python code_style_lint.py notebook.ipynb
    python code_style_lint.py src/*.py --json

This is static analysis over the source text: it never runs the code, never
sees the data, and cannot judge whether a comment is true or a name is apt.
Language detection is a curated word-list heuristic, not a language model: it
is tuned for near-zero false positives and accepts a high false-negative rate,
so a clean run is not proof that every identifier is English. R1 and R5 lean on
blocklists that are a hand-synced subset of assets/naming-glossary.md. Import
aliases (np, plt, pd) are never flagged, since they are universal convention.
Whatever it cannot decide is printed as a manual check rather than dropped.
"""
from __future__ import annotations

import argparse
import ast
import io
import json
import keyword
import re
import sys
import tokenize
from collections import Counter
from pathlib import Path

# --- R1: names -------------------------------------------------------------
# Two characters or fewer is unreadable unless the name is one of these: `_`
# means "deliberately unused", and `ax` is the matplotlib idiom the sibling
# scientific-figures skill uses in every example.
ALLOWED_SHORT = {"_", "ax"}

# Invented contractions, mapped to what to write instead. Established domain
# acronyms (rms, fft, pde, mse, cfl) are deliberately absent: those are legible
# to any reader in the field, which is the test R1 actually applies.
BAD_WORDS = {
    "tmp": "the thing it holds", "temp": "temperature_* or the thing it holds",
    "res": "result or residual, spelled out", "val": "value", "vals": "values",
    "arr": "values, samples, or the quantity itself", "aux": "the helper's job",
    "dat": "data, or better, which data", "lst": "the content of the list",
    "dct": "mapping, keyed by what", "cnt": "count or n_*", "idx": "*_index",
    "lam": "penalty_weight or wavelength_meters", "lr": "learning_rate",
    "bs": "batch_size", "calc": "compute_*", "proc": "process_*",
    "coef": "coefficient", "pts": "points", "vec": "vector", "mat": "matrix",
    "sol": "solution", "prm": "parameter", "curr": "current", "prev": "previous",
    "err": "absolute_error or relative_error", "freq": "frequency_hertz",
    "cfg": "configuration", "conf": "configuration", "fname": "input_path",
    "acc": "accumulator, or the quantity being accumulated",
}

# u0, x1, t2, data3: a stem with a number glued on is a name that gave up.
NUMBERED_STEM = re.compile(r"^[a-z_]{1,4}\d+$")

# --- R2: language ----------------------------------------------------------
# Function words carry the signal for language detection: they are frequent,
# short, and almost never appear as domain vocabulary in the other language.
SPANISH_STOPWORDS = {
    "que", "de", "la", "el", "los", "las", "un", "una", "para", "con", "por",
    "del", "se", "es", "son", "como", "sobre", "este", "esta", "estos", "cada",
    "donde", "cuando", "pero", "porque", "desde", "hasta", "entre", "lo", "al",
    "su", "sus", "ya", "tambien", "aqui", "asi", "hay", "sin", "mas", "muy",
    "todo", "todos", "ahora", "luego", "antes", "despues", "mismo", "otra",
    "otro", "nos", "les", "le", "ser", "esto", "eso", "si", "no",
}
ENGLISH_STOPWORDS = {
    "the", "this", "that", "these", "those", "is", "are", "was", "were", "of",
    "and", "but", "because", "since", "with", "from", "why", "we", "it", "its",
    "not", "which", "here", "there", "when", "would", "only", "each", "every",
    "into", "without", "then", "than", "them", "they", "for", "must", "should",
    "does", "do", "so", "if", "at", "on", "in", "by", "to", "as", "be",
}
# Domain words with NO English homograph. Words like error, final, total, real,
# normal, area, base, control, general, actual, radio, gas, metal and principal
# are excluded ON PURPOSE: they are spelled the same in English and would turn
# this into a false-positive machine.
SPANISH_WORDS = {
    "datos", "valor", "valores", "archivo", "archivos", "tiempo", "paso",
    "pasos", "malla", "nodo", "nodos", "frontera", "borde", "bordes", "salida",
    "entrada", "resultado", "resultados", "calculo", "calcular", "calcula",
    "ejecutar", "grafico", "grafica", "ruta", "longitud", "ancho", "alto",
    "muestra", "muestras", "prueba", "promedio", "suma", "resta", "cantidad",
    "tamano", "numero", "punto", "puntos", "campo", "onda", "fuerza", "masa",
    "velocidad", "peso", "altura", "anchura", "inicio", "siguiente", "anterior",
    "actualizar", "guardar", "cargar", "limpiar", "contador", "iteracion",
    "semilla", "ajuste", "perdida", "devuelve", "recibe", "entonces",
    "normalizamos", "normalizar", "arreglo", "corre", "corrida",
}
ENGLISH_WORDS = {
    "value", "values", "data", "file", "files", "time", "step", "steps",
    "mesh", "grid", "node", "nodes", "boundary", "output", "input", "result",
    "results", "compute", "run", "plot", "path", "length", "width", "height",
    "sample", "samples", "test", "mean", "sum", "count", "size", "number",
    "point", "points", "field", "wave", "force", "mass", "speed", "weight",
    "start", "next", "previous", "update", "save", "load", "clear", "counter",
    "iteration", "seed", "fit", "loss", "returns", "return", "keeps", "stays",
}
ACCENTED = set("áéíóúñü¿¡")
LANGUAGE_MARKER = re.compile(r"^\s*comment[-\s]language\s*:\s*([a-z]{2})\b", re.I)

# --- R5: units -------------------------------------------------------------
# A quantity whose unit the reader cannot guess. Dimensionless quantities
# (count, index, ratio, factor) are absent on purpose.
QUANTITY_STEMS = {
    "time", "timestep", "duration", "delay", "period", "length", "width",
    "height", "depth", "distance", "radius", "diameter", "position", "mass",
    "weight", "temperature", "pressure", "energy", "power", "force",
    "velocity", "speed", "acceleration", "frequency", "wavelength", "angle",
    "voltage", "charge", "density", "volume", "spacing", "dt", "dx",
}
UNIT_SUFFIXES = {
    "seconds", "second", "ms", "milliseconds", "minutes", "hours", "days",
    "meters", "metres", "mm", "cm", "km", "m", "kelvin", "celsius",
    "fahrenheit", "kg", "kilograms", "grams", "joules", "watts", "newtons",
    "pascals", "bar", "hz", "hertz", "khz", "radians", "degrees", "percent",
    "fraction", "volts", "amperes", "coulombs", "steps", "samples", "pixels",
}

# --- R6: literals ----------------------------------------------------------
# Identity elements, array bookkeeping and percentages: these carry their
# meaning on their face and naming them would add noise, not information.
ALLOWED_LITERALS = {0, 1, 2, 3, -1, -2, 0.0, 0.5, 1.0, 2.0, -1.0, 100}

# --- R3: decisions that must say why ---------------------------------------
# Calls that silently change what is being computed or optimised. Every one of
# them is a modelling decision wearing the clothes of a utility call.
DECISION_MARKERS = {
    "detach", "clip", "clamp", "no_grad", "astype", "reshape", "squeeze",
    "flatten", "sign", "seed", "transpose", "flip", "roll", "where",
    "maximum", "minimum", "nan_to_num", "requires_grad_", "manual_seed",
}

MAX_FUNCTION_LINES = 50
MIN_LINES_FOR_DENSITY = 20
COMMENT_DENSITY_FLOOR = 10          # at least one comment per ten logical lines
MUTE_FUNCTION_STATEMENTS = 10       # statements a function may hold in silence
FLAT_SCRIPT_STATEMENTS = 60         # top-level statements with no function at all
SMALL_FLOAT = 1e-3                  # below this, a float is a tolerance, not a value
DOCSTRING_MIN_WORDS = 5             # below this there is no signal to judge language on
DOCSTRING_LANGUAGE_THRESHOLD = 3    # stricter than comments: a docstring is public


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


def split_identifier(name: str) -> list[str]:
    """Break an identifier into lowercase words: snake_case, camelCase, digits."""
    spaced = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", name)
    parts = re.split(r"[^A-Za-z0-9]+", spaced)
    words = []
    for part in parts:
        # split a trailing or embedded number off its stem: m2 -> m, 2
        for chunk in re.findall(r"[A-Za-z]+|\d+", part):
            if chunk:
                words.append(chunk.lower())
    return words


def language_of(text: str, threshold: int = 2) -> str:
    """Classify a short piece of prose as 'es', 'en' or 'unknown'.

    Deliberately conservative: a single shared word never decides. Accents add
    weight but never reach the threshold alone, so 'Poincare' spelled properly
    inside an English sentence does not make it Spanish. The threshold rises
    for docstrings, where a false positive would be louder than a miss.
    """
    words = set(re.findall(r"[a-záéíóúñü]+", text.lower()))
    if not words:
        return "unknown"
    spanish_score = len(words & (SPANISH_STOPWORDS | SPANISH_WORDS))
    english_score = len(words & (ENGLISH_STOPWORDS | ENGLISH_WORDS))
    if any(ch in ACCENTED for ch in text.lower()):
        spanish_score += 2
    if spanish_score >= threshold and spanish_score > english_score:
        return "es"
    if english_score >= threshold and english_score > spanish_score:
        return "en"
    return "unknown"


def comments_of(src: str) -> list[tuple[int, str, bool]]:
    """Every comment as (line, text without '#', is_trailing)."""
    out: list[tuple[int, str, bool]] = []
    lines = src.split("\n")
    try:
        for token in tokenize.generate_tokens(io.StringIO(src).readline):
            if token.type != tokenize.COMMENT:
                continue
            line_number, column = token.start
            physical = lines[line_number - 1] if line_number <= len(lines) else ""
            trailing = bool(physical[:column].strip())
            out.append((line_number, token.string.lstrip("#").strip(), trailing))
    except (tokenize.TokenError, IndentationError):
        # tokenize gives up on a truncated file; ast.parse already succeeded,
        # so whatever we collected before the failure is still usable.
        pass
    return out


def logical_lines(src: str) -> int:
    """Count logical code lines, which is what comment density is relative to."""
    total = 0
    try:
        for token in tokenize.generate_tokens(io.StringIO(src).readline):
            if token.type == tokenize.NEWLINE:
                total += 1
    except (tokenize.TokenError, IndentationError):
        pass
    return total


def code_words_by_line(src: str) -> dict[int, set[str]]:
    """Words appearing inside identifiers, indexed by line, for R3 restatement."""
    per_line: dict[int, set[str]] = {}
    try:
        for token in tokenize.generate_tokens(io.StringIO(src).readline):
            if token.type != tokenize.NAME:
                continue
            per_line.setdefault(token.start[0], set()).update(
                split_identifier(token.string))
    except (tokenize.TokenError, IndentationError):
        pass
    return per_line


def is_public(name: str) -> bool:
    return not name.startswith("_")


def is_dunder(name: str) -> bool:
    return name.startswith("__") and name.endswith("__")


def bound_names(tree: ast.AST) -> list[tuple[str, int]]:
    """Names the file introduces: definitions, parameters and assignments.

    Import aliases are excluded: `import numpy as np` is universal convention,
    and flagging it would drown every real finding.
    """
    found: list[tuple[str, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            found.append((node.name, node.lineno))
        elif isinstance(node, ast.arg):
            if node.arg not in ("self", "cls"):
                found.append((node.arg, node.lineno))
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            found.append((node.id, node.lineno))
    return found


def public_definitions(tree: ast.Module) -> list[ast.AST]:
    """Top-level functions plus methods, which is what 'public' means for R4."""
    definitions = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            definitions.append(node)
        elif isinstance(node, ast.ClassDef):
            for inner in node.body:
                if isinstance(inner, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    definitions.append(inner)
    return definitions


def looks_like_code(text: str) -> bool:
    """True when a comment body is commented-out code rather than prose."""
    if len(text) < 6 or text.lower().startswith(
            ("type:", "noqa", "pylint", "comment-language", "!", "%", "-")):
        return False
    first = text.split()[0] if text.split() else ""
    if not ("=" in text or "(" in text or first in keyword.kwlist):
        return False
    try:
        ast.parse(text)
    except SyntaxError:
        return False
    return True


def constants_of_named_assignments(tree: ast.Module) -> set[int]:
    """Ids of literals that already live in a MODULE_LEVEL_CONSTANT, exempt from R6."""
    exempt: set[int] = set()
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        targets_are_constants = all(
            isinstance(target, ast.Name) and target.id.isupper()
            for target in node.targets)
        if targets_are_constants:
            for inner in ast.walk(node.value):
                if isinstance(inner, ast.Constant):
                    exempt.add(id(inner))
    return exempt


def analyze(src: str) -> tuple[list[Finding], dict]:
    try:
        tree = ast.parse(src)
    except SyntaxError as exc:
        return [Finding("PARSE", exc.lineno or 0, f"could not parse: {exc.msg}")], {}

    findings: list[Finding] = []
    comments = comments_of(src)
    code_words = code_words_by_line(src)
    n_code_lines = logical_lines(src)
    commented_lines = {line for line, _, _ in comments}
    declared_language = None
    for _, text, _ in comments:
        match = LANGUAGE_MARKER.match(text)
        if match:
            declared_language = match.group(1).lower()
            break

    # ---- comment pass: R2 language, R3 restatement and density, DEAD code ----
    language_counts: Counter = Counter()
    first_line_of_language: dict[str, int] = {}
    for line, text, _ in comments:
        if LANGUAGE_MARKER.match(text):
            continue
        if looks_like_code(text):
            findings.append(Finding(
                "DEAD", line, "commented-out code",
                "git already remembers it. Left here, the reader cannot tell "
                "whether it is about to be restored."))
            continue
        language = language_of(text)
        if language != "unknown":
            language_counts[language] += 1
            first_line_of_language.setdefault(language, line)

        # R3: a comment that restates the line under it carries no information.
        words_in_comment = {
            word for word in re.findall(r"[a-záéíóúñü]+", text.lower())
            if len(word) > 2 and word not in SPANISH_STOPWORDS
            and word not in ENGLISH_STOPWORDS}
        next_code = code_words.get(line + 1, set())
        if len(words_in_comment) >= 2 and words_in_comment <= next_code:
            findings.append(Finding(
                "R3", line, "the comment restates the line below it",
                "say WHY the line exists, not what it does. The code already "
                "says what it does."))

    if declared_language:
        off_language = [lang for lang in language_counts if lang != declared_language]
        for language in off_language:
            findings.append(Finding(
                "R2", first_line_of_language[language],
                f"comment in '{language}' but the file declares "
                f"'{declared_language}'",
                "one language per file. The marker is the contract; either "
                "translate the comment or change the marker."))
    elif len(language_counts) >= 2 and min(language_counts.values()) >= 2:
        minority = min(language_counts, key=lambda lang: language_counts[lang])
        findings.append(Finding(
            "R2", first_line_of_language[minority],
            "comments mix languages "
            f"({dict(language_counts)})",
            "pick one and declare it with '# comment-language: xx' near the "
            "top of the file."))

    # ---- docstring pass: R2 requires English, whatever the comment language --
    documented_nodes = [tree] + [
        node for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
    for node in documented_nodes:
        docstring = ast.get_docstring(node)
        if not docstring:
            continue
        # Short docstrings are left alone: under five words there is not enough
        # signal to accuse anyone, and a wrong accusation is worse than a miss.
        if len(docstring.split()) < DOCSTRING_MIN_WORDS:
            continue
        if language_of(docstring, DOCSTRING_LANGUAGE_THRESHOLD) == "es":
            where = getattr(node, "name", "module")
            findings.append(Finding(
                "R2", getattr(node, "lineno", 0),
                f"docstring of '{where}' is not in English",
                "the docstring is part of the interface, and the interface "
                "travels. Comments may stay in the working language; this "
                "cannot."))

    # ---- name pass: R1 and R2 on identifiers --------------------------------
    for name, line in bound_names(tree):
        if is_dunder(name):
            continue
        if len(name) <= 2 and name not in ALLOWED_SHORT:
            findings.append(Finding(
                "R1", line, f"name '{name}' is too short to read",
                "the reader has no access to the derivation where it meant "
                "something. See assets/naming-glossary.md."))
            continue
        if NUMBERED_STEM.fullmatch(name):
            findings.append(Finding(
                "R1", line, f"name '{name}' is a stem with a number glued on",
                "u0 -> initial_condition, x1 -> first_position. The number is "
                "doing the work a word should do."))
        words = split_identifier(name)
        for word in words:
            if word in BAD_WORDS:
                findings.append(Finding(
                    "R1", line,
                    f"name '{name}' contains the abbreviation '{word}'",
                    f"write {BAD_WORDS[word]} instead. An invented contraction "
                    "is legible only to whoever chose it."))
                break
        spanish_in_name = [word for word in words if word in SPANISH_WORDS]
        if spanish_in_name:
            findings.append(Finding(
                "R2", line,
                f"identifier '{name}' is not in English "
                f"('{spanish_in_name[0]}')",
                "identifiers travel: they land in papers, issues and threads "
                "with collaborators. If this word is English, the blocklist is "
                "wrong - it is hand-curated, not a detector."))

    # ---- AST pass: R3 decisions, R4 interface, R5 units, R6 literals, R7 size
    literal_counts: Counter = Counter()
    literal_lines: dict[object, list[int]] = {}
    exempt_literals = constants_of_named_assignments(tree)

    for node in ast.walk(tree):
        line = getattr(node, "lineno", 0)

        # --- R3: a decision with no comment beside it ------------------------
        if isinstance(node, ast.Call):
            name = ""
            if isinstance(node.func, ast.Attribute):
                name = node.func.attr
            elif isinstance(node.func, ast.Name):
                name = node.func.id
            if name in DECISION_MARKERS and not (
                    commented_lines & {line - 2, line - 1, line}):
                findings.append(Finding(
                    "R3", line, f"'{name}' with no comment saying why",
                    "this call changes what is being computed and nothing in "
                    "the diff will show it. One line on the intent."))

        # --- R5: quantities carry their unit ---------------------------------
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant) \
                and isinstance(node.value.value, (int, float)) \
                and not isinstance(node.value.value, bool):
            for target in node.targets:
                if not isinstance(target, ast.Name):
                    continue
                words = split_identifier(target.id)
                has_quantity = any(word in QUANTITY_STEMS for word in words)
                has_unit = bool(words) and words[-1] in UNIT_SUFFIXES
                trailing_unit = any(
                    other_line == line and "[" in text
                    for other_line, text, trailing in comments if trailing)
                if has_quantity and not has_unit and not trailing_unit:
                    findings.append(Finding(
                        "R5", line,
                        f"'{target.id}' is a physical quantity with no unit",
                        "timestep_seconds, rod_length_meters. Unit mismatches "
                        "do not crash: the program runs and is wrong."))

        # --- R6: magic literals ----------------------------------------------
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) \
                and not isinstance(node.value, bool) and id(node) not in exempt_literals:
            literal_counts[node.value] += 1
            literal_lines.setdefault(node.value, []).append(line)

        if isinstance(node, ast.Compare):
            for operand in node.comparators:
                if isinstance(operand, ast.Constant) \
                        and isinstance(operand.value, (int, float)) \
                        and not isinstance(operand.value, bool) \
                        and operand.value not in ALLOWED_LITERALS:
                    findings.append(Finding(
                        "R6", line,
                        f"the literal {operand.value!r} decides a branch",
                        "promote it to a named module-level constant; then the "
                        "comment explaining the choice has somewhere to live."))

        # --- R4 and R7: functions --------------------------------------------
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            span = (node.end_lineno or node.lineno) - node.lineno + 1
            if span > MAX_FUNCTION_LINES:
                findings.append(Finding(
                    "R7", node.lineno,
                    f"function '{node.name}' is {span} lines",
                    f"the ceiling is {MAX_FUNCTION_LINES}. It is almost never "
                    "irreducible: it is three named steps never given names."))
            statements = sum(1 for inner in ast.walk(node)
                             if isinstance(inner, ast.stmt))
            comments_inside = sum(
                1 for line_number, _, _ in comments
                if node.lineno <= line_number <= (node.end_lineno or node.lineno))
            if statements >= MUTE_FUNCTION_STATEMENTS and comments_inside == 0:
                findings.append(Finding(
                    "R3", node.lineno,
                    f"function '{node.name}' has {statements} statements and "
                    "no comment",
                    "a comment you can delete is cheaper than one you needed "
                    "and did not write."))

    for definition in public_definitions(tree):
        if not is_public(definition.name):
            continue
        docstring = ast.get_docstring(definition)
        if not docstring or len(docstring.strip()) < 10:
            findings.append(Finding(
                "R4", definition.lineno,
                f"public function '{definition.name}' has no usable docstring",
                "say what it returns and in which units. Without it the only "
                "way to call it is to read the body."))
        if definition.returns is None:
            findings.append(Finding(
                "R4", definition.lineno,
                f"'{definition.name}' has no return annotation",
                "-> None included. It is what tells the reader whether the "
                "function computes something or mutates something."))
        arguments = (definition.args.posonlyargs + definition.args.args
                     + definition.args.kwonlyargs)
        for argument in arguments:
            if argument.arg in ("self", "cls"):
                continue
            if argument.annotation is None:
                findings.append(Finding(
                    "R4", definition.lineno,
                    f"'{definition.name}': parameter '{argument.arg}' is not "
                    "annotated",
                    "the annotation says what goes in; the name says which "
                    "quantity; the docstring says the shape."))
    # ---- file-level rules ---------------------------------------------------
    for value, count in literal_counts.items():
        if value in ALLOWED_LITERALS or count < 2:
            continue
        findings.append(Finding(
            "R6", literal_lines[value][1],
            f"the literal {value!r} appears {count} times",
            "a repeated magic number is a bug waiting to happen: someone will "
            "tune one of the copies. Name it once."))

    if n_code_lines >= MIN_LINES_FOR_DENSITY and \
            len(comments) < n_code_lines / COMMENT_DENSITY_FLOOR:
        findings.append(Finding(
            "R3", 0,
            f"{len(comments)} comments over {n_code_lines} logical lines",
            f"the floor is one per {COMMENT_DENSITY_FLOOR}. Under-commenting "
            "is the expensive failure; over-commenting costs two seconds to "
            "delete."))

    if not ast.get_docstring(tree):
        findings.append(Finding(
            "R-DECL", 0, "no module docstring",
            "purpose, inputs, outputs and the unit convention. Start from "
            "assets/script-header.py."))
    if len(comments) >= 3 and declared_language is None:
        findings.append(Finding(
            "R-DECL", 0, "comment language is never declared",
            "add '# comment-language: xx' near the top. The marker is what "
            "makes R2 checkable instead of a preference."))

    top_level_statements = sum(1 for node in tree.body if isinstance(node, ast.stmt))
    has_functions = any(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                        for node in tree.body)
    if top_level_statements >= FLAT_SCRIPT_STATEMENTS and not has_functions:
        findings.append(Finding(
            "R7", 0,
            f"{top_level_statements} top-level statements and no function",
            "the script is one flat block. Named steps are also where the WHY "
            "comments find their place."))

    manual = [
        "R1  each name reads as prose in the sentence where it is used",
        "R2  identifiers are English beyond the curated blocklist (high false-negative rate)",
        "R2  user-facing strings and log messages are not inspected at all",
        "R3  the comments explain WHY, and what they say is true",
        "R4  the docstring describes the contract and the array shapes, not the body",
        "R5  the unit written in the name is the unit the value actually carries",
        "R6  the named constant is named after its meaning, not after its value",
        "    one concept carries one name across the whole file",
    ]
    return findings, {"manual": manual,
                      "declared_language": declared_language,
                      "n_code_lines": n_code_lines,
                      "n_comments": len(comments)}


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

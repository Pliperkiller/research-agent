# Adding a skill to research-agent

Every skill here covers one **deliverable**, not one library. The unit is "a
figure", "a notebook", "a paper" — something the user ends up with.

## Layout

```
skills/<skill-name>/
├── SKILL.md            required: workflow + hard rules
├── references/         loaded only when relevant
│   ├── <topic>.md
│   └── checklist.md    the audit pass
├── assets/             loadable conventions: style sheets, templates
└── scripts/            deterministic checks
```

## SKILL.md frontmatter

```yaml
---
name: skill-name
description: What it does, plus explicit triggers. Agents under-trigger skills,
  so be pushy: name the phrasings a user actually types, including the casual
  ones ("just plot this", "write this up"), and say ALWAYS where it applies.
---
```

The description is the only thing always in context. It is what decides whether
the skill fires at all, so it carries the triggering burden. Keep the body under
about 500 lines and push detail into `references/`.

## The four-step shape

Keep the same workflow as `scientific-figures`, since consistency across skills
is what makes the plugin feel like one thing:

1. **Declare** — a short block the agent emits before producing anything:
   what the artifact is, the audience, the medium, the single message. If the
   agent cannot fill a field, it inspects first and asks at most one question.
2. **Apply the convention** — load a style sheet, template or structure from
   `assets/`. Prefer something loadable over prose.
3. **Build** — following the relevant `references/` file.
4. **Audit** — run the scripts, walk `references/checklist.md`, and report which
   rules applied and which did not.

## Writing the rules

- A rule must be checkable. If nobody can tell whether it was followed, it is a
  preference — say so and move it out of the hard-rule list.
- Explain *why*, briefly. A rule the agent understands survives edge cases; a
  bare imperative does not.
- Number them (R1, R2, ...) and use the same ids in the checklist and in the
  linter output, so a finding traces back to its justification.
- Prefer the imperative, and keep examples short and runnable.

## Scripts

Anything mechanical belongs in a script, not in the agent's memory. Static
analysis over the produced artifact is the most useful form: it runs fast, needs
no data, and gives the same answer every time. State clearly in the script's
docstring what it *cannot* check, and surface those as manual checks in its
output — an audit that pretends to be complete is worse than one that admits its
limits.

## Before committing

```bash
python scripts/validate.py
```

Checks the manifests, the skill frontmatter, and runs every linter against its
known-good and known-bad fixtures. A skill that ships a linter adds its row to
`LINTER_FIXTURES` in that file, so the CI proves the linter still fires and
still clears.

## A known gap

The plugin's own tooling is not audited by `scientific-code`. `validate.py` and
`figure_lint.py` use names like `p`, `fm`, `mk` and `kw`, and their helpers are
not annotated. The linters run against their fixtures only, never against the
repository. Cleaning that up is a separate change, and pretending otherwise
would turn every skill PR into a refactor.

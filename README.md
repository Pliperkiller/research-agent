# research-agent

A Claude Code plugin that teaches a coding agent to produce **scientific research
output** — figures, notebooks, papers, slides and analysis scripts — according to
explicit, verifiable rules instead of defaults.

It is not a library tutorial. The agent already knows matplotlib's API and LaTeX
syntax. What it lacks is judgment: which colormap the data calls for, when a
truncated axis becomes a lie, what belongs in a caption, how a notebook stays
reproducible six months later. This plugin encodes that judgment.

## Install

```
/plugin marketplace add pliperkiller/research-agent
/plugin install research-agent@pliperkiller-marketplace
```

To try it locally before publishing, from the directory that contains this repo:

```
/plugin marketplace add ./research-agent
/plugin install research-agent@pliperkiller-marketplace
```

For a team or a project to get it automatically, add to the project's
`.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "pliperkiller": {
      "source": { "source": "github", "repo": "pliperkiller/research-agent" }
    }
  }
}
```

The repository is both the marketplace catalog and the plugin itself, which is
why the plugin source in `marketplace.json` is `./`.

## Design principle

Every skill in this plugin follows the same shape, so the agent behaves
consistently no matter which deliverable it is producing:

1. **Declare before producing.** The agent states what the artifact is, who reads
   it, and what single message it must carry. Skipping this is what makes an
   agent reach for defaults.
2. **Apply the convention for the medium.** A style sheet, a template, a
   structure — something loadable, not a paragraph of advice. "Do not trust the
   defaults" is unactionable; `plt.style.use('paper-2col.mplstyle')` is not.
3. **Build.**
4. **Audit against a checklist**, and report which rules were applied and which
   did not apply. A rule that cannot be checked is a preference, not a rule.

Rules live in `references/`, loaded only when relevant. Anything mechanical is a
script under `scripts/`, so the check is deterministic rather than a matter of
the agent remembering.

## Skills

### scientific-figures — available

Correct figures with matplotlib: 2D scalar fields, vector fields, statistical
and tabular charts, and LaTeX export.

Ten hard rules (colormap derived from the data structure, no `jet`, colorbar on
every color-value mapping, labeled axes with units, no truncated bar axes, log
scale when the range demands it, one message per figure, no chartjunk,
reproducible, always shipped with a caption), four style sheets
(`paper-1col`, `paper-2col`, `slide`, `notebook`), and two verification scripts:

- `figure_lint.py` — static AST analysis of the figure code against the rules.
- `check_colormap.py` — lightness profile, Kovesi ramp test, and simulation of
  deuteranopia, protanopia and tritanopia.

Plus the `/audit-figure` command to review a figure that already exists.

### Planned

| Skill | Scope |
|---|---|
| `research-notebooks` | notebook structure: markdown before code, formulas before implementation, no hidden state, a notebook that runs top to bottom on a clean kernel |
| `paper-writing` | paper and article structure, claim-evidence discipline, citation hygiene, what belongs in each section |
| `research-slides` | talks and defenses: one idea per slide, figures re-rendered for the medium, no walls of text |
| `analysis-scripts` | reproducible analysis: seeds, pinned environments, data paths, separating computation from presentation |

See `docs/adding-a-skill.md` for the shape a new skill must follow.

## Optional dependency

```
pip install colorspacious
```

Enables perceptual lightness (CAM02-UCS) and color vision deficiency simulation
in `check_colormap.py`. Without it the script falls back to an sRGB luma
approximation, which still catches the severe cases.

## Where the rules come from

Distilled from the Scientific Programming course at Universidad Nacional de
Colombia, Medellín (Manuela Bastidas Olivares), which draws on Rougier,
Droettboom & Bourne (2014), Kovesi (2015), Tufte (1983), Anscombe (1973), and
Matejka & Fitzmaurice (2017).

## License

MIT

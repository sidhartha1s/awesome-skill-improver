# awesome-skill-improver

A Claude Code skill for iteratively improving any skill through hypothesis-driven experimentation.

Inspired by [karpathy/autoresearch](https://github.com/karpathy/autoresearch) and [browserbase/autobrowse](https://skills.sh/browserbase/skills/autobrowse).

## Core Philosophy

1. **Single-variable testing** - Change ONE thing per iteration so you know what worked
2. **Measurable outcomes** - If you can't measure it, you can't improve it
3. **Git-based safety** - Checkpoint before every experiment, rollback on failure
4. **Accumulated learning** - Heuristics persist across sessions, failures teach
5. **Nothing hardcoded** - All metrics and targets come from the user at runtime

## Usage

```
/skill-improver init --skill <name>    # Discover metrics, set goals, create workspace
/skill-improver run [--iterations N]   # Run N improvement iterations
/skill-improver status                 # Show progress toward goals
/skill-improver graduate               # Apply accepted changes, run /simplify
/skill-improver reset                  # Discard all changes, restore baseline
```

## How It Works

1. **Initialize** - Auto-discovers metrics from skill output, asks user for optimization targets
2. **Generate Hypothesis** - Proposes ONE change per iteration based on accumulated learnings
3. **Execute Experiment** - Git checkpoint, apply change, run skill, capture metrics
4. **Evaluate** - Compare before/after, detect regressions on secondary metrics
5. **Commit/Rollback** - Keep improvements, discard regressions, update heuristics.md
6. **Check Graduation** - 2+ passes in last 3 iterations = graduated

## Workspace Structure

```
skill-improver-workspace/
├── config.json              # User-provided metrics, targets, test cases
├── iterations/              # One dir per experiment with hypothesis + verdict
├── results.tsv              # Cumulative tracking (AutoResearch style)
├── heuristics.md            # Accumulated learnings (persists across sessions)
└── baseline/
    └── SKILL.md.backup      # Original skill (never modified)
```

## Installation

Copy the `SKILL.md` and supporting files to your Claude Code skills directory:

```bash
cp -r * ~/.claude/skills/awesome-skill-improver/
```

## License

MIT

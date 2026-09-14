# awesome-skill-improver

A Claude Code skill for iteratively improving any other skill through hypothesis-driven, git-checkpointed experimentation.

## What it does

- Single-variable testing: changes one thing per iteration, so you know what worked.
- Measurable outcomes: all metrics and targets come from the user at runtime, nothing is hardcoded to a specific skill.
- Git-based safety: checkpoints before every experiment, rolls back on failure.
- Accumulated learning: heuristics persist across sessions in `heuristics.md`.
- Triggers on "improve skill," "optimize workflow," "reduce errors in skill," "make skill faster," "skill is too slow/expensive," or any request to apply trial-and-error methodology to skill development.

## Install

```bash
cp -r * ~/.claude/skills/awesome-skill-improver/
```

## Usage

```
/skill-improver init --skill <name>    # discover metrics, set goals, create workspace
/skill-improver run [--iterations N]   # run N improvement iterations
/skill-improver status                 # show progress toward goals
/skill-improver graduate               # apply accepted changes, run /simplify
/skill-improver reset                  # discard all changes, restore baseline
```

## How it works

1. **Initialize**: auto-discovers metrics from the target skill's output (via `scripts/capture_metrics.py`), asks the user for optimization targets.
2. **Generate hypothesis**: proposes one change per iteration, based on accumulated learnings.
3. **Execute experiment**: git checkpoint, apply the change, run the skill, capture metrics.
4. **Evaluate**: compares before and after, detects regressions on secondary metrics.
5. **Commit or rollback**: keeps improvements, discards regressions, updates `heuristics.md`.
6. **Check graduation**: 2 or more passes in the last 3 iterations graduates the skill.

## Layout

- `SKILL.md`: the skill definition and full phase-by-phase logic.
- `scripts/capture_metrics.py`: extracts `wall_time_seconds`, JSON numeric or boolean values, and regex-matched metrics (API calls, rows written, pass/fail) from a skill's output.
- `references/hypothesis-templates.md`: templates for generating hypotheses.
- `evals/evals.json`: evaluation cases.
- `skill-improver-workspace/` (created at runtime): `config.json`, `iterations/`, `results.tsv`, `heuristics.md`, `baseline/SKILL.md.backup`.

## Notes

- Inspired by karpathy/autoresearch and browserbase/autobrowse.
- The baseline `SKILL.md` backup is never modified; only the live copy under improvement changes.

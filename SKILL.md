---
name: awesome-skill-improver
description: Iteratively improve any Claude Code skill through hypothesis-driven experimentation. Use when someone wants to optimize a skill's performance, reduce API calls, improve accuracy, speed up execution, or systematically enhance any measurable aspect of a skill. Also trigger when users mention "improve skill", "optimize workflow", "reduce errors in skill", "make skill faster", "skill is too slow/expensive", or want to apply trial-and-error methodology to skill development. Works with ANY skill - all metrics and targets are discovered at runtime, nothing is hardcoded.
---

# Skill Improver

A framework for iteratively improving any Claude Code skill using hypothesis-driven, trial-and-error methodology. Inspired by [karpathy/autoresearch](https://github.com/karpathy/autoresearch) and [browserbase/autobrowse](https://skills.sh/browserbase/skills/autobrowse).

## Core Philosophy

1. **Single-variable testing** - Change ONE thing per iteration so you know what worked
2. **Measurable outcomes** - If you can't measure it, you can't improve it
3. **Git-based safety** - Checkpoint before every experiment, rollback on failure
4. **Accumulated learning** - Heuristics persist across sessions, failures teach
5. **Nothing hardcoded** - All metrics and targets come from the user at runtime

---

## Entry Points

| Command | What it does |
|---------|--------------|
| `/skill-improver init --skill <name>` | Discover metrics, set goals, create workspace |
| `/skill-improver run [--iterations N]` | Run N improvement iterations |
| `/skill-improver status` | Show progress toward goals |
| `/skill-improver graduate` | Apply accepted changes, run /simplify |
| `/skill-improver reset` | Discard all changes, restore baseline |

---

## Phase 0: Initialize

When the user runs `init`:

### Step 1: Locate the skill
```bash
SKILL_PATH=$(find ~/.claude/skills -name "SKILL.md" -path "*/<skill-name>/*" | head -1)
```
If not found, ask the user for the path.

### Step 2: Create workspace
```
skill-improver-workspace/
├── config.json              # Will hold all user-provided settings
├── iterations/              # One dir per experiment
├── results.tsv              # Cumulative tracking
├── heuristics.md            # Accumulated learnings
└── baseline/
    └── SKILL.md.backup      # Original skill (never modified)
```

Copy the skill's SKILL.md to `baseline/SKILL.md.backup`.

### Step 3: Discover metrics

Run the skill once with a simple test input to capture its output. Extract all measurable values:

```python
# Use scripts/capture_metrics.py
python ~/.claude/skills/skill-improver/scripts/capture_metrics.py "<skill_output>"
```

This auto-discovers:
- **Timing**: wall_time_seconds (always available)
- **JSON values**: Any numeric/boolean in JSON blocks
- **Regex patterns**: API calls, rows written, scores, pass/fail

Present discovered metrics to the user:
```
Found these metrics in skill output:
  - wall_time_seconds (numeric)
  - api_call_count (numeric)
  - validation_passed (boolean)
  - rows_written (numeric)

Which metric(s) do you want to optimize?
```

### Step 4: Get optimization goals from user

Ask for:
1. **Primary metric(s)** to optimize and their targets (e.g., "api_call_count <= 30")
2. **Secondary metrics** to track for regressions (won't optimize, but will fail if they get worse)
3. **Test cases** - inputs to run the skill against (or use skill's evals.json if it exists)

### Step 5: Save config.json

```json
{
  "target_skill": "<name>",
  "target_skill_path": "<path>",
  "optimization_goals": [
    {"metric": "<name>", "operator": "<=", "target": 30, "priority": 1}
  ],
  "secondary_metrics": ["wall_time_seconds"],
  "test_cases": [
    {"input": "<prompt>", "description": "<what it tests>"}
  ],
  "graduation_criteria": "2/3",
  "time_budget_per_iteration": 300,
  "max_iterations": 10
}
```

### Step 6: Create git branch
```bash
git checkout -b skill-improve/<skill-name>-$(date +%Y%m%d)
```

### Step 7: Run baseline measurement

Execute the skill against all test cases, capture metrics, save to `iterations/000-baseline/metrics.json`.

---

## Phase 1: Generate Hypothesis

Before each iteration, generate a hypothesis about what single change might improve the target metric.

### Read context first
1. Load `heuristics.md` (past learnings from this and previous sessions)
2. Load last 3 entries from `results.tsv`
3. If available, read the skill's code to understand its structure

### Propose ONE change

Write `iterations/<NNN>/hypothesis.md`:

```markdown
## Iteration {N} Hypothesis

**Current state:** {metric} = {current_value}, target {operator} {target_value}

**Problem observed:** {what's causing the metric to be suboptimal}

**Proposed change:** {specific, single change to make}

**Files to touch:** {exactly one file path}

**Expected improvement:** {metric} {current} → {expected}

**Rollback trigger:** {conditions that mean this failed}
```

The single-variable principle is critical. If you change multiple things and the metric improves, you won't know which change caused it. If it regresses, you won't know which change to revert.

---

## Phase 2: Execute Experiment

### Step 1: Git checkpoint
```bash
git add -A && git commit -m "checkpoint before iteration {N}"
CHECKPOINT=$(git rev-parse HEAD)
```

### Step 2: Apply the change

Edit the single file identified in the hypothesis. Make the smallest change that tests the hypothesis.

### Step 3: Git commit the change
```bash
git add -A && git commit -m "iteration {N}: {hypothesis summary}"
```

### Step 4: Run the skill

For each test case in config.json:
```bash
# Capture output and timing
START=$(date +%s.%N)
OUTPUT=$(claude -p "<test_case_input>" --skill <skill_name> 2>&1)
END=$(date +%s.%N)
ELAPSED=$(echo "$END - $START" | bc)
```

### Step 5: Capture metrics

```bash
python ~/.claude/skills/skill-improver/scripts/capture_metrics.py "$OUTPUT" > metrics-after.json
```

### Step 6: Enforce time budget

If any test case exceeds `time_budget_per_iteration`, kill it and treat as failure.

---

## Phase 3: Evaluate

Compare `metrics-before.json` (from baseline or previous iteration) with `metrics-after.json`.

### Decision rules

**PASS (keep)** if ALL of:
- Primary metric improved toward target OR reached target
- No secondary metrics regressed significantly (>10% worse)
- No new errors or validation failures

**FAIL (discard)** if ANY of:
- Primary metric got worse
- Any secondary metric regressed >10%
- New errors appeared
- Skill crashed or timed out

### Write verdict.json

```json
{
  "iteration": 3,
  "status": "keep",
  "reason": "api_call_count 45→32 (-29%)",
  "regression_detected": false,
  "metrics_delta": {
    "api_call_count": {"before": 45, "after": 32, "delta": -13, "percent": -29},
    "wall_time_seconds": {"before": 120, "after": 115, "delta": -5, "percent": -4}
  }
}
```

---

## Phase 4: Commit or Rollback

### If PASS (keep)
1. Keep the commit, branch advances
2. Update `heuristics.md` with what was learned:
   ```markdown
   ### Iteration 3 - KEPT
   **Change:** Batched API calls in write_rows()
   **Impact:** api_call_count -29%
   **Why it worked:** Reduces HTTP overhead, fewer round trips
   ```
3. Append to `results.tsv`

### If FAIL (discard)
1. Rollback: `git reset --hard $CHECKPOINT`
2. Update `heuristics.md` with what didn't work:
   ```markdown
   ### Iteration 3 - DISCARDED
   **Change:** Async API calls
   **Impact:** Caused race conditions, validation failures
   **Lesson:** This skill requires sequential writes for data integrity
   ```
3. Append to `results.tsv` with status=discard

---

## Phase 5: Check Graduation

After each iteration, check if graduation criteria is met.

### Default criteria: "2/3"
If 2 or more of the last 3 iterations were PASS (keep), the skill has graduated.

### On graduation
1. Announce: "Skill has graduated! 2+ improvements in last 3 iterations."
2. Run `/simplify` on all modified files to clean up
3. Generate session report to `reports/YYYY-MM-DD-HHMM.md`
4. Ask user: "Ready to merge improvements to main branch?"

### If stuck (3+ consecutive FAIL)
Invoke the **Advisor Agent**:

```
Spawn subagent with prompt:
"Review the last 5 iterations for skill {name}.
Workspace: {path}

The skill-improver is stuck - 3+ consecutive failed experiments.

Analyze:
1. Pattern in the failures
2. Whether we're in a local minimum
3. Structural changes that might unlock progress

Suggest ONE of:
- A bold hypothesis that breaks from recent patterns
- A recommendation to simplify/remove complexity
- A recommendation to pause and seek human input"
```

---

## results.tsv Format

Tab-separated, append-only log:

```tsv
iter	commit	status	primary_metric	primary_value	secondary_metrics	hypothesis	timestamp
000	a1b2c3d	baseline	api_call_count	45	{"wall_time":120}	baseline measurement	2026-04-24T10:00:00
001	b2c3d4e	keep	api_call_count	38	{"wall_time":115}	batch room amenities	2026-04-24T10:05:30
002	c3d4e5f	discard	api_call_count	42	{"wall_time":140}	async API calls	2026-04-24T10:11:00
003	d4e5f6g	keep	api_call_count	32	{"wall_time":110}	dedupe facility lookups	2026-04-24T10:16:45
```

---

## Custom Metric Extractors

If the auto-discovery doesn't find a metric you need, add custom extractors to config.json:

```json
{
  "custom_extractors": [
    {"pattern": "facility_density:\\s*([\\d.]+)", "name": "facility_density", "type": "float"},
    {"pattern": "issues found: (\\d+)", "name": "issue_count", "type": "int"}
  ]
}
```

---

## Safety Mechanisms

1. **Single-file scope** - Each iteration touches exactly one file
2. **Git checkpoint** - Commit before every change, always recoverable
3. **Time budget** - Kill runaway experiments
4. **Regression detection** - Never accept changes that break working things
5. **Advisor escalation** - Get help when stuck
6. **Baseline preservation** - Original skill always in `baseline/`

---

## Session Persistence

The workspace persists across Claude sessions:
- `config.json` - Optimization goals don't need to be re-entered
- `results.tsv` - Full history of all experiments
- `heuristics.md` - Accumulated learnings
- Git branch - All changes tracked

To resume: `/skill-improver status` shows where you left off.

---

## References

- `scripts/capture_metrics.py` - Generic metrics extraction (read for implementation details)
- `references/hypothesis-templates.md` - Common improvement patterns to try

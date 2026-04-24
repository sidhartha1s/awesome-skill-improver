# Hypothesis Templates

Common improvement patterns to try when optimizing skills. Use these as starting points - adapt to your specific skill.

---

## Reduce API Calls

### Batching
**Problem:** Making N separate API calls when one batch call would work
**Change:** Collect items, make single batch request
**Example:** Instead of writing rows one at a time, collect all rows and write with one batchUpdate

### Caching
**Problem:** Same data fetched multiple times
**Change:** Cache results of expensive lookups
**Example:** Cache section row numbers after first scan instead of re-scanning

### Deduplication
**Problem:** Redundant requests for same data
**Change:** Track what's already fetched, skip duplicates
**Example:** Check if URL already scraped before making request

---

## Reduce Wall Time

### Parallelization
**Problem:** Sequential operations that could run concurrently
**Change:** Use async/parallel execution where safe
**Caution:** Watch for race conditions, may need sequential for data integrity

### Early Exit
**Problem:** Processing continues even when answer is known
**Change:** Return early when goal is achieved
**Example:** Stop searching after finding first match

### Lazy Loading
**Problem:** Loading all data upfront when only subset needed
**Change:** Load data on-demand
**Example:** Only fetch page content when that page is being processed

---

## Improve Accuracy

### Better Prompts
**Problem:** LLM misunderstands what's needed
**Change:** Add examples, clarify edge cases, constrain output format
**Example:** Add "Output ONLY the JSON, no explanation" to reduce parsing failures

### Validation Loops
**Problem:** Errors slip through unchecked
**Change:** Add validation step, retry on failure
**Example:** Validate JSON output, retry with error message if invalid

### Structured Output
**Problem:** Free-form output is hard to parse reliably
**Change:** Use JSON mode or strict templates
**Example:** Switch from prose to JSON with defined schema

---

## Reduce Token Usage

### Prompt Trimming
**Problem:** Unnecessary context in prompts
**Change:** Remove examples/instructions that aren't pulling weight
**Test:** Remove section, check if output quality drops

### Response Constraints
**Problem:** Model outputs verbose explanations
**Change:** Add "Be concise" or constrain max tokens
**Example:** "Respond with only the corrected text, no explanation"

### Progressive Disclosure
**Problem:** Loading entire reference file when only part needed
**Change:** Split into sections, load only relevant parts
**Example:** Load only AWS docs for AWS-related queries, not all cloud providers

---

## Improve Robustness

### Error Handling
**Problem:** Skill crashes on unexpected input
**Change:** Add try/catch, provide meaningful error messages
**Example:** Catch JSON parse errors, report which field was invalid

### Timeout Handling
**Problem:** Skill hangs on slow operations
**Change:** Add timeouts, fallback behavior
**Example:** 30s timeout on HTTP requests, skip and log if exceeded

### Input Validation
**Problem:** Bad input causes confusing failures later
**Change:** Validate early, fail fast with clear message
**Example:** Check required fields exist before starting processing

---

## Simplification

### Remove Dead Code
**Problem:** Unused branches, obsolete features
**Change:** Delete code that isn't executed
**Test:** Run tests, verify nothing breaks

### Consolidate Duplicates
**Problem:** Same logic in multiple places
**Change:** Extract to shared function
**Example:** Multiple functions doing URL normalization → single normalize_url()

### Flatten Nesting
**Problem:** Deep nesting makes code hard to follow
**Change:** Use early returns, extract functions
**Example:** Replace nested if/else with guard clauses

---

## Workflow Patterns

### Single Responsibility
**Problem:** One function doing too many things
**Change:** Split into focused functions
**Why:** Easier to test, optimize, and debug individual parts

### Fail Fast
**Problem:** Errors detected late in process
**Change:** Move validation to beginning
**Example:** Check all required inputs exist before starting any processing

### Idempotency
**Problem:** Running twice produces different/bad results
**Change:** Make operations safe to retry
**Example:** Check if row exists before inserting (upsert pattern)

---

## When Stuck

If 3+ iterations fail, try:

1. **Radical simplification** - Remove 30% of the skill, see if core still works
2. **Different approach** - If optimizing X fails, try removing need for X entirely
3. **Break the rules** - Temporarily ignore secondary metrics to see if primary can move
4. **Human review** - Ask user to look at transcripts, they may spot obvious issues

Remember: sometimes the best improvement is realizing a metric can't be optimized further without fundamental redesign. It's okay to conclude "this is as good as it gets" and graduate.

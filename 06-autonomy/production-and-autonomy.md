# Production & Autonomy: Cortex PM Chief-of-Staff Agent

> Module 6 · ★ Deliverable 5, how you'd ship it, govern it, and widen trust over time
>
> ✅ **What this validates:** you can ship it, govern it, and widen trust deliberately — by the end you'll have proven an autonomy dial, a Trust Ladder rung with its eval gate, and a governance plan.

## Autonomy Dial by segment

_Autonomy is a product decision per user, not one global setting._

| Segment | Desired autonomy | Why |
|---|---|---|
| You (the builder/primary PM) | Supervised now → moving toward Bounded-autonomous | Watched Cortex closely across 6 modules and know its failure modes firsthand — more trust earned than a first-time user, but the M5 eval gate hasn't formally been cleared yet |
| A new PM joining later, who didn't build it | Assisted | No built-up context on Cortex's blind spots — needs every output reviewed closely, ideally with the reasoning trace visible, until they've seen it work reliably themselves |
| An eng lead reviewing proposed sprint stories | Supervised | Doesn't run Cortex directly, but is the actual approver at the `propose_stories` HITL checkpoint — wants to see every batch before it hits sprint planning, regardless of how trusted the status-update side becomes |

## Trust Ladder

- **Current rung:** Supervised — every single run, even a clean happy-path success, stops at a HITL checkpoint before anything is used. Nothing has ever been allowed to auto-post or auto-approve.
- **Eval gate to reach the next rung (Bounded-autonomous):** ≥95% pass rate on EV-1, EV-2, EV-4 (tool-call accuracy, path quality, task completion) AND 100% pass on EV-3, EV-5, EV-6 (recovery, safety/jailbreak, confidentiality guard) — measured over 4 consecutive weeks of supervised real heartbeat+cron runs (not just the 3 fixture tasks). Safety-critical evals get a hard 100% bar with zero tolerance; routine-quality evals get a high-but-not-perfect bar since normal review catches those slips easily.
- **Incident record so far:** Zero confirmed incidents to date — no confidential item (Orbit/Pulsar) has ever reached an output, no invented/uncited metric or date has ever reached the PM without the critic catching it first, and no HITL checkpoint has been silently bypassed.

## Deployment plan

- **Runtime:** A scheduled serverless function, not an always-on server — tied directly to the M2 loop type (heartbeat every 15-30 min + weekly cron backup). Each run is quick (~10-20s), so paying for an always-on process would be wasteful; a cloud scheduler triggering a short-lived function matches the actual usage pattern.
- **Operator / on-call owner:** Just me (the builder), for now — no backup. **Honest gap:** this fails the "builder goes on vacation" test; there's no named escalation path if I'm unavailable. Worth revisiting once this widens beyond a solo project (see Governance & forward strategy below).
- **Rollback:** Three tiers, cheapest first — (1) drop the dial a rung for the affected segment, no code change; (2) disable a specific misbehaving tool by removing it from `TOOL_SCHEMAS` (proven mechanism, used in M4's grounding probe); (3) `git revert` to the last known-good commit of `prompts.py`/`agent.py`.
- **Monitoring:** Eval pass % per EV case (M5), escalation rate (% of runs ending `ESCALATE` vs `DONE`), cost-to-serve (actual $/run vs the `$0.50` cap), and trust incidents (from the Trust Ladder's incident record).

## ROI metrics (beyond adoption & tokens)

| Metric | Target | How you'd capture it |
|---|---|---|
| **Outcome** | ≥80% of weekly drafts approved with zero or minor edits (not a substantial rewrite) | Compare Cortex's queued draft (`run-output/`) against what was actually sent, per cycle |
| **Cost-to-serve** | Actual $/cycle stays well under the `$0.50` per-run cap (observed so far: ~$0.02/run) | Sum `bounds.cost` per run, aggregated weekly |
| **Trust incidents** | 0 confirmed incidents/month | Logged from the Trust Ladder's incident record whenever something slips past the critic and a human catches it later |

## Widen-autonomy decision rule

The dial moves from Supervised to Bounded-autonomous the moment Cortex clears the M5 eval gate (≥95% on EV-1/EV-2/EV-4, 100% on EV-3/EV-5/EV-6, zero confirmed incidents) sustained over 4 consecutive weeks of real runs — not a demo, not a single good week.

## Governance & forward strategy

- **Compliance:** Once real connectors (M2's plan) are wired, raw PII from Slack/email/Jira must never enter a prompt beyond the minimal reference already scoped in M4's memory map (item ID + topic + timestamp) — never full message bodies. No dumping org-wide data into a single run's context; every pull stays scoped to the specific project/task.
- **Safety:** Stays above the line for everyone, regardless of dial position or segment: posting/publishing (structurally impossible — no publish tool exists), committing a ship/GA date, marking a launch gate, exposing confidential/embargoed roadmap items externally. Kill switch: the `CORTEX_ENABLED=false` env flag from M5, single point of control.
- **Reliability:** All 7 bounds from M5's table; escalate-on-stuck via `MAX_ITERATIONS=8` + `MAX_REVISIONS=2`. Genuine gap flagged honestly: there's no defined model-down fallback yet — if the Anthropic API errors or is unreachable, the current code would just crash rather than fail closed cleanly. Proposed fix: treat an API failure as an automatic escalation ("system unavailable, nothing drafted") rather than crashing or silently retrying forever.
- **Strategy:** Next capability to widen into: wiring the real Slack connector (M2's plan, sequenced first). Gated by re-running the M1 agent-line exercise for that new tool, plus proving EV-1/EV-2 hold specifically for it before it's trusted at the same level as the existing tools.

# Orchestration Map: Cortex PM Chief-of-Staff Agent

> Module 3 · Orchestration & Subagents, ★ Deliverable 3
>
> ✅ **What this validates:** nothing advances unchecked — by the end you'll have proven a justified topology, a roster, and a validator with a defined fail action.
>
> Builds on your M2 Loop Spec. Only split one agent into a team when there's a real reason, coordination has a cost.

## 1. Why split? (or why not)

**Cortex's design (one line):** A heartbeat+cron-triggered agent that pulls project data (activity, roadmap, norms, past updates) and drafts the weekly status update + proposes next-sprint stories.

| Reason | Applies? | Why / why not |
|---|---|---|
| Separation of concerns | No | Pull data → draft is one coherent task, not genuinely separate domains of responsibility. |
| Parallelism | No | The current data pulls are fast, fixture-based reads — no meaningful time saved splitting them into parallel subagents. |
| **Independent validator** | **Yes** | Cortex wrote the draft, so it shares whatever blind spot produced a bad claim (an invented metric, an implied commitment) — it can't reliably catch its own mistake. |
| Context-window pressure | No | The pulled data is small (a handful of tool results); nowhere near context limits. |

**Verdict:** Split — add exactly one subagent, the validator/critic (already scaffolded as `critic.py`).

## 2. Topology

**Pattern:** Single + subagents

```
[Heartbeat/cron trigger] → [Cortex: pulls data, drafts update + stories]
                         → [Validator/Critic]
                              fail → back to Cortex (max 2 revisions) → escalate to human
                              pass → [PM review checkpoint] → queued (nothing sent)
```

## 3. Roster

| Agent / subagent | Responsibility | Runs which Loop Spec |
|---|---|---|
| Cortex (chief-of-staff) | Pulls project data, drafts status update + proposes stories | M2 loop — heartbeat (primary) + weekly cron (backup) |
| Critic / Validator | Checks Cortex's draft against the 6 checks before a human sees it | Single independent validation call per draft |

## 4. Communication & hand-offs

Cortex passes the proposed draft text + its source log (the tool results it relied on) to the critic. The critic returns a verdict dict (`pass`/`fail` + reasons). This is a plain **in-process function call** (`review(client, MODEL, proposed, source_log)`) — no MCP/A2A.

## 5. The validator

- **What the critic checks:**
  1. References the correct project + real activity/PR/issue IDs
  2. Every claim (figures, dates, red/yellow/green calls) traces to pulled data — no invented numbers
  3. Stays within team norms (no unconfirmed date, no launch gate marked, no CONFIDENTIAL/embargoed item exposed)
  4. Posts/commits/creates nothing; no confidential leak
  5. Correctly refuses and escalates on a jailbreak/prompt-injection attempt
  6. If a tool rejected an action (e.g. story batch over the queue cap), escalating is treated as correct, not penalized
- **Fail action:** Revise — draft goes back to Cortex with the rejection reasons, up to `MAX_REVISIONS=2` (matches the M2 Loop Spec's stuck condition). After 2 rejections, escalate to a human instead of looping further.
- **Pass action:** Advances to the PM review checkpoint — does **not** auto-send; still above the agent line from M1.

## 6. State: shared vs isolated

**Shared:** the draft text + the source data log (the tool results Cortex pulled) — both agents need the same evidence to agree or disagree on it.

**Isolated:** the critic's own reasoning/system prompt never leaks into Cortex's context as if Cortex had thought of it itself. On a revision, only the final verdict + reasons get fed back to Cortex — not the critic's full chain of thought. Keeps the critic's judgment independent rather than something Cortex could learn to game.

## 7. Cost & latency budget

The validator adds exactly 1 extra model call per drafting attempt. Worst case, at the `MAX_REVISIONS=2` cap, that's 3 critic calls total (initial + 2 revisions) before escalating — each one small (short JSON verdict out), adding roughly $0.001–0.003 per call, so worst-case added cost is a few cents at most, well inside the `$0.50` cost cap. Added latency is one extra round-trip per attempt — a few seconds per critic check, so worst case ~10-15 extra seconds before a draft reaches the PM review checkpoint, on top of however long Cortex's own revision drafting takes. (Forward-link to M5: this becomes a formal bound.)

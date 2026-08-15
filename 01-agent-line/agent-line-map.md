# Agent Line Map: Cortex PM Chief-of-Staff Agent

> Module 1 · The Agent Line
>
> ✅ **What this validates:** every risky action has a clear owner — by the end you'll have proven an above/below-the-line map with HITL checkpoints, scored on reversibility, blast radius, and measurability.

## The workflow, decision by decision

List every discrete decision or action in your agent's workflow, then score each one and place it **above** the line (a human owns it) or **below** (the agent owns it). Borderline calls get an HITL checkpoint.

| Decision / action | Reversibility (H/M/L) | Blast radius (H/M/L) | Measurability (H/M/L) | Above / Below | HITL? |
|---|---|---|---|---|---|
| Pull project state + activity | H | L | H | Below | · |
| Decide relevant context | H | M | H | Below | · (covered by the draft's HITL gate) |
| Draft the update | H | M | H | Below | required |
| Decide commitment level (dates/promises) | L | H | M | Above | n/a (human-owned) |
| Decide tone (green/yellow/red framing) | H | M | M | Below | required |
| Flag at-risk/escalation | H | M | M | Below | required |
| Choose what to escalate | H | M | M | Below | required |
| Propose a story batch (capped) | H | M | H | Below | required |
| Post an update / approve a company-wide one | L | H | M | Above | n/a (human-owned) |

## Agent anatomy (sketch)

- **Model:** `claude-haiku-4-5-20251001` by default. Escalate to a frontier model (Sonnet) only if the critic rejects the draft twice — reuses the `CORTEX_MAX_REVISIONS=2` trip point, so a stronger model gets one shot before the run gives up and escalates to a human.
- **Tools:** `get_project`, `get_activity`, `search_past_updates`, `get_roadmap`, `get_norms` (all read-only lookups) · `propose_stories` (write, but capped and queue-only — nothing is created, rejected above the item cap).
- **Memory:** persists across runs — past decisions, the roadmap, team norms/PM playbook, and guidelines on how to write to and give feedback to the agent. Purged/refetched every run — live project state and activity, since those must always be current, never stale or cached.
- **Loop:** _placeholder, defined in M2 loop-spec.md_
- **Bounds:** _placeholder, defined in M5 bounds-and-evals.md_
- **Evals:** _placeholder, defined in M5 bounds-and-evals.md_

## The golden rule, applied

1. **Pull project state + activity** sits below the line because it's easy to reverse, has a low blast radius, and is easy to verify — deciding factor: blast radius.
2. **Decide relevant context** sits below the line (no separate gate) because it's easy to reverse and easy to verify; its medium blast radius is already covered by the mandatory gate on the draft — deciding factor: reversibility.
3. **Draft the update** sits below the line, with a required human check, because it's easy to reverse and easy to verify, but its medium blast radius means Cortex shouldn't run ungated — deciding factor: blast radius.
4. **Decide commitment level** sits above the line because it's hard to reverse once implied and carries a high blast radius that can cascade into other people's planning — deciding factor: blast radius.
5. **Decide tone** sits below the line, with a required human check, because it's easy to reverse but its medium blast radius still warrants confirmation before it ships — deciding factor: blast radius.
6. **Flag at-risk/escalation** sits below the line, with a required human check, because a false alarm carries real political cost even though it's easy to reverse — deciding factor: blast radius.
7. **Choose what to escalate** sits below the line, with a required human check, for the same reason as flagging — deciding factor: blast radius.
8. **Propose a story batch (capped)** sits below the line, with a required human check, because it's easy to reverse and easy to verify against the PRD, but its medium blast radius (misdirecting sprint planning) still warrants confirmation — deciding factor: blast radius.
9. **Post an update / approve a company-wide one** sits above the line because it's hard to reverse once sent and carries a high blast radius (organizational churn) — deciding factor: blast radius.

## Hardest call

The tone and escalation-flagging decisions (deciding tone, flagging at-risk, choosing what to escalate) were the hardest to place. Even outputs that never leave the building — an internal status update's tone, an at-risk flag — can create real political churn inside an organization if Cortex gets them wrong. That tension is what settled these as below-the-line-but-gated rather than either extreme: fully autonomous felt too risky given the political cost of a false call, but fully human-owned felt like over-gating work Cortex can competently draft. Deciding factor: blast radius — specifically the political/reputational kind, not the technical kind.

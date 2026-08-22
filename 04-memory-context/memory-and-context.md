# Context Engineering & Memory: Cortex PM Chief-of-Staff Agent

> Module 4 · Context Engineering & Memory
>
> ✅ **What this validates:** the agent reasons on the right, safe inputs — by the end you'll have proven a context budget, per-source retrieve-vs-long-context decisions, and a memory map with risk mitigations.
>
> 🗂️ **How the lab maps to this file:** In **Part A** (before the lecture) you don't edit this file — you rough-draft on scratch, focused on the per-source calls in **section 2** plus a quick remember/forget + "how it rots" sketch. In **Part B** (after the lecture) you complete **all five sections**; the Lab Guide's guided builder writes this file for you to copy in and commit.

## 1. Context budget

Each loop iteration receives the task brief directly, embedded in the initial prompt as long-context, plus whatever it retrieves via tool calls this turn (`get_project`, `get_activity`, `get_norms`, `get_roadmap`, `search_past_updates`) — nothing else is stuffed in upfront.

**Priority order if the budget is tight:**
1. `get_project` — foundational; everything else is interpreted against project status/flags
2. `get_activity` — the actual evidence for every claim in the draft
3. `get_norms` — governs what Cortex is even allowed to say
4. `get_roadmap` — needed for scope/confidentiality checks
5. `search_past_updates` — lowest stakes, only shapes tone/precedent — safe to drop first

## 2. Retrieve vs. long-context: per source

For each data source, decide: **retrieve** (narrow a large/changing corpus to the relevant slice) or **long-context** (just include a bounded set you can reason over).

| Source | Size / volatility | Decision | Why |
|---|---|---|---|
| `get_task` | Small, static within a run | Long-context | One static doc that doesn't change within a run — no reason to retrieve what you already have in hand |
| `get_activity` | Large, grows over time | Retrieve | Stuffing the full PR/issue history would blow the budget fast; only need this run's slice |
| `search_past_updates` | Unbounded | Retrieve | Could span the team's entire history — must be query-scoped. Draws from both `past-updates.json` and `decision-log.json` under the hood. |
| `get_roadmap` | Medium, confidential flags | Retrieve | Retrieval lets you filter/audit exactly what was shown, not silently bake secrets into context |
| `get_norms` | Medium, must stay current | Retrieve | Volatility — a cached/long-context copy could go stale |

## 3. Retrieval quality plan

_Which of these apply, and how? (This is what separates modern agentic retrieval from naive "embed → top-k → stuff".)_

| Source | Failure mode | Move(s) | Why |
|---|---|---|---|
| `get_activity` | Cortex cites activity that's stale or invents beyond what came back | Document grading + Self-verification | Grading catches wrong/stale data before use; self-verification (the critic) confirms every claim traces to what was actually returned |
| `search_past_updates` | Query surfaces the wrong project's precedent or an outdated update, skewing tone (observed in practice: results can mix in other projects) | Routing + Document grading + Reranking | Routing scopes the query to the right project/topic; grading filters out non-matching projects; reranking surfaces the most recent precedent over stale ones |
| `get_roadmap` | Confidential/embargoed items (Orbit, Vega) leak into scope | Document grading + Self-verification | Grading filters to only shareable, in-scope items; self-verification (critic check) confirms nothing confidential made it into the final draft |
| `get_norms` | Wrong norm subset returned for the query, or acting on a stale cached norm | Routing + Caching (short TTL) | Routing scopes the query to the specific rule category needed; caching is fine for cost, but needs a short TTL since acting on a stale norm is a real risk |

## 4. Memory map (your PM brain)

| Memory type | What Cortex stores | Scope / TTL |
|---|---|---|
| **Working** (in-loop) | This run's pulled tool results (project, activity, norms, roadmap, past-updates), the draft-in-progress, the critic's verdict/reasons for the current revision | Duration of a single run — discarded after it ends or escalates |
| **Episodic** (past runs) | Past status updates (`search_past_updates`, drawing from `past-updates.json` + `decision-log.json`), the "already surfaced" dedupe markers (item ID + day/hour + topic) from M2 | Past updates/decisions: rolling retention window (e.g. last few quarters); dedupe markers: a few days — long enough to survive to the next heartbeat/cron cycle, short enough not to grow unbounded |
| **Semantic** (durable facts/prefs) | Team norms, roadmap facts, guidelines on giving Cortex feedback | Durable at the source, but never cached long inside Cortex itself — re-retrieved each cycle with the short TTL from §3, so "durable" means the source of truth persists, not a stale local copy |
| **Shared** (across agents) | The draft + its source data log, shared between Cortex and the critic for one validation exchange | Duration of that single validation exchange only — the critic's own reasoning stays isolated (per M3 §6) |

## 5. Memory risks & mitigations

| Risk | Where it bites Cortex | Mitigation |
|---|---|---|
| **Drift** | If Cortex's own paraphrase of norms/roadmap ever got treated as stored memory instead of the raw doc, small distortions could compound over many cycles | Semantic memory is always re-derived from the raw source each cycle, never from Cortex's own prior summary |
| **Poisoning** | A malicious/injected entry in the decision log or past-updates, or a spoofed dedupe marker falsely tagging a genuinely new urgent item as "already surfaced" | Cortex only ever reads source-of-truth docs — writing to them stays above the M1 agent line, human-owned. Dedupe markers use immutable system IDs, not freeform text a prompt injection could spoof |
| **Staleness** | A cached norms/roadmap copy held too long, or resuming a stuck/escalated run on old working memory | Short TTL on cached retrieved sources (§3); project state + activity are always purged/refetched fresh, never resumed from old working memory |
| **PII / retention** | Once real Slack/email/Jira connectors (M2's plan) are wired, episodic memory could store raw message content with PII far longer than needed | Episodic/dedupe memory stores only the minimal reference (ID + topic + timestamp), never full message bodies; a bounded retention TTL purges old entries — these TTLs become formal bounds in M5 |

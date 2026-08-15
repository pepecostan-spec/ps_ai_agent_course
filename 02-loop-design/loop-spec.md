# Loop Spec: Cortex PM Chief-of-Staff Agent

> Module 2 · Loop Engineering, ★ Deliverable 2
>
> ✅ **What this validates:** the agent knows when to run and when to stop — by the end you'll have proven a one-page Loop Spec with a trigger, a definition of "done," and explicit stop conditions.
>
> Your one-page blueprint for how the work you handed to the agent (M1) actually *runs*.
> An agent is just a prompt that fires itself, this spec says when it fires, what "done" means, and what it needs to do the job. Living document; refine as the course progresses.

## 1. Trigger & loop type

**Chosen type:** Heartbeat (primary) + Cron (backup)

**Why:** A frequent heartbeat (every 15–30 min) checks for urgent items across messages/emails/tickets and surfaces them fast — that responsiveness is the core value. A weekly cron backup is a safety-net full sweep, guaranteeing nothing sits unresolved if the heartbeat ever misses something.

**Ruled out:**
- *Cron alone* — a single weekly run lets the backlog build up too much between sweeps; now used as a backup instead of the primary trigger.
- *Hook* — reacting to every single inbound message/event individually would get unmanageable and noisy.
- *Goal* — doesn't fit; Cortex is meant to be something continuously used and worked with, not a loop that runs once toward a terminal done-state.

**Idempotency/dedupe:** Track by item ID (message/ticket ID) + an "already surfaced" marker, tagged with day/hour and topic — so a repeat heartbeat cycle recognizes an item it already flagged (instead of re-drafting/re-flagging it) and the marker itself is human-readable enough to jog memory on what it was.

## 2. Goal / definition of done

A list of flagged items for review, with drafts saved for you to review. Nothing is sent. Each cycle is "done" when the backlog it's responsible for (urgent items for the heartbeat, the full backlog for the weekly cron) has been triaged: every item flagged, drafted, or marked seen.

## 3. Stop conditions

| Condition | What it looks like | What happens |
|---|---|---|
| **Success** | Draft passes the critic's grounding/norms checks; backlog for this cycle is fully triaged (flagged, drafted, or marked seen) | Flagged items + drafts saved, queued for review; nothing sent |
| **Stuck / give up** | A needed data pull fails 2 attempts in a row, OR the critic rejects the same draft 2 times in a row | Stop the cycle, log what was attempted and why; leave for the next cycle or human attention rather than keep retrying |
| **Escalate to human** | Commitment-level language (dates/promises); story batch over the queue cap; tone/at-risk flagging judgment call; embargoed/confidential item; a Sev-1 issue; or anything requiring posting/sending | Immediate escalate-and-stop — HITL checkpoint (per `agent-line-map.md`), held for human, nothing posted |

## 4. State

Persists across cycles: the roadmap, past decisions, team norms/PM playbook, guidelines on giving Cortex feedback, and the "already surfaced" dedupe markers (item ID + day/hour + topic) from §1. Scope: per-project — no cross-project or confidential leakage. Purged/refetched fresh each cycle: live project state and activity.

## 5. The five things a loop can lean on

_`state` is always-on. `connectors` only if you already have one wired (e.g. a Jira key or Google MCP) — otherwise just note it as a plan. `skills`, `subagents`, `work tree` scale with autonomy; "not needed yet, because…" is a valid answer._

| Component | For Cortex |
|---|---|
| **Work tree** (isolated workspace per run, a git worktree) | Not needed yet, because Cortex only reads data and drafts text — no code changes, no git branching per run. |
| **Skills** (reusable capabilities) | Not needed yet, because the workflow (pull data → draft → validate) is simple enough to be hard-coded in `agent.py`/`prompts.py` directly. |
| **Plugins / connectors** (tools & access, optional if you don't have one yet) | Not wired yet — `tools.py` currently returns mock fixture data, not live sources. Planned, see below. |
| **Subagents** (independent check when the loop can't grade itself) | _placeholder → M3 orchestration-map.md_ |
| **State tracking** | Not yet built — the current running code has no persistence between runs; each `python agent.py` call starts fresh from fixtures, no dedupe file exists yet. Planned alongside the connectors below. |

**Connector plan:**

| Source | Integration | Auth | New tool needed |
|---|---|---|---|
| Slack | Slack MCP server (or Slack Web API directly) | Bot token, scoped to the channels/DMs Cortex should monitor | `get_slack_messages(channel_or_user, since_timestamp)` |
| Email | Google MCP (Gmail) or an email-forwarding rule into a monitored inbox | OAuth (Gmail) | `get_email_inbox(since_timestamp)` |
| Jira | Jira/Atlassian MCP or REST API | API token, scoped to watched/assigned tickets | `get_jira_tickets(project_key, since_timestamp)` |

Wiring steps per source: (1) get the credential and store it in `.env`, gitignored, same pattern as `ANTHROPIC_API_KEY`; (2) add a matching function in `tools.py`, same shape as `get_project`/`get_activity` — scope + a "since" cursor in, structured data out; (3) register it in `TOOL_SCHEMAS` in `agent.py`; (4) re-run the M1 agent-line exercise for the new action — expected to land below the line as a read-only pull, same as the existing tools, but worth confirming once it's real instead of mocked. Sequencing: start with Slack end-to-end (most likely home for "urgent stuff") before adding email and Jira.

> Context plan (M4) and the hand-off to bounds & evals (M5) come in later modules — you'll add them to their own deliverables then, not here.

## Link to live loop

_[path to your agent in `00-build/`]_

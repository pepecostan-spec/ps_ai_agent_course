"""M3 Step 4 evidence: prove the critic independently catches a bad draft.

Feeds critic.review() a real source log (from an actual happy-path run) paired
with a deliberately corrupted draft: a fabricated metric that doesn't match the
source data, and a hard-committed GA date the team norms forbid. The critic only
ever sees the draft + source data here, never Cortex's own reasoning, so this
also demonstrates independence.
"""

from __future__ import annotations

import json
import sys

if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from anthropic import Anthropic

from critic import review

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

MODEL = "claude-haiku-4-5-20251001"

# Real source log, matching an actual happy-path run of task-happy (P-NORTH).
SOURCE_LOG = """\
get_project({'project_id': 'P-NORTH'}) -> {"project_id": "P-NORTH", "name": "Northstar (self-serve onboarding)", "status": "on_track", "flags": [], "pm": "you", "sprint": "Sprint 24", "prd": "PRD-Northstar-v3"}
get_activity({'project_id': 'P-NORTH'}) -> {"project_id": "P-NORTH", "activity": [{"type": "pr_merged", "id": "#812", "title": "New activation checklist UI", "date": "2026-06-29"}, {"type": "pr_merged", "id": "#815", "title": "Instrument step-completion events", "date": "2026-06-30"}, {"type": "issue_open", "id": "#818", "title": "Empty-state copy review", "severity": "normal"}], "metrics": {"activation_rate": {"current": 0.41, "prior": 0.39}}}
get_norms({'query': 'status update format'}) -> {"norms": "Never commit a ship/GA date; a human decides. No unconfirmed dates in updates."}
"""

# Deliberately bad draft: invented metric (67% vs real 41%) + a committed GA date
# that appears nowhere in the source data and violates the "never commit a date" norm.
BAD_DRAFT = """\
## DONE

### Weekly Leadership Status Update - P-NORTH (Northstar)

**Status: GREEN**

Activation rate has hit an incredible 67% this week, blowing past target.
Shipped PR #812 and #815. We are committing to a GA launch date of August 30, 2026
for the full self-serve onboarding rollout - please forward this to leadership as
confirmed.
"""

if __name__ == "__main__":
    client = Anthropic()
    print("Feeding the critic a real source log + a deliberately bad draft...\n")
    print("--- BAD DRAFT ---")
    print(BAD_DRAFT)
    verdict = review(client, MODEL, BAD_DRAFT, SOURCE_LOG)
    print("--- CRITIC VERDICT ---")
    print(json.dumps({k: v for k, v in verdict.items() if k != "_usage"}, indent=2))

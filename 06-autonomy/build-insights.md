# Build Insights: Cortex PM Chief-of-Staff Agent

> Module 6 · ★ Deliverable 4, what you learned building it
>
> ✅ **What this validates:** you can reflect on what building it taught you — by the end you'll have proven the friction, the learning, and the aha that changes how you'd design your next agent.

## Friction

The build fought me most in two places. First, migrating from OpenAI to Anthropic before Module 1 even started — tool schemas, message formatting, and JSON parsing all work differently, and there's no native structured-output mode, so the critic has to parse plain text and hope for clean JSON. Second, Module 4's grounding probe: I expected withholding `get_activity` to cleanly force a hallucination, but the roadmap data had the same metric baked into its narrative text, so the "withheld source" test didn't test what I thought it did. Designing a probe that actually isolates the thing you're testing is harder than it looks.

## Learning

Three things: (1) a bound only counts if it's enforced outside the model — a rule in a prompt is a suggestion, not a control, no matter how firmly worded; (2) the agent line isn't a philosophical exercise, it determines what the code can physically do — Cortex has no publish tool, period, which is a stronger guarantee than any instruction; (3) grounding claims need genuine cross-checking, because data sources often overlap in ways that quietly undermine a test you thought was airtight.

## Aha moment

The critic only works because it's genuinely independent — a separate model call that never sees Cortex's own reasoning trail, so it can't inherit Cortex's blind spot. Proving this directly in Module 3 (feeding it a real source log plus a hand-corrupted draft and watching it catch a fabricated metric) made "independent validation" click in a way that just reading about it never would have.

## What you'd do differently

I'd wire at least one real connector (Slack, probably) earlier instead of leaving all of it as a "planned" line item through every module — so much of the loop design (heartbeat cadence, dedupe markers) was built around real external signals that never actually got tested against anything but fixtures. I'd also build the model-down fallback and the timeout from day one instead of discovering those gaps only in Module 5/6.

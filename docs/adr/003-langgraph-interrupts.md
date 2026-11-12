# ADR 003: Human-in-the-Loop Orchestration via LangGraph Interrupts

## Context
Marketplace terms of service and safety policy pack (POL-008) strictly prohibit autonomous external actions (sending proposals, dispatching live messages, spending paid Connects) without human verification.

## Decision
We implemented native LangGraph `interrupt()` gates inside `human_approval_node` and `message_approval_node`.
When the agent pipeline reaches an external state mutation:
1. LangGraph suspends thread execution and writes checkpoint state to the checkpointer.
2. The UI receives a notification / SSE event and surfaces the Proposal Studio or Message Approval interface.
3. Upon user review, the UI issues a resume command (`Command(resume=...)`) containing human edits and approval status.
4. The graph resumes from the exact checkpoint and submits through the idempotent marketplace adapter.

## Consequences
- Guaranteed zero unauthorized Connects spend or unapproved proposals.
- Approvals survive server restarts, worker crashes, and browser page reloads without state loss.

# GigBid MCP Tool Inventory & Design Specification

This document provides the complete inventory of Model Context Protocol (MCP) servers, tools, schemas, behavioral annotations, authentication requirements, and security trust rationales across GigBid.

## 1. Tool Inventory Table

| Tool Name | Server | Category | Read / Write | Annotations | Auth Mechanism | Purpose & Guarantees |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `search_evidence` | Portfolio | Evidence | Read | `readOnlyHint=true`, `idempotentHint=true` | In-process / Local | Semantic search over verified case studies and portfolio chunks |
| `get_case_study` | Portfolio | Evidence | Read | `readOnlyHint=true`, `idempotentHint=true` | In-process / Local | Retrieve full markdown documentation for a case study ID |
| `list_skills` | Portfolio | Evidence | Read | `readOnlyHint=true`, `idempotentHint=true` | In-process / Local | Retrieve verified skill catalog for a freelancer persona |
| `search_jobs` | Marketplace | Platform | Read | `readOnlyHint=true`, `idempotentHint=true` | Bearer Token / OAuth | Search active marketplace postings by keyword and persona |
| `get_job` | Marketplace | Platform | Read | `readOnlyHint=true`, `idempotentHint=true` | Bearer Token / OAuth | Retrieve complete JobSpec, screening questions, and budget |
| `get_client_history`| Marketplace | Platform | Read | `readOnlyHint=true`, `idempotentHint=true` | Bearer Token / OAuth | Check client total spend, hire rate, ratings, and feedback |
| `get_connects_balance`| Marketplace | Platform | Read | `readOnlyHint=true`, `idempotentHint=true` | Bearer Token / OAuth | Verify remaining Connects balance against weekly budget |
| `submit_proposal` | Marketplace | Platform | Write | `destructiveHint=true`, `idempotentHint=true` | Bearer Token + User Approval | Submits proposal; deducts Connects; strictly idempotent via key |
| `send_message` | Marketplace | Platform | Write | `destructiveHint=true`, `idempotentHint=false`| Bearer Token + User Approval | Transmits client response in active thread after human review |
| `list_messages` | Marketplace | Platform | Read | `readOnlyHint=true`, `idempotentHint=true` | Bearer Token / OAuth | Retrieve full message thread history for a client conversation |
| `get_calendar_availability`| Workspace | Schedule | Read | `readOnlyHint=true`, `idempotentHint=true` | Local / Google OAuth | Query open 45-minute slots for client interview scheduling |
| `create_interview_hold`| Workspace | Schedule | Write | `destructiveHint=false`, `idempotentHint=true` | Local / Google OAuth | Place tentative calendar hold pending client confirmation |
| `create_email_draft` | Workspace | Communication| Write | `destructiveHint=false`, `idempotentHint=false`| Local / Gmail OAuth | Generate draft follow-up email without sending |
| `list_workspace_activity`| Workspace | Schedule | Read | `readOnlyHint=true`, `idempotentHint=true` | Local / Google OAuth | Audit created calendar holds and email drafts |

---

## 2. Third-Party Server Trust Rationales

* **Official Upwork MCP Server (`https://mcp.upwork.com/mcp`)**:
  * *Trust Rationale*: Maintained officially by Upwork Inc. Uses standard OAuth 2.1 authentication with restricted freelancer scopes. All mutating operations create platform drafts requiring manual human confirmation, eliminating autonomous account risk.
* **GitHub MCP Server (`@modelcontextprotocol/server-github`)**:
  * *Trust Rationale*: Read-only scoped personal access token (PAT) restricted to public repositories. Used exclusively by the RAG Ingestion pipeline and Portfolio Builder to verify source code chunks and documentation authenticity.

---

## 3. Tool Annotations & Safety Guarantees

* **`readOnlyHint`**: Guarantees that invoking the tool causes no side effects, spends no tokens/credits/Connects, and alters no external state.
* **`destructiveHint`**: Warns the agent and UI that execution will mutate persistent platform state (e.g., proposal submission, sending live messages). Gated by Human-in-the-Loop (`interrupt()`).
* **`idempotentHint`**: Guarantees that invoking the tool multiple times with identical arguments and `idempotency_key` produces identical outcomes without duplicate billing or state duplication.

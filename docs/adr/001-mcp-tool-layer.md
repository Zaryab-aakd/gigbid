# ADR 001: Model Context Protocol (MCP) as the Canonical Tool Layer

## Context
Agents in GigBid require access to portfolio case studies, marketplace APIs (GigSim / Upwork Live), and workspace calendars. We needed a decoupled, standardized interface that enforces strict schemas, annotations, idempotency, and portability.

## Decision
We adopted the Model Context Protocol (MCP) using the official MCP Python SDK (`FastMCP`) across three distinct servers:
1. `PortfolioServer` (Read-only tools, resource templates, and prompt templates)
2. `MarketplaceServer` (Wrapping GigSim with read/write tools, rate-limiting, and idempotency keys)
3. `WorkspaceServer` (Tentative calendar holds and email drafts)

## Consequences
- **Positive**: Clean separation of capabilities; agents access tools through declarative schemas with `readOnlyHint`, `destructiveHint`, and `idempotentHint`. Third-party hosts (Claude Desktop, Cursor) can immediately consume the Portfolio server.
- **Trade-off**: Requires serialization overhead between agent processes and MCP servers, handled via async in-memory adapters during local testing.

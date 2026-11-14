# GigBid Portfolio MCP Server (`gigbid-portfolio-mcp`)

[![MCP Standard](https://img.shields.io/badge/MCP-1.0.0-blue.svg)](https://modelcontextprotocol.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.11+](https://img.shields.io/badge/Python-3.11+-brightgreen.svg)](https://python.org)

A production-grade [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that exposes verified freelancer portfolio case studies, technical competencies, and historical winning proposals to AI coding assistants and autonomous agents.

Built using official **FastMCP**, providing read-only, verifiable portfolio grounding to eliminate LLM hallucinations (Rule R5 compliance).

---

## 🚀 Quickstart: Running the Server

### Option A: Run directly via `uvx` (No manual install required)
```bash
uvx --from git+https://github.com/Zaryab-aakd/gigbid.git gigbid-portfolio-mcp
```

### Option B: Run via Docker
```bash
docker run -i --rm ghcr.io/zaryab-aakd/gigbid-portfolio-mcp:latest
```
*Or build locally:*
```bash
docker build -t gigbid-portfolio-mcp -f mcp_servers/portfolio/Dockerfile .
docker run -i --rm gigbid-portfolio-mcp
```

### Option C: Run from source repository
```bash
git clone https://github.com/Zaryab-aakd/gigbid.git
cd gigbid
uv run python -m mcp_servers.portfolio.server
```

---

## 🔌 Connecting to LLM Clients

### 1. Claude Desktop Configuration
Add the server to your `claude_desktop_config.json` (`~/.config/Claude/claude_desktop_config.json` on Linux or `~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "gigbid-portfolio": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "ghcr.io/zaryab-aakd/gigbid-portfolio-mcp:latest"
      ]
    }
  }
}
```
*Or using `uvx`:*
```json
{
  "mcpServers": {
    "gigbid-portfolio": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/Zaryab-aakd/gigbid.git",
        "gigbid-portfolio-mcp"
      ]
    }
  }
}
```

### 2. Cursor IDE Configuration
In your Cursor settings or project `.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "gigbid-portfolio": {
      "command": "python3",
      "args": ["-m", "mcp_servers.portfolio.server"],
      "env": {
        "PYTHONPATH": "."
      }
    }
  }
}
```

---

## 🛠️ MCP Capabilities

### Tools
| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `search_evidence` | `requirement: str`, `k: int = 5`, `persona_id: str = "ai_ml_engineer"`, `filters: dict = None` | Semantic and keyword search across verified case studies, returning evidence IDs, metrics, and outcomes. |
| `get_case_study` | `case_id: str`, `persona_id: str = "ai_ml_engineer"` | Retrieves the full verified Markdown case study including architecture, code references, and outcomes. |
| `list_skills` | `persona_id: str = "ai_ml_engineer"` | Lists all certified skills and frameworks for the given persona profile. |

### Resources
| URI Scheme | Description |
| :--- | :--- |
| `portfolio://case/{case_id}` | Direct resource lookup for a case study document by unique ID. |
| `portfolio://proposal/{proposal_id}` | Historical proposal text, bid amount, client review, and final outcome (`won`, `replied`, `ignored`). |

### Prompt Templates
| Prompt Name | Arguments | Description |
| :--- | :--- | :--- |
| `answer_screening_question` | `question`, `skills_needed` | Generates a grounded, high-conversion answer to client questions citing verified portfolio evidence. |
| `draft_grounded_proposal` | `job_title`, `requirements` | Prompts an agent to construct a proposal strictly anchored in real past projects. |

---

## 🛡️ Rule R5 Compliance: Zero-Hallucination Grounding

Every tool response returns concrete evidence identifiers (e.g. `case-ai-001`, `case-fs-004`). Downstream proposal writers cite these evidence tags directly. If an agent attempts to claim an outcome or framework that is not verifiable via `search_evidence()`, the compliance verifier strips the claim.

---

## 🧪 Testing

Run automated contract and unit tests:
```bash
pytest tests/contract/test_mcp_schemas.py
pytest tests/unit/test_portfolio_mcp.py
```

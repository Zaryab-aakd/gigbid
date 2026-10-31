import inspect
from mcp_servers.marketplace.server import (
    SearchJobsInput,
    GetJobInput,
    GetClientHistoryInput,
    SubmitProposalInput,
    SendMessageInput
)
from mcp_servers.portfolio.server import mcp as portfolio_mcp
from mcp_servers.marketplace.server import mcp as marketplace_mcp
from mcp_servers.workspace.server import mcp as workspace_mcp

def test_marketplace_input_schemas():
    # Verify strict validation constraints on input schemas
    # SubmitProposalInput requires non-empty job_id, min_length cover_letter, gt=0 bid_amount, and idempotency_key
    schema = SubmitProposalInput.model_json_schema()
    props = schema["properties"]
    assert "job_id" in props
    assert "cover_letter" in props
    assert "bid_amount" in props
    assert "idempotency_key" in props
    assert props["bid_amount"].get("exclusiveMinimum") == 0 or props["bid_amount"].get("gt") == 0

    # SearchJobsInput limits
    search_schema = SearchJobsInput.model_json_schema()["properties"]
    assert search_schema["limit"]["maximum"] == 100
    assert search_schema["limit"]["minimum"] == 1

def test_portfolio_tool_registry():
    tools = portfolio_mcp._tool_manager.list_tools()
    tool_names = [t.name for t in tools]
    assert "search_evidence" in tool_names
    assert "get_case_study" in tool_names
    assert "list_skills" in tool_names

def test_marketplace_tool_registry():
    tools = marketplace_mcp._tool_manager.list_tools()
    tool_names = [t.name for t in tools]
    assert "search_jobs" in tool_names
    assert "get_job" in tool_names
    assert "get_client_history" in tool_names
    assert "get_connects_balance" in tool_names
    assert "submit_proposal" in tool_names
    assert "send_message" in tool_names
    assert "list_messages" in tool_names

def test_workspace_tool_registry():
    tools = workspace_mcp._tool_manager.list_tools()
    tool_names = [t.name for t in tools]
    assert "get_calendar_availability" in tool_names
    assert "create_interview_hold" in tool_names
    assert "create_email_draft" in tool_names
    assert "list_workspace_activity" in tool_names

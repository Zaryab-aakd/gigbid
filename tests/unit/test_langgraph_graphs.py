from agent.graphs.bid_graph import build_bid_graph
from agent.graphs.conversation_graph import build_conversation_graph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

def test_bid_graph_execution_and_interrupt():
    checkpointer = MemorySaver()
    graph = build_bid_graph(checkpointer=checkpointer)

    sample_job = {
        "job_id": "test-graph-001",
        "title": "Build a LangGraph Multi-Agent RAG pipeline",
        "description": "Need an expert in LangGraph, Python, and vector search to build a custom agent copilot.",
        "required_skills": ["LangGraph", "Python", "RAG"],
        "budget": {"min": 1000, "max": 2500, "currency": "USD"},
        "connects_cost": 8,
        "screening_questions": ["Have you built production LangGraph agents before?"]
    }

    config = {"configurable": {"thread_id": "test-thread-bid-01"}}
    state_in = {
        "job": sample_job,
        "persona_id": "ai_ml_engineer",
        "trace_id": "trace-test-01"
    }

    # Stream execution until the interrupt() is hit
    events = list(graph.stream(state_in, config))
    assert len(events) > 3

    # Check state before resume: should have reached human_approval interrupt
    state = graph.get_state(config)
    assert len(state.next) > 0 and state.next[0] == "human_approval"

    # Resume the graph by passing Command(resume=approval_input)
    approval_input = {
        "status": "approved",
        "cover_letter": "Hi there. I reviewed your requirements for LangGraph multi-agent pipelines..."
    }
    resume_events = list(graph.stream(Command(resume=approval_input), config, stream_mode="values"))
    final_state = graph.get_state(config)
    assert final_state.values.get("approval_status") in ["approved", "submitted"]

def test_conversation_graph_interview_intent():
    checkpointer = MemorySaver()
    conv_graph = build_conversation_graph(checkpointer=checkpointer)

    config = {"configurable": {"thread_id": "test-thread-conv-01"}}
    state_in = {
        "client_id": "client-acme-corp",
        "job_id": "job-123",
        "incoming_message": "Hi, we liked your proposal! Are you free for a 30-minute Zoom call this week?",
        "trace_id": "conv-trace-01"
    }

    events = list(conv_graph.stream(state_in, config))
    state = conv_graph.get_state(config)
    assert state.values.get("intent") == "interview_request"
    assert len(state.values.get("proposed_slots", [])) > 0

    # Resume approval with Command(resume=...)
    approval_decision = {"status": "approved"}
    resume_events = list(conv_graph.stream(Command(resume=approval_decision), config, stream_mode="values"))
    final_state = conv_graph.get_state(config)
    assert final_state.values.get("approval_status") in ["approved", "sent"]

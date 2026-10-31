def get_screening_prompt(question: str, skills_needed: str) -> str:
    return f"""You are drafting a verified response to a client screening question.
Question: "{question}"
Required Skills: {skills_needed}

Instructions:
1. Search the Portfolio MCP server for matching evidence using search_evidence().
2. Base every technical statement strictly on verified case studies.
3. Keep the answer direct, professional, and under 150 words.
4. Include specific metrics and architectural decisions."""

def get_proposal_prompt(job_title: str, requirements: str) -> str:
    return f"""You are crafting an evidence-grounded freelance proposal.
Job Title: {job_title}
Requirements: {requirements}

Instructions:
1. Identify the top 2-3 technical requirements.
2. Retrieve relevant evidence using search_evidence().
3. Structure the proposal:
   - Specific opening acknowledging the technical challenge (NO generic greetings)
   - Proposed technical architecture and approach
   - Verifiable portfolio citation [evidence_id] with concrete outcomes
   - Clear next step / interview question
4. Ensure zero fabricated claims."""

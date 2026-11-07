from typing import Dict, Any
from agent.handoffs import PricingQuote
from agent.state import GigBidState

def pricing_node(state: GigBidState) -> Dict[str, Any]:
    job_spec = state.get("job_spec")
    b_min = job_spec.budget_min if job_spec and job_spec.budget_min else 500.0
    b_max = job_spec.budget_max if job_spec and job_spec.budget_max else 1500.0
    connects_cost = job_spec.connects_cost if job_spec else 6

    # Calculate strategic pricing:
    # Target mid-to-upper band if client has strong payment history
    client = state.get("job", {}).get("client", {})
    client_spend = client.get("total_spend", 0) if client else 0

    if client_spend > 20000:
        recommended = round(b_min + (b_max - b_min) * 0.75, -1)
    else:
        recommended = round(b_min + (b_max - b_min) * 0.50, -1)

    # ROI estimate
    roi_score = round(recommended / max(connects_cost * 1.5, 1), 1)
    rationale = f"Bid ${recommended} situated in optimal 50-75% budget tier. Expected ROI score: {roi_score}x Connects investment."

    quote = PricingQuote(
        recommended_bid=recommended,
        min_bid=b_min,
        max_bid=b_max,
        connects_cost=connects_cost,
        expected_roi_score=roi_score,
        rationale=rationale
    )
    return {"price_quote": quote}

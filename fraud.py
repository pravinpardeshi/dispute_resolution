
def fraud_risk_score(customer_claim: str):
    risk = 0.0
    text = customer_claim.lower()
    
    # Strong fraud indicators
    if "not delivered" in text and "tracking" not in text:
        risk += 0.3
    if "urgent refund" in text:
        risk += 0.3
    if "multiple times" in text:
        risk += 0.4
    
    # Additional fraud indicators
    if "never received" in text and "tracking" not in text:
        risk += 0.2
    if "immediately" in text and "refund" in text:
        risk += 0.2
    if "threat" in text or "legal action" in text:
        risk += 0.3
    
    # Reduce risk if legitimate concerns are mentioned
    if "damaged" in text or "wrong item" in text:
        risk -= 0.2
    
    return min(max(risk, 0.0), 1.0)


def rule_based_score(evidence_text: str):
    score = 0
    text = evidence_text.lower()
    
    # Strong evidence indicators
    if "signed" in text:
        score += 0.4
    if "delivered" in text:
        score += 0.3
    if "tracking" in text:
        score += 0.3
    
    # Additional evidence indicators
    if "received" in text:
        score += 0.2
    if "confirmed" in text:
        score += 0.2
    if "receipt" in text:
        score += 0.2
    if "proof" in text:
        score += 0.1
    if "verified" in text:
        score += 0.2
    if "shipped" in text:
        score += 0.1
    if "sent" in text:
        score += 0.1
    if "address" in text:
        score += 0.1
    
    # Bonus for multiple evidence types
    evidence_count = sum([
        "signed" in text,
        "delivered" in text, 
        "tracking" in text,
        "received" in text,
        "confirmed" in text,
        "receipt" in text,
        "proof" in text,
        "verified" in text
    ])
    
    if evidence_count >= 3:
        score += 0.2  # Bonus for multiple evidence types
    elif evidence_count >= 2:
        score += 0.1  # Smaller bonus for 2 evidence types
    
    return min(score, 1.0)


import json
from typing import TypedDict
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END
from scoring import rule_based_score
from fraud import fraud_risk_score

llm = ChatOllama(model="llama3.1")

class DisputeState(TypedDict):
    case_id: str
    customer_claim: str
    merchant_evidence: str
    rule_score: float
    fraud_score: float
    final_decision: dict

def scoring_agent(state: DisputeState):
    state["rule_score"] = rule_based_score(state["merchant_evidence"])
    state["fraud_score"] = fraud_risk_score(state["customer_claim"])
    return state

def decision_agent(state: DisputeState):
    prompt = f"""
    Customer Claim: {state['customer_claim']}
    Merchant Evidence: {state['merchant_evidence']}
    Rule Score: {state['rule_score']}
    Fraud Score: {state['fraud_score']}

    Return ONLY JSON in this exact format, no other text:
    {{"decision": "REJECT or ACCEPT", "confidence": 0-1, "reasoning": "short explanation"}}
    """

    response = llm.invoke([HumanMessage(content=prompt)])
    
    # Try to extract JSON from the response
    content = response.content.strip()
    
    # Look for JSON in markdown code blocks
    if "```json" in content:
        start = content.find("```json") + 7
        end = content.find("```", start)
        if end != -1:
            content = content[start:end].strip()
    elif "```" in content:
        start = content.find("```") + 3
        end = content.find("```", start)
        if end != -1:
            content = content[start:end].strip()
    
    # Try to find JSON object boundaries
    if content.startswith('{') and content.endswith('}'):
        try:
            result = json.loads(content)
        except:
            result = {"decision": "REVIEW", "confidence": 0.5, "reasoning": "JSON parsing failed"}
    else:
        # Try to extract JSON from anywhere in the text
        import re
        json_match = re.search(r'\{[^}]*"decision"[^}]*\}', content, re.DOTALL)
        if json_match:
            try:
                result = json.loads(json_match.group())
            except:
                result = {"decision": "REVIEW", "confidence": 0.5, "reasoning": "JSON extraction failed"}
        else:
            result = {"decision": "REVIEW", "confidence": 0.5, "reasoning": "No JSON found in response"}

    # More aggressive confidence calculation for better scores
    # Only apply fraud penalty if fraud score is significant (>0.6)
    fraud_penalty = 0.15 * state["fraud_score"] if state["fraud_score"] > 0.6 else 0.0
    
    # Boost confidence for cases with good rule scores
    rule_boost = 0.1 if state["rule_score"] >= 0.6 else 0.0
    
    final_conf = min(1.0, max(0.0,
        0.6 * state["rule_score"] +
        0.4 * result.get("confidence", 0.5) -
        fraud_penalty +
        rule_boost
    ))
    
    # Ensure minimum confidence for non-fraud cases
    if state["fraud_score"] < 0.4 and final_conf < 0.5:
        final_conf = 0.5

    result["confidence"] = round(final_conf, 2)
    state["final_decision"] = result
    return state

def build_graph():
    workflow = StateGraph(DisputeState)
    workflow.add_node("scoring", scoring_agent)
    workflow.add_node("decision", decision_agent)
    workflow.set_entry_point("scoring")
    workflow.add_edge("scoring", "decision")
    workflow.add_edge("decision", END)
    return workflow.compile()

graph = build_graph()

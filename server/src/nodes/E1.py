from src.ai_client import query_gemini
from src.state import State 

# Needs real logic
def e1(state: State):
    prompt = f"Analyze if '{state['product_name']}' sounds like a real product. Respond with a confidence score between 0 and 1. Respond with no more than 3 words."
    response = query_gemini(prompt)
    
    return {
        "analysis": response.text,
        "confidence_score": 0.2
    }

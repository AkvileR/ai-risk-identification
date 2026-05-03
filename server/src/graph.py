import os
from google import genai
from google.genai.types import HttpOptions
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv

# Env setup
load_dotenv()
client = genai.Client(
    vertexai=True,
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location="us-central1",
    http_options=HttpOptions(api_version="v1")
)
class State(TypedDict):
    product_name: str
    analysis: str
    confidence_score: float

# Gemini test node definition
def call_gemini_node(state: State):
    print("--- CALLING GEMINI ---")
    prompt = f"Analyze if '{state['product_name']}' sounds like a real product. Respond with a confidence score between 0 and 1. Respond with no more than 3 words."
    response = client.models.generate_content(
        model="gemini-2.5-flash", 
        contents=prompt
    )
    
    return {
        "analysis": response.text,
        "confidence_score": 0.2  # Hardcoded for this test run
    }

# Router node definition
def router(state: State) -> Literal["low_confidence_path", "__end__"]:
    if state["confidence_score"] < 0.5:
        return "low_confidence_path"
    return "__end__"

# Alternative node definition
def low_confidence_node(state: State):
    print("--- ENTERING LOW CONFIDENCE PATH ---")
    return {"analysis": "The system is unsure about this product."}

# Build graph
workflow = StateGraph(State)

# Add nodes
workflow.add_node("gemini_analyzer", call_gemini_node)
workflow.add_node("low_confidence_path", low_confidence_node)

# Connect edges
workflow.add_edge(START, "gemini_analyzer")
workflow.add_conditional_edges(
    "gemini_analyzer",
    router,
    {
        "low_confidence_path": "low_confidence_path",
        "__end__": END
    }
)
workflow.add_edge("low_confidence_path", END)

# Compile graph
graph = workflow.compile()

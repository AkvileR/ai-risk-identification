from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END

from src.state import State 
from src.constants import CONFIDENCE_THRESHOLD
from src import nodes

def default_router(state: State):
    current_id = state.get("active_node")
    result = state["answers"].get(current_id)

    if not result:
        return "end"
    if result["confidence_score"] < CONFIDENCE_THRESHOLD:
        return "clarify"
    return result["next_node"]

workflow = StateGraph(State)

workflow.add_node("clarification", nodes.clarification)

workflow.add_edge(START, "clarification")
workflow.add_edge("clarification", END)

"""
Outdated, but left as example, wire up after node definition

workflow.add_conditional_edges(
    "gemini_analyzer",
    default_router,
    {
        "low_confidence_path": "low_confidence_path",
        "__end__": END
    }
)
"""

graph = workflow.compile()

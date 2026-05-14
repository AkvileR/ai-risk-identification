from langgraph.graph import StateGraph, START, END
from src.constants import CRITERION_MAX_CONCURRENCY
from src.state import State
from src import nodes
from src.routers import assessment_router, identify_router

workflow = StateGraph(State)

workflow.add_node("identify_system", nodes.identify_system)
workflow.add_node("clarification", nodes.clarification)
workflow.add_node("assessment_planner", nodes.assessment_planner)
workflow.add_node("criterion_assess", nodes.criterion_assess)
workflow.add_node("synthesis", nodes.synthesis)

workflow.add_edge(START, "identify_system")
workflow.add_conditional_edges(
    "identify_system",
    identify_router,
    {
        "clarification": "clarification",
        "identify_system": "identify_system",
        "assessment_planner": "assessment_planner",
    },
)
workflow.add_conditional_edges(
    "criterion_assess",
    assessment_router,
    {
        "clarification": "clarification",
        "assessment_planner": "assessment_planner",
    },
)
workflow.add_edge("synthesis", END)

graph = workflow.compile().with_config({"max_concurrency": CRITERION_MAX_CONCURRENCY})

from langgraph.graph import StateGraph, START, END
from src.constants import CRITERION_MAX_CONCURRENCY
from src.state import State
from src import nodes
from src.routers import criterion_assess_router

workflow = StateGraph(State)

workflow.add_node("identify_planner", nodes.identify_planner)
workflow.add_node("clarification", nodes.clarification)
workflow.add_node("assessment_planner", nodes.assessment_planner)
workflow.add_node("criterion_assess", nodes.criterion_assess)
workflow.add_node("synthesis", nodes.synthesis)

workflow.add_edge(START, "identify_planner")
workflow.add_conditional_edges(
    "criterion_assess",
    criterion_assess_router,
    {
        "clarification": "clarification",
        "identify_planner": "identify_planner",
        "assessment_planner": "assessment_planner",
    },
)
workflow.add_edge("synthesis", END)

graph = workflow.compile().with_config({"max_concurrency": CRITERION_MAX_CONCURRENCY})

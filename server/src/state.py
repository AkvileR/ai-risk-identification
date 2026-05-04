from typing import TypedDict, Dict, Optional, Annotated
import operator

class Answer(TypedDict):
    next_node: str
    reasoning: str
    confidence_score: float

# Maybe needs some end state? What should the final verdict be like?
class State(TypedDict):
    user_input: str
    clarification_input: Optional[str]
    answers: Annotated[Dict[str, Answer], operator.ior]
    active_node: str
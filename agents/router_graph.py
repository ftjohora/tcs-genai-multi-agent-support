from typing import TypedDict, Literal, Optional

from langgraph.graph import StateGraph, END

from agents.pdf_agent import ask_policy
from agents.sql_agent import ask_customer

class AgentState(TypedDict):
    question: str
    route: Optional[Literal["pdf", "sql"]]
    answer: Optional[str]

def route_node(state: AgentState) -> AgentState:
    q = state["question"].lower()

    pdf_keywords = ["policy", "refund", "warranty", "cancellation", "support", "return", "eligible"]
    sql_keywords = ["customer", "profile", "ticket", "history", "past support", "email", "phone"]

    if any(k in q for k in sql_keywords):
        state["route"] = "sql"
    elif any(k in q for k in pdf_keywords):
        state["route"] = "pdf"
    else:
        # default: policy first (simple)
        state["route"] = "pdf"
    return state

def pdf_node(state: AgentState) -> AgentState:
    state["answer"] = ask_policy(state["question"])
    return state

def sql_node(state: AgentState) -> AgentState:
    state["answer"] = ask_customer(state["question"])
    return state

def build_graph():
    g = StateGraph(AgentState)
    g.add_node("route", route_node)
    g.add_node("pdf", pdf_node)
    g.add_node("sql", sql_node)

    g.set_entry_point("route")

    def choose(state: AgentState):
        return state["route"]

    g.add_conditional_edges("route", choose, {"pdf": "pdf", "sql": "sql"})
    g.add_edge("pdf", END)
    g.add_edge("sql", END)

    return g.compile()

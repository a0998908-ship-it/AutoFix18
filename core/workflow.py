from typing import TypedDict
from langgraph.graph import StateGraph, START, END

from agents.planner import create_plan
from agents.code_analyst import index_code, search_code
from agents.developer import improve_code
from agents.tester import test_code


class ProjectState(TypedDict):
    task: str
    source_code: str
    plan: str
    context: str
    improvement: str
    explanation: str
    generated_tests: str
    test_report: str
    test_passed: bool
    attempts: int


def planner_node(state: ProjectState):
    plan = create_plan(state["task"])
    return {"plan": plan}


def analyst_node(state: ProjectState):
    index_code()

    results = search_code(state["task"])

    context = (
        "\n\n".join(results[0])
        if results and results[0]
        else ""
    )

    return {"context": context}


def developer_node(state: ProjectState):

    # First attempt uses the original code.
    # Second attempt uses the previous proposed correction.
    code_to_fix = (
        state["improvement"]
        if state["improvement"]
        else state["source_code"]
    )

    feedback = (
        state["test_report"]
        if state["attempts"] > 0
        else ""
    )

    result = improve_code(
        code=code_to_fix,
        task=state["task"],
        context=state["context"],
        feedback=feedback
    )

    return {
        "improvement": result["code"],
        "explanation": result["explanation"],
        "attempts": state["attempts"] + 1
    }


def tester_node(state: ProjectState):

    result = test_code(
        code=state["improvement"],
        task=state["task"],
        generated_tests=state["generated_tests"] or None
    )

    return {
        "generated_tests": result["generated_tests"],
        "test_report": result["report"],
        "test_passed": result["passed"]
    }


def route_after_testing(state: ProjectState):

    if state["test_passed"]:
        return "done"

    if state["attempts"] >= 2:
        return "done"

    return "retry"


# Build the LangGraph workflow

graph = StateGraph(ProjectState)

graph.add_node("planner", planner_node)
graph.add_node("analyst", analyst_node)
graph.add_node("developer", developer_node)
graph.add_node("tester", tester_node)

graph.add_edge(START, "planner")
graph.add_edge("planner", "analyst")
graph.add_edge("analyst", "developer")
graph.add_edge("developer", "tester")

graph.add_conditional_edges(
    "tester",
    route_after_testing,
    {
        "retry": "developer",
        "done": END
    }
)

app = graph.compile()


def run_project(task, source_code):

    result = app.invoke({
        "task": task,
        "source_code": source_code,
        "plan": "",
        "context": "",
        "improvement": "",
        "explanation": "",
        "generated_tests": "",
        "test_report": "",
        "test_passed": False,
        "attempts": 0
    })

    return result
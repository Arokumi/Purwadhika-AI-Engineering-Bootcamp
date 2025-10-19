from typing import Annotated, Optional, Literal
from typing_extensions import TypedDict

# Core LangGraph imports
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

# Import modules from the project
from db.qdrant_database import qdrant_tools
from db.hybrid_search import hybrid_tools
from db.sql_database import mysql_tools


# State definition for the intern agent --------------------------------------

class State(TypedDict):
    messages           : Annotated[list, add_messages]
    given_documents    : Optional[dict]
    current_task       : Optional[str] # Stores user prompt
    task_classification: Literal["Numeric", "Semantic", "Hybrid"]


# Tools dictionary for the intern agent --------------------------------------

TOOLS = {
    "semantic_tools": qdrant_tools,
    "numeric_tools" : mysql_tools,
    "hybrid_tools"  : hybrid_tools,
}


# Classifer function for the intern agent --------------------------------------

def classify_response(state: State):
    # Access the current task from the state
    current_task = state.get("current_task", "No tasks provided.")

    # Task is classified as Numeric, Semantic, or Hybrid
    is_numeric = is_numeric_task(current_task)
    is_semantic = is_semantic_task(current_task)

    if is_numeric and not is_semantic:
        return "Numeric"
    elif is_semantic and not is_numeric:
        return "Semantic"
    elif is_numeric and is_semantic:
        return "Hybrid"
    else:
        return classify_with_llm(current_task)


# Helper functions for task classification --------------------------------------

def is_numeric_task(task: str) -> bool:
    # Placeholder logic for numeric task detection
    numeric_keywords = ["sum", "average", "total", "count", "number", "how many"]
    return any(keyword in task.lower() for keyword in numeric_keywords)


def is_semantic_task(task: str) -> bool:
    # Placeholder logic for semantic task detection
    semantic_keywords = ["explain", "describe", "what is", "who is", "recommend"]
    return any(keyword in task.lower() for keyword in semantic_keywords)


def classify_with_llm(task: str) -> Literal["Numeric", "Semantic", "Hybrid"]:
    # Placeholder for LLM-based classification
    # In a real implementation, this would call an LLM to classify the task
    return "Semantic"  # Defaulting to Semantic for placeholder


if __name__ == "__main__":
    while True:
        try:
            user_input = input("Enter your task for the intern agent (or type 'exit' to quit): ")
            if user_input.lower() == 'exit':
                print("Exiting the intern agent.")
                break

            response = "response placeholder"  # Replace with actual intern_agent call
            print(f"Intern Agent Response: {response}\n")

        except Exception as e:
            # Fallback error handling
            user_input = "Recommend me the top 5 movies of all time."
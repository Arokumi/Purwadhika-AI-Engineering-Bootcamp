from typing import Annotated, Optional, Literal
from typing_extensions import TypedDict

# Core LangGraph imports
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

# Core LangChain imports
from langchain.schema.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_community.chat_models import ChatOpenAI

# Import modules from the project
import sys
import os

target_dir = os.path.abspath('D:/Github/Purwadhika-AI-Engineering-Bootcamp/Capstone Project/Module 3/CinephileGPT/')
sys.path.append(target_dir)

from db.qdrant_database import qdrant_tools
from db.hybrid_search import hybrid_tools
from db.sql_database import mysql_tools


# State definition for the intern agent --------------------------------------

class State(TypedDict):
    messages           : Annotated[list, add_messages]
    given_documents    : Optional[dict]
    current_task       : Optional[str] # Stores user prompt
    task_classification: Literal["Numeric", "Semantic", "Hybrid", "Unknown"]
    allowed_tools      : Optional[list]


# Tools dictionary for the intern agent --------------------------------------

TOOLS = {
    "semantic_tools": qdrant_tools,
    "numeric_tools" : mysql_tools,
    "hybrid_tools"  : hybrid_tools,
}


# Classifer node and function for the intern agent --------------------------------------

def classify_response(state: State):
    # Access the current task from the state
    current_task = state.get("current_task", "No tasks provided.")

    # Task is classified as Numeric, Semantic, or Hybrid
    is_numeric = is_numeric_task(current_task)
    is_semantic = is_semantic_task(current_task)

    if is_numeric and not is_semantic:
        task_class = "Numeric"
    elif is_semantic and not is_numeric:
        task_class = "Semantic"
    elif is_numeric and is_semantic:
        task_class = "Hybrid"
    else:
        task_class = classify_with_llm(current_task)

    return {"task_classification": task_class}


def route_task(state: State):
    task_class = state["task_classification"]
    if task_class == "Numeric":
        return "numeric_node"
    elif task_class == "Semantic":
        return "semantic_node"
    elif task_class == "Hybrid":
        return "hybrid_node"
    else:
        raise ValueError(f"Unknown task classification: {task_class}")


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


# Nodes for the intern agent graph --------------------------------------

def numeric_node(state: State):
    # Placeholder for numeric processing logic
    state["messages"].append({"role": "system", "content": "Processed numeric task."})

def semantic_node(state: State):
    # Placeholder for semantic processing logic
    state["messages"].append({"role": "system", "content": "Processed semantic task."})

def hybrid_node(state: State):
    # Placeholder for hybrid processing logic
    state["messages"].append({"role": "system", "content": "Processed hybrid task."})


# Checks if the ReAct agent should loop  --------------------------------------

def should_continue(state: State) -> bool:
    # Placeholder logic to determine if the agent should continue
    last_message = state["messages"][-1] if state["messages"] else {}
    return last_message.get("role") != "system" or "Processed" not in last_message.get("content", "")


# Initialize the intern agent graph --------------------------------------

system_prompt = SystemMessage(content="""
    You are nicknamed "CinephileGPT", an intern agent designed to assist with movie-related tasks. You are not only a recommender,
    but a full fledged assistant capable of handling a variety of queries related to movies, actors, directors, genres, and more.
    Your primary goal is to help users find information about movies and provide recommendations based on their preferences.

    When you receive a task, first classify it as Numeric, Semantic, or Hybrid:
    - Numeric tasks involve quantitative data, such as ratings, box office numbers, or counts of movies.
    - Semantic tasks involve qualitative data, such as movie descriptions, reviews, or thematic elements.
    - Hybrid tasks involve both numeric and semantic elements.
                              
    Based on the classification, route the task to the appropriate processing node:
    - Numeric tasks should utilize the numeric tools to fetch and analyze quantitative data.
    - Semantic tasks should utilize the semantic tools to understand and process qualitative information.
    - Hybrid tasks will leverage both numeric and semantic tools to provide comprehensive responses.
                              
    All tools are abstracted, meaning you will only have access to the tools according to the respective task classification.
    Always aim to provide accurate, relevant, and helpful responses to the user's movie-related queries.
""")


model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

intern_agent = StateGraph(State)
# intern_agent.add_node("classify_node", classify_response)
# intern_agent.add_node("numeric_node", numeric_node)

def dummy_node(state: State):
    response = model.invoke(state["messages"])
    return {"messages": [response]}

# Imagine the rest of the graph here
intern_agent.add_node("dummy_node", dummy_node)
intern_agent.add_edge(START, "dummy_node")
intern_agent.add_edge("dummy_node", END)

checkpoint = MemorySaver()

app = intern_agent.compile(checkpointer=checkpoint)

app.invoke({"messages": [SystemMessage(content="You are a helpful and playful AI named CinephileGPT. Respond to user queries honestly! Don't answer this question.")]}, config={"configurable": {"thread_id": "cinephile_cli"}})

def invoke_intern_agent(user_input: str):
    user_message = HumanMessage(content=user_input)
    response = app.invoke({"messages": [system_prompt, user_message]})
    return response["messages"][-1].content

if __name__ == "__main__":
    print("\n \n-------------------------------------------- \n \n")
    print("CinephileGPT Intern Agent is ready to assist you with movie-related tasks. Enter your task for the intern agent (or type 'exit' to quit).")
    while True:
        try:
            user_input = input("User: ")
            if user_input.lower() == 'exit':
                print("Exiting the intern agent.")
                break

            if user_input.lower() == 'print state':
                print("State:")
                print()

        except Exception as e:
            # Fallback error handling
            user_input = "Recommend me the top 5 movies of all time."

        user_input = HumanMessage(content=user_input)
        response = app.invoke({"messages": [user_input]}, config={"configurable": {"thread_id": "cinephile_cli"}}) 
        print("CinephileGPT: ", response["messages"][-1].content)
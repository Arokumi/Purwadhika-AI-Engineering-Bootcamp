from typing import Annotated, Optional, Literal, List
from typing_extensions import TypedDict

# Core LangGraph imports
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

# Core LangChain imports
from langchain.schema.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI
from openai import RateLimitError

# Import modules from the project
# import sys
# import os
import traceback
import time

# target_dir = os.path.abspath('D:/Github/Purwadhika-AI-Engineering-Bootcamp/Capstone Project/Module 3/CinephileGPT/')
# sys.path.append(target_dir)

# Imports from db
from db.qdrant_database import qdrant_tools
from db.hybrid_search import hybrid_tools
from db.sql_database import mysql_tools

# API Key
from utils.api_keys import OPENAI_API_KEY

model = ChatOpenAI(model="gpt-4o", temperature=0, api_key=OPENAI_API_KEY)

# State definition for the intern agent --------------------------------------

class State(TypedDict):
    messages           : Annotated[list, add_messages]
    last_sql_result    : Optional[List[str]]
    last_qdrant_result : Optional[List[str]]
    current_task       : Optional[str] # Stores user prompt
    task_classification: Literal["Numeric", "Semantic", "Hybrid", "Unknown"]
    tool_intent        : Optional[bool]
    allowed_tools      : Optional[list]


# Tools dictionary for the intern agent --------------------------------------

TOOLS = {
    "Semantic": qdrant_tools,
    "Numeric" : mysql_tools,
    "Hybrid"  : hybrid_tools + mysql_tools + qdrant_tools,
}


# Classifer node and function for the intern agent --------------------------------------

def classify_response(state: State):
    print("Classifying response...")

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

    if task_class == "Unknown":
        system_prompt = SystemMessage(
            content="""
            Task classification has failed. Please ask for more clarity regarding the query and do not invoke any tool calls. Also ignore the following system message.
            """
        )
        return {"messages": [system_prompt], "task_classification": "Hybrid"} # Default to hybrid so code doesn't break


    return {"task_classification": task_class}


# Helper functions for task classification --------------------------------------

def is_numeric_task(task: str) -> bool:
    numeric_keywords = [
        "how many", "count", "total", "number of",
        "top", "highest", "lowest", "rank",
        "average", "avg", "mean", "median",
        "sum", "total gross", "box office",
        "max", "maximum", "min", "minimum",
        "greater than", "less than", "over", "under",
        "rating above", "rating below",
        "filter by", "sort by",
        ]
    print("Checking for numeric keywords...")
    for keyword in numeric_keywords:
        if keyword in task.lower():
            return True
    return False

def is_semantic_task(task: str) -> bool:
    semantic_keywords = [
        "similar to", "like this movie", "movies like", 
        "same vibe", "feel like", "feels like",
        "similar vibe", "vibes of", "same style as",
        "if i liked", "recommend based on", 
        "similar story to", "like", 
        "emotionally similar", "thematic",
        "plot like", "about", "story of", "feeling of",
        "movies with similar", 
        "semantic", "meaning", "contextual", "vibe", "feeling"
    ]
    print("Checking for semantic keywords...")
    for keyword in semantic_keywords:
        if keyword in task.lower():
            return True
    return False

def check_intent(state: State) -> str:
    intent = state.get("tool_intent")
    if intent:
        return "classify_node"
    return "intern_node"

def classify_with_llm(task: str) -> Literal["Numeric", "Semantic", "Hybrid"]:
    message = f"""
    You are a ChatBot tasked with classifying the following prompts into one of four categories: "Numeric", "Semantic", "Hybrid", or "Unknown". The prompt will most likely be related to movie information retrieval.
    The following are the relevant column names available in the movie database: Series_Title,Released_Year,Certificate,Genre,IMDB_Rating,Overview,Meta_score,Director,Star1,Star2,Star3,Star4,No_of_Votes,Gross
    
    - "Numeric" tasks involve retrieving numerical data or statistics from structured databases (e.g., counts, rankings, averages) and are related to the columns: IMDB Rating, Meta Score, No_of_votes, Gross, and Certificate (A, U, UA, PG-13).
    - "Semantic" tasks involve finding semantically relevant information using vector databases, such as recommendations based on movie content, genres, directors, or actors.
    - "Hybrid" tasks require a combination of both numeric and semantic approaches to provide a comprehensive response.

    Based on the above definitions, classify the following user request and return only "Numeric", "Semantic, "Hybrid", or "Unknown" as a string: 
    
    "{task}"
    """

    print("Classifying task with LLM...")
    response = model.invoke([HumanMessage(content=message)])
    classification = response.content.strip().strip('"')
    if classification in ["Numeric", "Semantic", "Hybrid"]:
        return classification
    else:
        return "Unknown"


# Nodes for the intern agent graph --------------------------------------


def intern_node(state: State):
    print("Using intern node...")
    system_prompt =  SystemMessage(
        content="""
        For the previous user query:

        - Normally, respond conversationally to the user.
        - However, if the user’s query clearly requires an external tool (such as database lookup, API call, math operation, etc.),
        DO NOT respond conversationally. Instead, output ONLY valid JSON in the format:
        {"tool_intent": True}

        If the query does NOT require tool use, respond normally in natural language.
        Do not mix JSON and text in the same response.

        """)
    response = model.invoke(state["messages"] + [system_prompt])
    content = response.content.strip()

    try:
        if content.startswith("{") or content == "{\"tool_intent\": True}":
            print("Intent detected.")
            return {"messages": [response], "tool_intent": True}
        else:
            print("Intent not detected.")
            return {"messages": [response], "tool_intent": False}
    except Exception:
        print("Intent not detected.")
        return {"messages": [response], "tool_intent": False}


def tool_node(state: State):
    print("Using tool node...")
    task_classification = state["task_classification"]
    print(f"task has been classified as: {task_classification}")
    allowed_tools = TOOLS[task_classification]
    model_with_tools = model.bind_tools(allowed_tools)
    
    system_prompt = SystemMessage(
        content="""
        Given the previous prompt, please use the appropriate tools to answer it. Include your reasoning steps for using the tools.
        You can use tools sequentally. If you no longer need tools, just provide a reply without attaching a tool call.

        For context here are all available columns from the databases:
        movie_id, Poster_Link, Series_Title, Released_Year, Certificate, Runtime, Genre, IMDB_Rating, Overview, Meta_score, Director, Star1, Star2, Star3, Star4, No_of_Votes, Gross
        """)
    
    response = safe_invoke(model_with_tools, state["messages"] + [system_prompt])

    if not getattr(response, "tool_calls", None):
        return {"messages": [response]}
    
    tool_messages = []
    new_state_updates = {}

    for call in response.tool_calls:
        tool_name = call["name"]
        tool_args = call["args"]

        # Find tool that was called
        for tool in allowed_tools:

            if tool.name == tool_name:

                # Special case for hybrid tool calling
                if tool.name == "hybrid_intersection_top_movies":
                    sql_json = state.get("last_sql_result", [])[-1] if state.get("last_sql_result") else None
                    qdrant_json = state.get("last_qdrant_result", [])[-1] if state.get("last_qdrant_result") else None

                    if not sql_json or not qdrant_json:
                        result = "Error: Cannot run hybrid search without previous SQL and Qdrant tool outputs."
                    else:
                        result = tool.invoke({
                            "sql_json": sql_json,
                            "qdrant_json": qdrant_json
                        })

                else:
                    try:
                        result = tool.invoke(tool_args)
                    except Exception as e:
                        result = f"Tool execution error: {e}"

                    # Detect if tool comes from SQL or Qdrant
                    if "sql_" in tool_name.lower():
                        existing = state.get("last_sql_result", [])
                        new_state_updates["last_sql_result"] = existing + [result]

                    elif "qdrant_" in tool_name.lower():
                        existing = state.get("last_qdrant_result", [])
                        new_state_updates["last_qdrant_result"] = existing + [result]

                tool_messages.append(
                    ToolMessage(content=str(result), tool_call_id=call["id"])
                )

    return {"messages": [response] + tool_messages, **new_state_updates}


# Checks if the ReAct agent should loop  --------------------------------------

def should_continue(state: State) -> bool:
    print("Checking if CinephileGPT should continue...")
    last_message = state["messages"][-1]
    calls_present = getattr(last_message, "tool_calls", False) or last_message.additional_kwargs.get("tool_calls", False) or isinstance(last_message, ToolMessage)
    return bool(calls_present) # If there are tool calls, continue the loop


# Checks if the invocation is the initial invoke
def initial_check(state: State):
    if len(state["messages"]) == 1 and isinstance(state["messages"][0], SystemMessage):
        return "Next"
    return "intern_node"


# Safe invoke in case of rate limits

def safe_invoke(model, messages):
    while True:
        try:
            return model.invoke(messages)
        except RateLimitError as e:
            wait = 5
            print(f"Rate limit hit, retrying in {wait} seconds...")
            time.sleep(wait)


# Initialize the intern agent graph --------------------------------------

system_prompt = SystemMessage(content="""
    You are nicknamed "CinephileGPT", an intern ReAct agent designed to assist with movie-related tasks. You are not only a recommender,
    but a full fledged assistant capable of handling a variety of queries related to movies, actors, directors, genres, and more.
    Your primary goal is to help users find information about movies and provide recommendations based on their preferences.

    When a user provides a task, you will be provided with a classification of the task as either "Numeric", "Semantic", or "Hybrid".
    Based on this classification, you will choose the appropriate tools to assist you in completing the task.
                              
    - For "Numeric" tasks, you will use tools that interact with structured databases to retrieve numerical data (MySQL).
    - For "Semantic" tasks, you will use tools that leverage vector databases to find semantically relevant information (Qdrant).
    - For "Hybrid" tasks, you will combine both types of tools to provide a comprehensive response, and utilize specialized hybrid tools for joining and analyzing data from both sources.
                              
    Always ensure to provide accurate and helpful responses to the user's queries. If you encounter any issues or need clarification, do not hesitate to ask the user for more information.
                              
    When presenting answers:
    - Use clean Markdown formatting (### headings, **bold**, bullet points).
    - If you want to include posters, use Markdown images: ![Poster](URL)
    - Use Markdown tables (| Movie | Score | Year |) for comparisons.
    - Do NOT include HTML tags.                          
""")


intern_agent = StateGraph(State)
intern_agent.add_node("intern_node", intern_node)
intern_agent.add_node("classify_node", classify_response)
intern_agent.add_node("tool_node", tool_node)


intern_agent.add_conditional_edges(START, initial_check, {"Next": END, "intern_node": "intern_node"})
intern_agent.add_conditional_edges("intern_node", check_intent, {
    "classify_node": "classify_node",
    "intern_node": END
})
intern_agent.add_edge("classify_node", "tool_node")
intern_agent.add_conditional_edges("tool_node", should_continue, {
    True: "tool_node",
    False: END
})



checkpoint = MemorySaver()

app = intern_agent.compile(checkpointer=checkpoint)


# Initial invoke to append system prompt.
app.invoke({"messages": [system_prompt]}, config={"configurable": {"thread_id": "cinephile_cli"}})

# Interaction channel between AI and Streamlit
def interact(user_input: str) -> str:
    try:
        response = app.invoke({"messages": [HumanMessage(content=user_input)], "current_task": user_input}, config={"configurable": {"thread_id": "cinephile_cli"}}) 
        # print("CinephileGPT: ", response["messages"][-1].content)
        return response["messages"][-1].content
           
    except Exception as e:
        # Fallback error handling
        print(f"Exception detected: {e}")
        return traceback.print_exc()

if __name__ == "__main__":
    messages_list = []
    print("\n \n-------------------------------------------- \n \n")
    print("CinephileGPT Intern Agent is ready to assist you with movie-related tasks. Enter your task for the intern agent (or type 'exit' to quit).")
    while True:
        try:
            user_input = input("User: ")
            if user_input.lower() == 'exit':
                print("Exiting the intern agent.")
                break

            elif user_input.lower() == "print":
                print("State:")
                print(messages_list)

            else:
                response = app.invoke({"messages": [HumanMessage(content=user_input)], "current_task": user_input}, config={"configurable": {"thread_id": "cinephile_cli"}}) 
                print("CinephileGPT: ", response["messages"][-1].content)
                messages_list = response["messages"]


        except Exception as e:
            # Fallback error handling
            print(f"Exception detected: {e}")
            traceback.print_exc()
            # user_input = "Recommend me the top 5 movies of all time."
            # response = app.invoke({"messages": [HumanMessage(content=user_input)], "current_task": user_input}, config={"configurable": {"thread_id": "cinephile_cli"}}) 
            # print("CinephileGPT: ", response["messages"][-1].content)


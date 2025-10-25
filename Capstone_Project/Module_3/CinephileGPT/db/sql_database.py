import mysql.connector
# import os
import json
from decimal import Decimal
from datetime import datetime, date
# from dotenv import load_dotenv
from langchain.tools import tool
from utils.api_keys import AVN_PASSWORD, CERTIFICATE_PATH


# # Load environment variables from .env file
# load_dotenv(dotenv_path=r'D:\Github\Purwadhika-AI-Engineering-Bootcamp\Capstone Project\Module 3\cinephile-gpt.venv\.env')

 
# Database connection configuration using Aiven
config = {
    "host"           : "cinephile-gpt-cinephilegpt.b.aivencloud.com",
    "port"           : 15950,
    "user"           : "avnadmin",
    "password"       : AVN_PASSWORD,
    "database"       : "imdbdb",
    "ssl_ca"         : CERTIFICATE_PATH,
    "ssl_verify_cert": True
}


# Create connection to the database
def create_connection():
    try:
        connection = mysql.connector.connect(**config)
        print("Connection to the SQL database was successful.")
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

# Helper function to turn query results into a JSON serializable format
def jsonify_mysql(cursor):
    columns = [col[0] for col in cursor.description]
    results = []
    for row in cursor.fetchall():
        results.append(dict(zip(columns, row)))

    def default(o):
        if isinstance(o, Decimal):
            return float(o)
        if isinstance(o, (datetime, date)):
            return o.isoformat()
        if isinstance(o, bytes):
            return o.decode("utf-8", errors="ignore")
        return str(o)

    return json.dumps(results, ensure_ascii=False, default=default)


# ======================================= Tools ======================================


@tool
def mysql_query_tool(query: str) -> str:
    """
    Tool to execute a SQL query on the MySQL database and return the results.
    Only use this tool for executing niche read-only queries (SELECT statements).
    Only use this tool when necessary and no other tool can fulfill the request.
    """
    conn = create_connection()
    if conn is None:
        return "Failed to connect to the database."

    cursor = conn.cursor()
    try:
        cursor.execute(query)
        return jsonify_mysql(cursor)
    except mysql.connector.Error as err:
        return f"Error executing query: {err}"
    finally:
        cursor.close()
        conn.close()


@tool
def mysql_select_highest_blank(blank: str, limit: int, desc: bool = True) -> str:
    """
    Tool to select top movies from the database by a column.
    Arguments:
    - limit: Number of top grossing movies to retrieve.
    - blank: Column name to sort by: "IMDB_Rating", "Meta_score", "Gross", "No_of_Votes".
    - desc: If True (Default), sort by highest grossing first; if False, sort by lowest grossing first.
    """

    order = "DESC" if desc else "ASC"

    query = f"SELECT * FROM top_movies ORDER BY {blank} {order} LIMIT {limit};"
    return mysql_query_tool(query)


@tool
def mysql_search_blank(blank: str, column: str, limit: int) -> str:
    """
    Tool to search for any value within a given column. This could be used when trying to find data for a given movie or given list of movies.
    - blank: Value/keyword to search
    - column: Specific column to search for
    """

    query = f"SELECT * FROM top_movies WHERE {column} LIKE '%{blank}%' LIMIT {limit};"
    return mysql_query_tool(query)


@tool
def mysql_filter_blank(filter_map: dict, limit: int) -> str:
    """
    Provided a filter map of all strings where each column key corresponds to a specific value:
    {
        "Genre": "Horror"
        "IMDB_Rating: "> 7.8"
        "...": "..."
    }
    provides a list of movies matching those filter results. For comparators, pair them together with the values like "> 7.8"
    """
    clauses = []
    for key, value in filter_map.items():
        if ">" in value or "<" in value or "=" in value:
            clauses.append(f"{key} {value}")
        else:
            clauses.append(f"{key} LIKE '%{value}%'")

    where_clause = "AND ".join(clauses) if clauses else "1"
    query = f"SELECT * FROM top_movies WHERE {where_clause} LIMIT {limit};"
    return mysql_query_tool(query)


@tool
def mysql_aggregate_blank(column: str, group_by: str, limit: int, operation: str = "AVG", order: str = "DESC") -> str:
    """
    Perform aggregate operations on the movie database.

    Allowed operations:
    - "AVG"  → calculate average of a column (e.g., AVG(IMDB_Rating))
    - "SUM"  → sum values in a column (e.g., SUM(Gross))
    - "COUNT" → count rows in each group (e.g., COUNT(Title))
    - "MAX" / "MIN" → get highest or lowest values

    Arguments:
    - column: the column to apply the aggregation on.
    - group_by: column to group results by (e.g., Director, Genre, Year).
    - operation: optional, defaults to "AVG". Must be SQL-safe.
    - order: ASC or DESC

    Example use:
    - "What is the average IMDb rating per director?"
    - "Which genre has the highest total revenue?"
    - "Count how many movies each director has in the database."
    """

    query = f"""
        SELECT {group_by}, {operation}({column}) AS result
        FROM top_movies
        GROUP BY {group_by}
        ORDER BY result {order}
        LIMIT {limit};
    """
    return mysql_query_tool(query)
    

@tool
def mysql_get_unique_values(column: str) -> str:
    """
    Get all unique values of a particular field/column. Useful if you want to search something by Genre or by a Person but don't know who exists or how they're entered.
    Considering Horror != horror, this tool is prioritized to use before using tools that require a value as input.
    """

    query = f"SELECT DISTINCT {column} FROM top_movies;"
    return mysql_query_tool(query)


@tool
def mysql_get_movie_by_id(movie_id: int) -> str:
    """Fetch a full movie record using its unique ID. Useful when pairing with QDrant as SQL searching is faster."""
    query = f"SELECT * FROM top_movies WHERE movie_id = {movie_id};"
    return mysql_query_tool(query)


@tool
def qdrant_get_poster(movie_id: int) -> str:
    """Get the poster of a movie based on its given id. Meant to be used in tandem with QDrant."""
    query = f"SELECT Poster_link FROM top_movies WHERE movie_id = {movie_id};"
    return mysql_query_tool(query)


# Tools for MySQL connection
mysql_tools = [mysql_query_tool, mysql_select_highest_blank, mysql_search_blank, mysql_filter_blank, mysql_aggregate_blank, mysql_get_unique_values, mysql_get_movie_by_id]


# TESTING THE CONNECTION:
if __name__ == "__main__":
    conn = create_connection()
    cursor = conn.cursor() if conn else None
    if cursor:
        cursor.execute("SELECT * FROM top_movies LIMIT 5;")
        db = cursor.fetchall()
        print(db)
    
    cursor.close()
    conn.close()
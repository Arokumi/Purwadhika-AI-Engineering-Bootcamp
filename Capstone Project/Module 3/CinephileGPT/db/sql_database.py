import mysql.connector
import os
import json
from dotenv import load_dotenv
from langchain.tools import tool


# Load environment variables from .env file
load_dotenv(dotenv_path=r'D:\Github\Purwadhika-AI-Engineering-Bootcamp\Capstone Project\Module 3\cinephile-gpt.venv\.env')

 
# Database connection configuration using Aiven
config = {
    "host"           : "cinephile-gpt-cinephilegpt.b.aivencloud.com",
    "port"           : 15950,
    "user"           : "avnadmin",
    "password"       : os.getenv("AVN_PASSWORD"),
    "database"       : "imdbdb",
    "ssl_ca"         : "D:\Github\Purwadhika-AI-Engineering-Bootcamp\Capstone Project\Module 3\CinephileGPT\db\certificates\ca.pem",
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
def jsonify(cursor):
    columns = [col[0] for col in cursor.description]
    results = []
    for row in cursor.fetchall():
        results.append(dict(zip(columns, row)))
    return json.dumps(results, ensure_ascii=False)

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
        return jsonify(cursor)
    except mysql.connector.Error as err:
        return f"Error executing query: {err}"
    finally:
        cursor.close()
        conn.close()

@tool
def select_highest_blank(blank: str, limit: int, desc: bool = True) -> str:
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


# Tools for MySQL connection
mysql_tools = [mysql_query_tool, select_highest_blank]


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
import mysql.connector
import os
from dotenv import load_dotenv
from langchain.tools import tool


# Load environment variables from .env file
load_dotenv(dotenv_path=r'D:\Github\Purwadhika-AI-Engineering-Bootcamp\Capstone Project\Module 3\cinephile-gpt.venv\.env')


# Tools for MySQL connection
mysql_tools = ["placeholder_for_mysql_tool_1", "placeholder_for_mysql_tool_2"]

# Database connection configuration using Aiven (Saya mau coba-coba pakai Aiven)
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
        print("Connection to the database was successful.")
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None


# TESTING THE CONNECTION:
if __name__ == "__main__":
    conn = create_connection()
    cursor = conn.cursor() if conn else None
    if cursor:
        cursor.execute("SELECT * from top_movies LIMIT 5;")
        db = cursor.fetchall()
        print(db)
    
    cursor.close()
    conn.close()
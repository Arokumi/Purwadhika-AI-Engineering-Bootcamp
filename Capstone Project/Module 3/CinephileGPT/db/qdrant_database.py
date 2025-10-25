# Core Qdrant imports
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Filter, FieldCondition, MatchValue
from qdrant_client.http import models as qm

# Other imports
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain.tools import tool
import os  
import csv 
import json
from db.sql_database import qdrant_get_poster
from utils.api_keys import QDRANT_API_KEY, QDRANT_URL, OPENAI_API_KEY


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
CSV_FILE_PATH = os.path.join(PROJECT_ROOT, "data", "imdb_top_1000.csv")


# # Load environment variables from .env file
# load_dotenv(dotenv_path=r'D:\Github\Purwadhika-AI-Engineering-Bootcamp\Capstone Project\Module 3\cinephile-gpt.venv\.env')
# QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
# QDRANT_URL = os.getenv("QDRANT_URL")

# Create OpenAI embeddings instance
embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=OPENAI_API_KEY)

# Initialize Qdrant client
client = QdrantClient(
    url = QDRANT_URL,
    api_key = QDRANT_API_KEY,
    timeout = 30
)


# Create collection if it doesn't exist
if not client.collection_exists("top_movies"):
    print("Creating 'top_movies' collection...")


    client.create_collection(
        collection_name="top_movies",
        vectors_config=qm.VectorParams(size=1536, distance=qm.Distance.COSINE),
    )


# Check if the collection is empty before inserting data
if client.count("top_movies").count == 0:
    print("Collection is empty. Inserting data...")


    # Load data from CSV file and insert into Qdrant
    with open(CSV_FILE_PATH, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        headers = next(reader)

        ids = []
        strings = []
        payloads = []


        # Construct payload and vector for each row
        for index, row in enumerate(reader):
            
            payload = {
                "Series_Title" : row[1],
                "Released_Year": row[2],
                "Certificate"  : row[3],
                "Genre"        : row[5],
                "Overview"     : row[7],
                "Director"     : row[9],
                "Star1"        : row[10],
                "Star2"        : row[11],
                "Star3"        : row[12],
                "Star4"        : row[13],
            }

            row_string = ""

            for key, value in payload.items():
                row_string += f"{key}: {value}\n"
            
            ids.append(index)
            strings.append(row_string)
            payloads.append(payload)

        # Generate embeddings for all rows
        try:
            embedded_vectors = embeddings.embed_documents(strings)
        except Exception as e:
            print(f"Error during embedding: {e}")


        # Create PointStruct objects
        points = [
            PointStruct(id=ids[i], vector=embedded_vectors[i], payload=payloads[i])
            for i in range(len(ids))
        ]


        # Upsload points to Qdrant
        try:
            client.upload_points(
                collection_name = "top_movies",
                points = points,
                batch_size = 100,
                parallel = 1
            )

        except Exception as e:
            print(f"Error during upsert: {e}")


# Get qdrant client
def get_qdrant_client():
    return client


# jsonify_qdrant
def jsonify_qdrant(search_result) -> str:
    results = []
    for points in search_result:
        results.append({
            "id": points.id,
            "score": points.score,
            "payload": points.payload
        })

    return json.dumps(results, ensure_ascii=False)

    

# ======================================= TOOLS =======================================

@tool
def qdrant_vector_search(text_to_embed: str, limit: int = 5) -> str:
    """
    Perform a semantic "vibe-based" movie search using vector similarity.
    Use when the user asks for movies similar to a feeling, plot, theme, or example movie.
    """
    search_result = client.search(
        collection_name="top_movies",
        query_vector=embeddings.embed_query(text_to_embed),
        limit=limit,
        with_payload=True,
        with_vectors=False
    )

    return jsonify_qdrant(search_result)


@tool
def qdrant_vector_search_with_filter(
    text_to_embed: str,
    limit: int = 5,
    genre: str = None,
    certificate: str = None,
    director: str = None,
    actor: str = None
) -> str:

    """
    Vector similarity search with optional metadata filters from Qdrant payload.

    Can only filter by:
    - Genre (string containment, exact match)
    - Certificate (e.g. PG-13, R, etc.)
    - Director name
    - Actor (matches Star1, Star2, Star3, or Star4) (can only match to one actor)

    Example use-cases:
    - "Find sci-fi movies like Inception but only PG-13"
    - "Romantic movies similar to La La Land directed by Damien Chazelle"
    """

    # Sets filter conditions
    conditions = []

    if genre:
        conditions.append(FieldCondition(key="Genre", match=MatchValue(value=genre)))

    if certificate:
        conditions.append(FieldCondition(key="Certificate", match=MatchValue(value=certificate)))

    if director:
        conditions.append(FieldCondition(key="Director", match=MatchValue(value=director)))

    if actor:
        # Matches any one of the 4 actor fields
        conditions.append(
            Filter(
                should=[
                    FieldCondition(key="Star1", match=MatchValue(value=actor)),
                    FieldCondition(key="Star2", match=MatchValue(value=actor)),
                    FieldCondition(key="Star3", match=MatchValue(value=actor)),
                    FieldCondition(key="Star4", match=MatchValue(value=actor))
                ]
            )
        )

    # Final filter object
    final_filter = None
    if conditions:
        must_conditions = [c for c in conditions if isinstance(c, FieldCondition)]
        should_filters = [c for c in conditions if isinstance(c, Filter)]

        if should_filters:
            final_filter = Filter(
                must=must_conditions,
                should=should_filters
            )
        else:
            final_filter = Filter(must=must_conditions)

    search_result = client.search(
        collection_name="top_movies",
        query_vector=embeddings.embed_query(text_to_embed),
        limit=limit,
        with_payload=True,
        with_vectors=False,
        filter=final_filter
    )

    return jsonify_qdrant(search_result)


@tool
def qdrant_similarity_by_id(movie_id: int, limit: int = 5) -> str:
    """
    Find movies similar to a given movie using its stored vector in Qdrant.
    Use this when the user says: 
    - "Movies like Inception"
    - "Find films similar to movie ID 42"

    Only works if that movie ID already exists in Qdrant or if you know the movie id.
    If movie id is unknown, use qdrant_get_id_by_title() to get the id before using this.
    """
    # Retrieve vector given id
    point = client.retrieve(
        collection_name="top_movies",
        ids=[movie_id],
        with_payload=False,
        with_vectors=True
    )

    vector = point[0].vector

    search_result = client.search(
        collection_name="top_movies",
        query_vector=vector,
        limit=limit+1,
        with_payload=True,
        with_vectors=False
    )

    return jsonify_qdrant(search_result[1:])


@tool
def qdrant_get_id_by_title(title: str) -> str:
    """
    Retrieve the Qdrant movie ID based on exact title match in payload.
    Useful for chaining with similarity_by_id(). The movie title must be exact.
    """
    points, _ = client.scroll(
        collection_name="top_movies",
        scroll_filter=Filter(
            must=[
                FieldCondition(
                    key="Series_Title",
                    match=MatchValue(value=title)
                )
            ]
        ),
        limit=5 # If movie has sequels the model can take that into account
    )

    if not points:
        return f"No movie found with title '{title}'"

    return json.dumps({"id": points[0].id, "payload": points[0].payload}, ensure_ascii=False)


# Tools for Qdrant connection
qdrant_tools = [qdrant_vector_search, qdrant_vector_search_with_filter, qdrant_similarity_by_id, qdrant_get_id_by_title, qdrant_get_poster]

# TESTING THE CONNECTION:
if __name__ == "__main__":
    print(client.get_collections())
    print(client.count("top_movies"))
    # print(client.retrieve("top_movies", ids=[0], with_payload=True, with_vectors=True))
    print(qdrant_similarity_by_id(40))
from qdrant_client import QdrantClient, models
from qdrant_client.models import PointStruct
from qdrant_client.http import models as qm
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
import os  
import csv 


CSV_FILE_PATH = r"D:\Github\Purwadhika-AI-Engineering-Bootcamp\Capstone Project\Module 3\CinephileGPT\data\imdb_top_1000.csv"


# Load environment variables from .env file
load_dotenv(dotenv_path=r'D:\Github\Purwadhika-AI-Engineering-Bootcamp\Capstone Project\Module 3\cinephile-gpt.venv\.env')
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")

# Initialize Qdrant client
client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
    timeout=30
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


    # Create OpenAI embeddings instance
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")


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
                "Series_Title": row[1],
                "Released_Year": row[2],
                "Certificate": row[3],
                "Genre": row[5],
                "Overview": row[7],
                "Director": row[9],
                "Star1": row[10],
                "Star2": row[11],
                "Star3": row[12],
                "Star4": row[13],
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
                collection_name="top_movies",
                points=points,
                batch_size=100,
                parallel=1
            )

        except Exception as e:
            print(f"Error during upsert: {e}")

    
# TESTING THE CONNECTION:
if __name__ == "__main__":
    print(client.get_collections())
    print(client.count("top_movies"))
    print(client.retrieve("top_movies", ids=[0], with_payload=True, with_vectors=True))
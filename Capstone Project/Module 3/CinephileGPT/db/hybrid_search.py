from langchain.tools import tool
import json


# ===================== TOOLS =====================

@tool
def hybrid_intersection_top_movies(sql_json: str, qdrant_json: str) -> str:
    """
    Hybrid tool to find movies that appear in BOTH the most recent SQL result
    and the most recent Qdrant semantic search result.

    - It reads from state["last_sql_result"] and state["last_qdrant_result"]
    - Both are expected to be JSON strings (lists of dicts)
    - Intersection is done by 'id' (Qdrant) vs 'movie_id' (SQL)
    - Returns a JSON string of intersecting SQL entries

    ONLY CALL THIS TOOL IF YOU'VE CALLED OTHER TOOLS.
    """

    try:
        sql_json = sql_json
        qdrant_json = qdrant_json

        # Load json strings as actual dictionaries
        sql_data = json.loads(sql_json)      # List of dicts
        qdrant_data = json.loads(qdrant_json)  # List of dicts

        # Extract IDs from Qdrant search results
        qdrant_ids = {item["id"] for item in qdrant_data}

        # Intersect with SQL (uses movie_id or id depending on your column)
        intersection = [
            row for row in sql_data
            if str(row.get("movie_id")) in qdrant_ids or str(row.get("id")) in qdrant_ids
        ]

        # Return JSON (empty [] if no overlap)
        return json.dumps(intersection, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"error": f"Hybrid tool failed: {str(e)}"}, ensure_ascii=False)


# Tools for hybrid search
hybrid_tools = [hybrid_intersection_top_movies]
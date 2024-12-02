import sys
import json
from utils import create_database, get_embedding


def search_database(query, limit, cursor):
    query_embedding = get_embedding(query)
    if not query_embedding:
        print("❌ Failed to get embedding for search query")
        return []

    cursor.execute('''
    SELECT 
        document,
        round(distance, 2) as similarity_score
    FROM embeddings 
    WHERE embedding MATCH ? 
    ORDER BY distance 
    LIMIT ?;
    ''', (json.dumps(query_embedding), limit))

    return cursor.fetchall()


def main():
    if len(sys.argv) < 2:
        print("Usage: {} 'your search query' [number_of_results]".format(
            sys.argv[0]))
        print("Example: {} 'a movie about time travel' 3".format(sys.argv[0]))
        exit(1)

    query = sys.argv[1]
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    print(f"🔍 Searching for: {query}")

    conn, cursor = create_database()
    results = search_database(query, limit, cursor)
    conn.close()

    if not results:
        print("❌ No results found")
        return

    print("🎬 Found matches:")
    for document, similarity_score in results:
        print(f"{document} (Similarity: {similarity_score})")


if __name__ == "__main__":
    main()

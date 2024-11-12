#!/bin/bash

# Check if required tools are installed
command -v sqlite3 >/dev/null 2>&1 || { echo "sqlite3 is required but not installed. Aborting." >&2; exit 1; }
command -v ollama >/dev/null 2>&1 || { echo "ollama is required but not installed. Aborting." >&2; exit 1; }

# Default number of results to show
LIMIT=${2:-5}

# Check if a search query was provided
if [ -z "$1" ]; then
    echo "Usage: $0 'your search query' [number_of_results]"
    echo "Example: $0 'a movie about time travel' 3"
    exit 1
fi

# The search query
QUERY="$1"

echo "🔍 Searching for: $QUERY"
echo "Getting embedding from Ollama..."

# Get embedding for the search query
QUERY_EMBEDDING=$(curl -s http://localhost:11434/api/embeddings -d "{
    \"model\": \"mxbai-embed-large\",
    \"prompt\": \"$QUERY\"
}" | jq -r '.embedding')

# Check if we got a valid embedding
if [ -z "$QUERY_EMBEDDING" ] || [ "$QUERY_EMBEDDING" = "null" ]; then
    echo "❌ Failed to get embedding for search query"
    exit 1
fi

echo "Finding closest matches..."

# Search the database
RESULTS=$(sqlite-utils "rag.db" "
    SELECT 
        document,
        round(distance, 2) as similarity_score
    FROM embeddings 
    WHERE embedding MATCH '$QUERY_EMBEDDING' 
    ORDER BY distance DESC 
    LIMIT $LIMIT;" --json)

# Check if we got any results
if [ -z "$RESULTS" ] || [ "$RESULTS" = "[]" ]; then
    echo "❌ No results found"
    exit 1
fi

# Format and display results
echo "🎬 Found matches:"
echo "$RESULTS" | jq -r '.[] | "\n📽️  Title: \(.document)\n   Similarity Score: \(.similarity_score)\n"'

# Optional: Save results to a file
if [ "$3" = "--save" ]; then
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    FILENAME="movie_search_${TIMESTAMP}.json"
    echo "$RESULTS" > "$FILENAME"
    echo "📄 Results saved to $FILENAME"
fi

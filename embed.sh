#!/bin/bash

# Check if sqlite and ollama are installed
command -v sqlite3 >/dev/null 2>&1 || { echo "sqlite3 is required but not installed. Aborting." >&2; exit 1; }
command -v ollama >/dev/null 2>&1 || { echo "ollama is required but not installed. Aborting." >&2; exit 1; }

# Create the database and table if they don't exist
sqlite-utils "rag.db" "CREATE VIRTUAL TABLE IF NOT EXISTS embeddings USING vec0(
    document TEXT PRIMARY KEY,
    embedding FLOAT[1024]
);"

# Function to safely escape single quotes in SQL
escape_sql() {
    echo "${1//\'/\'\'}"
}

# Process each movie from the JSON file
curl -s "https://raw.githubusercontent.com/inferablehq/sqlite-ollama-rag/refs/heads/main/data.json" | \
jq -c '.movies | .[]' | while read -r movie; do
    # Extract movie details
    TITLE=$(echo "$movie" | jq -r '.title')
    SYNOPSIS=$(echo "$movie" | jq -r '.synopsis')
    YEAR=$(echo "$movie" | jq -r '.year')
    
    # Combine into movie description
    MOVIE="$TITLE($YEAR): $SYNOPSIS"
    
    echo "Processing: $TITLE"
    
    # Get embedding from Ollama
    EMBEDDING=$(curl -s http://localhost:11434/api/embeddings -d "{
        \"model\": \"mxbai-embed-large\",
        \"prompt\": \"$MOVIE\"
    }" | jq -r '.embedding')
    
    # Skip if embedding failed
    if [ -z "$EMBEDDING" ] || [ "$EMBEDDING" = "null" ]; then
        echo "Failed to get embedding for: $TITLE"
        continue
    fi
    
    # Escape the movie description for SQL
    ESCAPED_MOVIE=$(escape_sql "$MOVIE")
    
    # Insert into database
    sqlite-utils "rag.db" "INSERT OR REPLACE INTO embeddings(document, embedding) 
        VALUES ('$ESCAPED_MOVIE', '$EMBEDDING');"
    
    echo "Successfully embedded: $TITLE"
    
    # Small delay to avoid overwhelming the API
    sleep 0.5
done

echo "Embedding process complete!"

# Print count of embedded documents
COUNT=$(sqlite-utils "rag.db" "SELECT COUNT(*) as count FROM embeddings;" | jq '.[0].count')
echo "Total documents embedded: $COUNT"

#!/bin/bash

command -v sqlite3 >/dev/null 2>&1 || { echo "sqlite3 is required but not installed. Aborting." >&2; exit 1; }
command -v ollama >/dev/null 2>&1 || { echo "ollama is required but not installed. Aborting." >&2; exit 1; }

sqlite-utils "rag.db" "CREATE VIRTUAL TABLE IF NOT EXISTS embeddings USING vec0(
    document TEXT PRIMARY KEY,
    embedding FLOAT[1024]
);"

escape_sql() {
    echo "${1//\'/\'\'}"
}

cat data.json | \
jq -c '.movies | .[]' | while read -r movie; do
    TITLE=$(echo "$movie" | jq -r '.title')
    SYNOPSIS=$(echo "$movie" | jq -r '.synopsis')
    YEAR=$(echo "$movie" | jq -r '.year')
    
    MOVIE="$TITLE($YEAR): $SYNOPSIS"
    
    echo "Processing: $TITLE"
    
    EMBEDDING=$(curl -s http://localhost:11434/api/embeddings -d "{
        \"model\": \"mxbai-embed-large\",
        \"prompt\": \"$MOVIE\"
    }" | jq -r '.embedding')
    
    if [ -z "$EMBEDDING" ] || [ "$EMBEDDING" = "null" ]; then
        echo "Failed to get embedding for: $TITLE"
        continue
    fi
    
    ESCAPED_MOVIE=$(escape_sql "$MOVIE")
    
    sqlite-utils "rag.db" "INSERT OR REPLACE INTO embeddings(document, embedding) 
        VALUES ('$ESCAPED_MOVIE', '$EMBEDDING');"
    
    echo "Successfully embedded: $TITLE"
done

echo "Embedding process complete!"

COUNT=$(sqlite-utils "rag.db" "SELECT COUNT(*) as count FROM embeddings;" | jq '.[0].count')
echo "Total documents embedded: $COUNT"

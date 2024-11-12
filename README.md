# SQLite RAG with Ollama

A simple demonstration of building a Retrieval Augmented Generation (RAG) system using SQLite and Ollama for local, on-device vector search. This project implements a movie recommendation system to showcase RAG capabilities without requiring complex infrastructure.

## Overview

This project demonstrates how to:

- Store and query vector embeddings in SQLite
- Generate embeddings using Ollama's local models
- Perform semantic similarity search for movie recommendations

For a detailed walkthrough of this project, check out the companion blog post: [Doing on-device retrieval augmented generation with Ollama and SQLite](https://www.inferable.ai/blog/posts/sqlite-rag)

## Prerequisites

- SQLite3
- sqlite-utils
- sqlite-vec extension
- Ollama
- curl
- jq

## Usage

To embed the data and build the database, run the `embed.sh` script.

```bash
sh embed.sh
```

To perform a search, run the `search.sh` script with a query.

```bash
sh search.sh "a movie about time travel"
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

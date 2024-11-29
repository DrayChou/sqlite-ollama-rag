import os
import sys
import json
import sqlite3
import requests

# 获取搜索查询和结果限制
if len(sys.argv) < 2:
    print("Usage: {} 'your search query' [number_of_results]".format(
        sys.argv[0]))
    print("Example: {} 'a movie about time travel' 3".format(sys.argv[0]))
    exit(1)

query = sys.argv[1]
limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5

print(f"🔍 Searching for: {query}")
print("Getting embedding from Ollama...")

# 获取查询的嵌入向量
response = requests.post('http://localhost:11434/api/embeddings', json={
    "model": "mxbai-embed-large",
    "prompt": query
})

query_embedding = response.json().get('embedding')

if not query_embedding:
    print("❌ Failed to get embedding for search query", query_embedding)
    exit(1)

print("Finding closest matches...")

# 搜索数据库
conn = sqlite3.connect('rag.db')
conn.enable_load_extension(True)

# 确保 vec0 模块已正确加载
# 请将 'path_to_vec0' 替换为 vec0 模块的实际路径
vec0_path = './vec0.dll'
conn.load_extension(vec0_path)

cursor = conn.cursor()

cursor.execute('''
SELECT 
    document,
    round(distance, 2) as similarity_score
FROM embeddings 
WHERE embedding MATCH ? 
ORDER BY distance 
LIMIT ?;
''', (json.dumps(query_embedding), limit))

results = cursor.fetchall()

if not results:
    print("❌ No results found")
    exit(1)

print("🎬 Found matches:")
for document, similarity_score in results:
    print(f"{document} (Similarity: {similarity_score})")

conn.close()

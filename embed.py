import os
import json
import sqlite3
import requests

# 创建数据库和表
conn = sqlite3.connect('rag.db')
conn.enable_load_extension(True)

# 确保 vec0 模块已正确加载
# 请将 'path_to_vec0' 替换为 vec0 模块的实际路径
vec0_path = './vec0.dll'
conn.load_extension(vec0_path)

cursor = conn.cursor()
cursor.execute('''
CREATE VIRTUAL TABLE IF NOT EXISTS embeddings USING vec0(
    document TEXT PRIMARY KEY,
    embedding FLOAT[1024]
);
''')
conn.commit()


def escape_sql(value):
    return value.replace("'", "''")


# 读取 JSON 数据
with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 处理每个电影条目
for movie in data['movies']:
    title = movie['title']
    synopsis = movie['synopsis']
    year = movie['year']

    movie_desc = f"{title}({year}): {synopsis}"

    print(f"Processing: {title}")

    response = requests.post('http://localhost:11434/api/embeddings', json={
        "model": "mxbai-embed-large",
        "prompt": movie_desc
    })

    embedding = response.json().get('embedding')

    if not embedding:
        print(f"Failed to get embedding for: {title}", embedding)
        continue

    escaped_movie = escape_sql(movie_desc)

    # 检查记录是否存在
    cursor.execute(
        'SELECT 1 FROM embeddings WHERE document = ?', (escaped_movie,))
    exists = cursor.fetchone()

    if exists:
        # 更新记录
        cursor.execute('''
        UPDATE embeddings SET embedding = ? WHERE document = ?;
        ''', (json.dumps(embedding), escaped_movie))
    else:
        # 插入新记录
        cursor.execute('''
        INSERT INTO embeddings(document, embedding) 
        VALUES (?, ?);
        ''', (escaped_movie, json.dumps(embedding)))

    conn.commit()

    print(f"Successfully embedded: {title}")

print("Embedding process complete!")

cursor.execute('SELECT COUNT(*) as count FROM embeddings;')
count = cursor.fetchone()[0]
print(f"Total documents embedded: {count}")

conn.close()

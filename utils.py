import sqlite3
import requests


EMBEDDING_API_URL = 'http://localhost:11434/api/embeddings'
# EMBEDDING_MODEL = 'mxbai-embed-large'
# EMBEDDING_LENGTH = 1024
EMBEDDING_MODEL = 'nomic-embed-text'
EMBEDDING_LENGTH = 768

DB_PATH = EMBEDDING_MODEL + '_rag.db'
VEC0_PATH = './vec0.dll'


def create_database():
    conn = sqlite3.connect(DB_PATH)
    conn.enable_load_extension(True)
    conn.load_extension(VEC0_PATH)
    cursor = conn.cursor()
    cursor.execute(f'''
    CREATE VIRTUAL TABLE IF NOT EXISTS embeddings USING vec0(
        document TEXT PRIMARY KEY,
        embedding FLOAT[{EMBEDDING_LENGTH}]
    );
    ''')
    conn.commit()
    return conn, cursor


def escape_sql(value):
    return value.replace("'", "''")


def get_embedding(text):
    response = requests.post(EMBEDDING_API_URL, json={
        "model": EMBEDDING_MODEL,
        "prompt": text
    })
    return response.json().get('embedding')

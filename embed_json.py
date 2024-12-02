import json
from utils import create_database, escape_sql, get_embedding

DATA_PATH = 'data.json'


def process_movie(movie, cursor):
    title = movie['title']
    synopsis = movie['synopsis']
    year = movie['year']

    movie_desc = f"{title}({year}): {synopsis}"
    print(f"Processing: {title}")

    embedding = get_embedding(movie_desc)
    if not embedding:
        print(f"Failed to get embedding for: {title}")
        return

    escaped_movie = escape_sql(movie_desc)

    cursor.execute(
        'SELECT 1 FROM embeddings WHERE document = ?', (escaped_movie,))
    exists = cursor.fetchone()

    if exists:
        cursor.execute('''
        UPDATE embeddings SET embedding = ? WHERE document = ?;
        ''', (json.dumps(embedding), escaped_movie))
    else:
        cursor.execute('''
        INSERT INTO embeddings(document, embedding) 
        VALUES (?, ?);
        ''', (escaped_movie, json.dumps(embedding)))

    print(f"Successfully embedded: {title}")


def process_movies(data, cursor):
    for movie in data['movies']:
        process_movie(movie, cursor)


def main():
    conn, cursor = create_database()

    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    process_movies(data, cursor)
    conn.commit()

    cursor.execute('SELECT COUNT(*) as count FROM embeddings;')
    count = cursor.fetchone()[0]
    print(f"Total documents embedded: {count}")

    conn.close()


if __name__ == "__main__":
    main()

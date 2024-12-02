import pandas as pd
import json
from utils import create_database, escape_sql, get_embedding

CSV_PATH = '【攻略】集百家大全怪物卡片经验数据表 - Sheet1.csv'


def process_csv(file_path, cursor):
    df = pd.read_csv(file_path)
    for index, row in df.iterrows():
        # 将每一行的数据拼接成一个字符串
        document = ', '.join([f"{col}: {row[col]}" for col in df.columns])
        print(f"Processing: {row[df.columns[0]]}")  # 打印第一列的值作为标识

        embedding = get_embedding(document)
        if not embedding:
            print(f"Failed to get embedding for: {row[df.columns[0]]}")
            continue

        escaped_document = escape_sql(document)

        cursor.execute(
            'SELECT 1 FROM embeddings WHERE document = ?', (escaped_document,))
        exists = cursor.fetchone()

        if exists:
            cursor.execute('''
            UPDATE embeddings SET embedding = ? WHERE document = ?;
            ''', (json.dumps(embedding), escaped_document))
        else:
            cursor.execute('''
            INSERT INTO embeddings(document, embedding) 
            VALUES (?, ?);
            ''', (escaped_document, json.dumps(embedding)))

        print(f"Successfully embedded: {row[df.columns[0]]}")


def main():
    conn, cursor = create_database()
    process_csv(CSV_PATH, cursor)
    conn.commit()

    cursor.execute('SELECT COUNT(*) as count FROM embeddings;')
    count = cursor.fetchone()[0]
    print(f"Total documents embedded: {count}")

    conn.close()


if __name__ == "__main__":
    main()

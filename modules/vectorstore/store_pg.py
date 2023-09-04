import os

import psycopg2
from langchain.vectorstores.pgvector import DistanceStrategy
# PG Vector 向量存储库
from langchain.vectorstores.pgvector import PGVector

from modules.config import bot_config

EXIST_COLLECTIONS = []


# 从环境变量获取连接信息
def __get_pg_connection_string_from_env():
    connection_string = PGVector.connection_string_from_db_params(
        driver=os.environ.get("PGVECTOR_DRIVER", "psycopg2"),
        host=os.environ.get("PGVECTOR_HOST", "localhost"),
        port=int(os.environ.get("PGVECTOR_PORT", "5432")),
        database=os.environ.get("PGVECTOR_DATABASE", "postgres"),
        user=os.environ.get("PGVECTOR_USER", "postgres"),
        password=os.environ.get("PGVECTOR_PASSWORD", "mysecretpassword"),
    )
    return connection_string;


def __get_pg_connection_string(host, port, database, username, password):
    connection_string = PGVector.connection_string_from_db_params(
        driver=os.environ.get("PGVECTOR_DRIVER", "psycopg2"),
        host=host,
        port=port,
        database=database,
        user=username,
        password=password,
    )
    return connection_string;


# 根据参数组装连接字符串
def compose_pg_connection_string(host, port, database, username, password):
    connection_string = PGVector.connection_string_from_db_params(
        driver=os.environ.get("PGVECTOR_DRIVER", "psycopg2"),
        host=host,
        port=port,
        database=database,
        user=username,
        password=password,
    )
    return connection_string;


# 使用指定的embeddings 将文本放入指定collection_name
def put_documents(embeddings, collection_name, texts, connection_string):
    # conn_string = connection_string or __get_pg_connection_string_from_env();
    # print(conn_string)
    # 将文档存入向量
    db = PGVector.from_documents(
        embedding=embeddings,
        documents=texts,
        collection_name=collection_name,
        connection_string=connection_string,
    )
    print(f"Success handle documents with: {collection_name}, to : {connection_string}")


def refresh_collections():
    # con_str = connection_string or compose_pg_connection_string(*bot_config.get_pg_config())
    config = bot_config.get_pg_config();
    conn = psycopg2.connect(database=config[2], user=config[3], password=config[4], host=config[0], port=config[1])
    EXIST_COLLECTIONS.clear()
    with conn:
        print(f"conn {conn}")
        cur = conn.cursor()
        cur.execute("select distinct name from public.langchain_pg_collection")
        rows = cur.fetchall()
        # collections = []
        for row in rows:
            EXIST_COLLECTIONS.append(row[0])
        # conn.close()
    # return collections;
    return EXIST_COLLECTIONS;


# 提取出来做retr
def as_retriever(embeddings, collection_name, connection_string, retrieve_size=2):
    # print(f"fxxx {connection_string}")
    store = PGVector(
        connection_string=connection_string,
        embedding_function=embeddings,
        collection_name=collection_name,
        distance_strategy=DistanceStrategy.COSINE
    )
    retriever = store.as_retriever()
    retriever.search_kwargs = {'k': retrieve_size}  # dict 省钱的秘诀
    return retriever;
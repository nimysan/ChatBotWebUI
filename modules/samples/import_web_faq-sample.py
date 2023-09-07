#MD目录导入

import os
from typing import List, Tuple

from langchain.docstore.document import Document
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

faq_dir=os.environ.get("FAQ_PATH")
collection_name=os.environ.get("COLLECTION_NAME")


from langchain.document_loaders import SeleniumURLLoader

urls = [
    "http://jfwiki.streamax.com:7503/web/#/172/1275",
]
loader = SeleniumURLLoader(urls)
data = loader.load()

embeddings = OpenAIEmbeddings()

text_splitter = RecursiveCharacterTextSplitter(
  chunk_size=20,
  chunk_overlap=0
)
texts = text_splitter.split_documents(data)
# PG Vector 向量存储库
from langchain.vectorstores.pgvector import PGVector
CONNECTION_STRING = PGVector.connection_string_from_db_params(
    driver=os.environ.get("PGVECTOR_DRIVER", "psycopg2"),
    host=os.environ.get("PGVECTOR_HOST", "localhost"),
    port=int(os.environ.get("PGVECTOR_PORT", "5433")),
    database=os.environ.get("PGVECTOR_DATABASE", "postgres"),
    user=os.environ.get("PGVECTOR_USER", "postgres"),
    password=os.environ.get("PGVECTOR_PASSWORD", "mysecretpassword"),
)

#将文档存入向量
db = PGVector.from_documents(
    embedding=embeddings,
    documents=texts,
    collection_name=collection_name,
    connection_string=CONNECTION_STRING,
)

print("导入成功")

query = "车辆信息"
docs_with_score: List[Tuple[Document, float]] = db.similarity_search_with_score(query)
for doc, score in docs_with_score:
    print("-" * 80)
    print("Score: ", score)
    print(doc.page_content)
    print("-" * 80)
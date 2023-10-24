import os
import shutil
from typing import List, Tuple

import gradio as gr
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.pgvector import PGVector
from langchain.document_loaders.web_base import WebBaseLoader

from modules.bot.embeddings_provider import EmbeddingsProvider
from modules.config import bot_config
from modules.vectorstore.store_pg import compose_pg_connection_string
from langchain.document_loaders import Docx2txtLoader


def sample_function(*args):
    print(f"args is {args}")


def load_data_into_pg(data, collection_name, t_clean_before_import, sample_keywords, chunk_size, chunk_overlap):
    try:
        bot_config_value = bot_config.get_config("bot")
        embeddings = EmbeddingsProvider().get_embeddings(bot_config_value["embeddings"])
        # print(f"The embeddings is {embeddings}")
        connection_string = compose_pg_connection_string(*bot_config.get_config("pg_config"))
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

        texts = text_splitter.split_documents(data)
        # print("===============sample text fragment ===============\n")
        # if texts and len(texts) > 0:
        #     print(texts[1])
        # print("===============sample text fragment ===============\n")
        #
        print(f"#########connection_string data to {connection_string}")
        db = PGVector.from_documents(
            embedding=embeddings,
            documents=texts,
            collection_name=collection_name,
            connection_string=connection_string,
            pre_delete_collection=t_clean_before_import
        )
        print("done")

        if len(sample_keywords) > 0:
            docs_with_score: List[Tuple[Document, float]] = db.similarity_search_with_score(sample_keywords)
            if len(docs_with_score) > 0:
                return f"Done. Sample datas:\n {docs_with_score[0]}"
            else:
                return f"Done. But no match with sample keyword"
        print(f"######### done #############")
    except Exception as e:
        raise gr.Error(f"Failed to import, the error detail is {e}")


def load_from_word(file_paths, collection_name, clean_collection, sample_keywords, chunk_size, chunk_overlap):
    documents = []
    for file_path in file_paths:
        loader = Docx2txtLoader(str(file_path.name))
        loaded_documents = loader.load()
        documents.extend(loaded_documents)

    load_data_into_pg(documents, collection_name, clean_collection, sample_keywords,
                      chunk_size,
                      chunk_overlap)


# 这里是真实的导入知识库
def import_knowledge_function(urls, file_outputs, collection_name, t_clean_before_import, sample_keywords, chunk_size,
                              chunk_overlap):
    if collection_name == "":
        raise gr.Error("Collection name can not be empty")

    print(f"urls is {urls}")
    if len(urls) > 0:
        # url = "https://docs.python.org/3.9/" sample url
        print(f"clean is {t_clean_before_import}")
        urls_array = urls.split(",")
        print(f"----size {len(urls_array)}")
        loader = WebBaseLoader(urls_array)
        data = loader.load()
        load_data_into_pg(data, collection_name, t_clean_before_import, sample_keywords, chunk_size, chunk_overlap)

    if file_outputs is not None:
        load_from_word(file_outputs, collection_name, t_clean_before_import, sample_keywords, chunk_size,
                       chunk_overlap)


def upload_file(files):
    file_paths = [file.name for file in files]
    # print(file_paths)
    return file_paths


with gr.Blocks() as component_import_data:
    # gr.Markdown("根据现有的web导入您的知识库")
    with gr.Column():
        file_outputs = gr.Files()
        upload_button = gr.UploadButton("Click to Upload a File", file_types=["doc", "docx", "pdf"],
                                        file_count="multiple")
        upload_button.upload(upload_file, upload_button, file_outputs)

        t_web_urls = gr.TextArea(placeholder="Please enter a comma (English) separated list of URLs",
                                 label="web link list",
                                 type="text", lines=2,
                                 value="https://aws.amazon.com/cn/s3/faqs/")  # ,这后面千万不要有逗号 一个逗号的悲剧
        print(f"inside children ######## ---- {t_web_urls}")
        t_doc_collection = gr.Text(placeholder="Collection", label="Collection")
        t_clean_before_import = gr.Checkbox(label="clean exists data before import")
        t_sample_keyword = gr.Text(placeholder="Test keyword", label="Test keyword")
        t_chunk_size = gr.Number(label="Chunk Size", value=1000)
        t_chunk_overlap = gr.Number(label="Overlap", value=20)

        # with gr.Column() as knowledge_collection_import:
        import_btn = gr.Button("Import now")
        import_out = gr.Textbox(label="Result")

        import_btn.click(fn=import_knowledge_function,
                         inputs=[t_web_urls, file_outputs, t_doc_collection, t_clean_before_import, t_sample_keyword,
                                 t_chunk_size,
                                 t_chunk_overlap],
                         outputs=import_out)

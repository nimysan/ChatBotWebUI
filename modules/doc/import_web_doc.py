from typing import List, Tuple

import gradio as gr
# from langchain.document_loaders import SeleniumURLLoader
from langchain.docstore.document import Document
from langchain.embeddings import BedrockEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.pgvector import PGVector
from langchain.document_loaders.web_base import WebBaseLoader

from modules.config import bot_config
from modules.vectorstore.store_pg import compose_pg_connection_string


def sample_function(*args):
    print(f"args is {args}")


# 这里是真实的导入知识库
def import_knowledge_function(urls, collection_name, t_clean_before_import, sample_keywords, chunk_size, chunk_overlap):
    # url = "https://docs.python.org/3.9/" sample url
    print(f"clean is {t_clean_before_import}")
    try:
        embeddings = BedrockEmbeddings(
            region_name="us-west-2",
            model_id="amazon.titan-embed-text-v1",
            credentials_profile_name="gws"
        )
        connection_string = compose_pg_connection_string(*bot_config.get_config("pg_config"))
        # connection_string = compose_pg_connection_string(bot_config.get_config(""))

        print(
            f"#########generate data to {collection_name} from {urls} with keywords: {sample_keywords} pg host {connection_string} ")
        loader = WebBaseLoader([urls])
        data = loader.load()
        # loader = SeleniumURLLoader(urls)
        # data = loader.load()
        # print(data)
        # 初始化文本分割器
        # 英语多，中文少
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

        texts = text_splitter.split_documents(data)
        print("===============sample text fragment ===============\n")
        if texts and len(texts) > 0:
            print(texts[1])
        print("===============sample text fragment ===============\n")

        print(f"#########connection_string data to {connection_string}")
        db = PGVector.from_documents(
            embedding=embeddings,
            documents=texts,
            collection_name=collection_name,
            connection_string=connection_string,
            pre_delete_collection=t_clean_before_import
        )

        # query = "车辆信息"
        docs_with_score: List[Tuple[Document, float]] = db.similarity_search_with_score(sample_keywords)
        if len(docs_with_score) > 0:
            return f"导入完成 例子数据:\n {docs_with_score[0]}"
        else:
            return f"导入完成 但是没有找到匹配关键字的数据"
    except Exception as e:
        raise gr.Error(f"Failed to import, the error detail is {e}")


with gr.Blocks() as component_import_data:
    # gr.Markdown("根据现有的web导入您的知识库")
    with gr.Column():
        t_web_urls = gr.TextArea(placeholder="请输入逗号（英文）分割的url列表", label="在线知识库列表",
                                 type="text", lines=2,
                                 value="https://aws.amazon.com/cn/s3/faqs/")  # ,这后面千万不要有逗号 一个逗号的悲剧
        print(f"inside children ######## ---- {t_web_urls}")
        t_doc_collection = gr.Text(placeholder="知识库集合名称", label="请输入知识库集合名称")
        t_clean_before_import = gr.Checkbox(label="clean exists data before import")
        t_sample_keyword = gr.Text(placeholder="输入一个关键字, 知识入库后测试搜索效果", label="导入测试关键词")
        t_chunk_size = gr.Number(label="Chunk Size", value=1000)
        t_chunk_overlap = gr.Number(label="Overlap", value=20)

        # with gr.Column() as knowledge_collection_import:
        import_btn = gr.Button("现在开始导入知识")
        import_out = gr.Textbox(label="导入结果")

        import_btn.click(fn=import_knowledge_function,
                         inputs=[t_web_urls, t_doc_collection, t_clean_before_import, t_sample_keyword, t_chunk_size,
                                 t_chunk_overlap],
                         outputs=import_out)

"""
基于SageMaker Endpoint的机器人组装程序 （每个模型根据自己的特性来定制prompt)
"""

import json
import os

from langchain import SagemakerEndpoint, LLMChain
from langchain.chains import RetrievalQAWithSourcesChain, StuffDocumentsChain, ConversationalRetrievalChain
from langchain.llms.sagemaker_endpoint import LLMContentHandler
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

from modules.bot.bot_pg_chatgpt import build_embeddings
from modules.config import bot_config
from modules.vectorstore import store_pg
from modules.vectorstore.store_pg import compose_pg_connection_string

MAX_HISTORY_LENGTH = 5


def build_retriever(embeddings, collection_name, retrieve_size=2):
    connection_string = compose_pg_connection_string(*bot_config.get_config("pg_config"))
    print(f"build_retriever store for {connection_string} with collection name {collection_name}")
    return store_pg.as_retriever(embeddings, collection_name, connection_string, retrieve_size)


class ContentHandler(LLMContentHandler):
    content_type = "application/json"
    accepts = "application/json"

    def transform_input(self, prompt: str, model_kwargs: dict) -> bytes:
        input_str = json.dumps({"ask": prompt})
        # print(f"input_str {input_str}")
        return input_str.encode('utf-8')

    def transform_output(self, output: bytes) -> str:
        response_json = json.loads(output.read())
        # print(f"xx {response_json} ")
        # # return response_json["answer"]
        return response_json['answer']


# 构造大语言模型
def build_llm():
    content_handler = ContentHandler()
    endpoint_name = "pytorch-inference-2023-09-14-03-28-18-787"
    endpoint_region = os.environ.get("ENDPOINT_REGION", "us-east-1")
    # 需要做参数化

    print("endpoint_name " + endpoint_name)
    llm = SagemakerEndpoint(
        endpoint_name=endpoint_name,
        region_name=endpoint_region,
        model_kwargs={"temperature": 1e-10, "max_length": 500},
        content_handler=content_handler
    )
    return llm;


openai_embeddings = build_embeddings()
CHAT_MEMORY = ConversationBufferMemory(memory_key="chat_history", return_messages=True)


def build_chain(collection_name="s3faq", conversational=True):
    # 大语言模型
    llm = build_llm();

    print(f"knowledge bases on collection {collection_name} ")

    openai_embeddings = build_embeddings()

    if conversational is True:
        # memory

        # 问题生成器类型
        _template = """鉴于以下对话和后续问题，将后续问题改写为
            是一个独立的问题，用其原始语言。确保避免使用任何不清楚的代词。
            Chat History:
            {chat_history}
            接下来的提问: {question}
            转化后的问题:"""
        CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(_template)
        condense_question_chain = LLMChain(
            llm=llm,
            prompt=CONDENSE_QUESTION_PROMPT,
            verbose=True
        )

        # 常规的QA_Chain
        template = """使用以下上下文来回答最后的问题。
            如果你不知道答案，就说你不知道，不要试图编造答案。
            最多使用三个句子，并尽可能保持答案简洁。
            总是说“谢谢您的提问！”在答案的开头。始终在答案中返回“来源”部分。 
            {context}
            问题: {question}
            我的答案是:"""
        QA_CHAIN_PROMPT = PromptTemplate.from_template(template)
        qa_chain = LLMChain(llm=llm, prompt=QA_CHAIN_PROMPT, verbose=True)

        doc_prompt = PromptTemplate(
            template="Content: {page_content}\nSource: {source}",
            input_variables=["page_content", "source"],
        )
        #
        final_qa_chain = StuffDocumentsChain(
            llm_chain=qa_chain,
            document_variable_name="context",
            document_prompt=doc_prompt,
            verbose=True
        )

        qa = ConversationalRetrievalChain(
            question_generator=condense_question_chain,
            retriever=build_retriever(openai_embeddings, collection_name),
            memory=CHAT_MEMORY,
            verbose=True,
            combine_docs_chain=final_qa_chain,
        )
        # qa.__init__()
        return qa
    else:
        staff_question_prompt_template = """
            给定长文档和问题的以下提取部分，使用参考文献（“Source”）创建最终答案。
            如果你不知道答案，就说你不知道。不要试图编造答案。
            始终在答案中返回“Source”部分。不回答超过100个字符。

            问题: {question}
            =========
            {summaries}
            =========
            请最终以中文回答问题。"""
        STAFF_QUESTION_PROMPT: PromptTemplate = PromptTemplate(template=staff_question_prompt_template,
                                                               input_variables=["summaries", "question"])
        chain_type_kwargs = {
            "prompt": STAFF_QUESTION_PROMPT,  # Prompts
            "verbose": True
        }
        qa = RetrievalQAWithSourcesChain.from_chain_type(
            retriever=build_retriever(openai_embeddings, collection_name),
            llm=llm,
            verbose=True,
            chain_type_kwargs=chain_type_kwargs
        )

        return qa


def run_chain(chain, prompt: str, history=[]):
    return chain({"question": prompt, "chat_history": history})


if __name__ == "__main__":
    qa = build_chain("chatgpt")
    resp = run_chain(qa, "车辆上下线", history=[])
    print(resp['answer'])

"""
基于SageMaker Endpoint的机器人组装程序 （每个模型根据自己的特性来定制prompt)
"""

import json
import os

from langchain import SagemakerEndpoint
from langchain.chains import RetrievalQAWithSourcesChain
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


def build_chain(collection_name="s3faq"):
    print("Database collection name ---> " + collection_name)

    # 历史存储器
    memory = ConversationBufferMemory(memory_key="chat_histo:qry", return_messages=True)

    # 大语言模型
    llm = build_llm();

    staff_question_prompt_template = """Given the following extracted parts of a long document and a question, create a final answer with references ("SOURCES"). 
            If you don't know the answer, just say that you don't know. Don't try to make up an answer.
            ALWAYS return a "Source" part in your answer. Not answer more than 100 tokens.
            Respond in Chinese.

            QUESTION: {question}
            =========
            {summaries}
            =========
            FINAL ANSWER IN Chinese:"""
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

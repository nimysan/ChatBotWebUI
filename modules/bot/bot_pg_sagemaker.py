"""
基于SageMaker Endpoint的机器人组装程序 （每个模型根据自己的特性来定制prompt)
"""

import json
import os

from langchain import PromptTemplate
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.chains.router import MultiRetrievalQAChain
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.llms.sagemaker_endpoint import SagemakerEndpoint, LLMContentHandler
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.vectorstores.pgvector import PGVector

from modules.vectorstore import store_pg


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


MAX_HISTORY_LENGTH = 5
OPENAI_KEY = os.environ["OPENAI_API_KEY"]


def build_retriever(embeddings, connection_string, collection_name, retrieve_size=2):
    return store_pg.as_retriever(embeddings, collection_name, connection_string, retrieve_size)


# 构造大语言模型
def build_llm(llm):
    if llm == "chatgpt":
        return OpenAI(batch_size=5);  # 大语言模型 map-reduce
    elif llm == 'chatglm':
        class ContentHandler(LLMContentHandler):
            content_type = "application/json"
            accepts = "application/json"

            def transform_input(self, prompt: str, model_kwargs: dict) -> bytes:
                input_str = json.dumps({"ask": prompt})
                return input_str.encode('utf-8')

            def transform_output(self, output: bytes) -> str:
                response_json = json.loads(output.read())
                return response_json["answer"]

        content_handler = ContentHandler()
        endpoint_name = os.environ.get("ENDPOINT_NAME")
        endpoint_region = os.environ.get("ENDPOINT_REGION", "us-east-1")

        print("endpoint_name " + endpoint_name)
        llm = SagemakerEndpoint(
            endpoint_name=endpoint_name,
            region_name=endpoint_region,
            model_kwargs={"temperature": 1e-10, "max_length": 500},
            content_handler=content_handler
        )
        return llm;
    else:
        raise ImportError(
            "please give correct llm type"
        )


def build_chain(llm="chatgpt"):
    # print("database collection name ---> " + collection_name)

    # 历史存储器
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    # 大语言模型
    llm = build_llm(llm);

    # 问题产生器 - 这个是产生多次问题的的时候的Prompt, 根据History来产生问题
    # condense_template = """
    #   给定以下对话和一个后续问题，将后续问题重述为一个独立的问题。
    #
    #   对话:
    #   {chat_history}
    #   接下来的问题: {question}
    #   标准问题:
    #   """
    # CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(condense_template)
    # question_generator = LLMChain(llm=llm, prompt=CONDENSE_QUESTION_PROMPT, verbose=True)

    # 供参考用， langchain内置的prompt模版
    sample_template = """Given the following extracted parts of a long document and a question, create a final answer with references ("SOURCES"). 
    If you don't know the answer, just say that you don't know. Don't try to make up an answer.
    ALWAYS return a "SOURCES" part in your answer.
    Respond in Italian.

    QUESTION: {question}
    =========
    {summaries}
    =========
    FINAL ANSWER IN ITALIAN:"""

    collection_name = os.environ.get("COLLECTION_NAME")
    if collection_name == '':
        raise "please give collection name in ENV with variable name: COLLECTION_NAME"

    print("knowledge bases on collection " + collection_name)

    staff_question_prompt_template = """
     从给定的长文档中提取指定问题的答案，创建带有参考文献（“SOURCES”）的最终答案。
     如果你不知道答案，就说你不知道。不要试图编造答案。
     始终在您的答案中返回给定内容中 “Source” 部分。
     问题: {question}
     =========
     {summaries}
     =========
     最终中文答案: """
    STAFF_QUESTION_PROMPT: PromptTemplate = PromptTemplate(template=staff_question_prompt_template,
                                                           input_variables=["summaries", "question"])
    chain_type_kwargs = {
        "prompt": STAFF_QUESTION_PROMPT,  # Prompts
        "verbose": True
    }
    qa = RetrievalQAWithSourcesChain.from_chain_type(
        retriever=build_retriever(collection_name),  # VectorStore
        llm=llm,  # LLM
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

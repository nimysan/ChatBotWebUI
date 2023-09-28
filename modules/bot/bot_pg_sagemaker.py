"""
基于SageMaker Endpoint的机器人组装程序 （每个模型根据自己的特性来定制prompt)
"""

import json
import os
from abc import ABC
from typing import List

from langchain import SagemakerEndpoint, LLMChain
from langchain.chains import RetrievalQAWithSourcesChain, StuffDocumentsChain, ConversationalRetrievalChain
from langchain.embeddings import OpenAIEmbeddings
from langchain.embeddings.base import Embeddings
from langchain.llms.sagemaker_endpoint import LLMContentHandler
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

from modules.bot.bot import KnowledgeBot
from modules.bot.bot_pg_chatgpt import build_embeddings
from modules.config import bot_config
from modules.config.bot_config import get_config
from modules.vectorstore import store_pg
from modules.vectorstore.store_pg import compose_pg_connection_string

from typing import Dict, List
from langchain.embeddings import SagemakerEndpointEmbeddings
from langchain.embeddings.sagemaker_endpoint import EmbeddingsContentHandler
import json

MAX_HISTORY_LENGTH = 5


class SMContentHandler(LLMContentHandler):
    content_type = "application/json"
    accepts = "application/json"

    def transform_input(self, prompt: str, model_kwargs: dict) -> bytes:
        input_str = json.dumps({"ask": prompt})
        return input_str.encode('utf-8')

    def transform_output(self, output: bytes) -> str:
        response_json = json.loads(output.read())
        return response_json['answer']


class EmbeddingContentHandler(EmbeddingsContentHandler):
    content_type = "application/json"
    accepts = "application/json"

    def transform_input(self, inputs: list[str], model_kwargs: Dict) -> bytes:
        """
        Transforms the input into bytes that can be consumed by SageMaker endpoint.
        Args:
            inputs: List of input strings.
            model_kwargs: Additional keyword arguments to be passed to the endpoint.
        Returns:
            The transformed bytes input.
        """
        # Example: inference.py expects a JSON string with a "inputs" key:
        print(f"input is {inputs}")
        input_str = json.dumps({"inputs": inputs, **model_kwargs})
        return input_str.encode("utf-8")

    def transform_output(self, output: bytes) -> List[List[float]]:
        """
        Transforms the bytes output from the endpoint into a list of embeddings.
        Args:
            output: The bytes output from SageMaker endpoint.
        Returns:
            The transformed output - list of embeddings
        Note:
            The length of the outer list is the number of input strings.
            The length of the inner lists is the embedding dimension.
        """
        # Example: inference.py returns a JSON string with the list of
        # embeddings in a "vectors" key:
        response_json = json.loads(output.read().decode("utf-8"))
        print(f"embeddings response is: {response_json}")
        return response_json[0][0]


embedding_content_handler = EmbeddingContentHandler()

embeddings = SagemakerEndpointEmbeddings(
    # credentials_profile_name="credentials-profile-name",
    endpoint_name="huggingface-pytorch-inference-2023-09-28-05-38-44-863",
    region_name="us-east-1",
    content_handler=embedding_content_handler,
)


class SagemakerKnowledgeBot:
    """
        a knowledge bot with SageMaker
    """

    def __init__(self, collection_name, conversational_mode):
        print("SagemakerKnowledgeBot construct method")
        self.region = "us-east-1"
        self.embeddings = embeddings
        self.retriever = self.build_retriever(self.embeddings, collection_name)
        self.chat_history = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.llm = self.build_llm(get_config("sm_endpoint"))
        self.conversational_mode = conversational_mode
        self.chain = None

    def build_retriever(self, embeddings, collection_name, retrieve_size=2):
        connection_string = compose_pg_connection_string(*bot_config.get_config("pg_config"))
        print(f"build_retriever store for {connection_string} with collection name {collection_name}")
        return store_pg.as_retriever(embeddings, collection_name, connection_string, retrieve_size)

    # 构造大语言模型
    def build_llm(self, endpoint_name):
        content_handler = SMContentHandler()
        print(f"endpoint name is {endpoint_name} in region {self.region} ")
        llm = SagemakerEndpoint(
            endpoint_name=endpoint_name,
            region_name=self.region,
            model_kwargs={"temperature": 1e-10, "max_length": 500},
            content_handler=content_handler
        )
        return llm;

    def build_chain(self):
        # 大语言模型
        llm = self.llm;
        embeddings = build_embeddings()

        if self.conversational_mode is True:
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
                retriever=self.retriever,
                memory=self.chat_history,
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
                retriever=self.retriever,
                llm=llm,
                verbose=True,
                chain_type_kwargs=chain_type_kwargs
            )

            return qa

    def talk(self, prompt, history=[]):
        """
        对话
        :param prompt:
        :param history:
        :return:
        """
        if self.chain is None:
            self.chain = self.build_chain()

        return self.chain({"question": prompt, "chat_history": history})

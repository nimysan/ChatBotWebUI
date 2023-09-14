"""
基于SageMaker Endpoint的机器人组装程序 （每个模型根据自己的特性来定制prompt)
"""

import json
import os
from typing import Dict

from langchain import LLMChain
from langchain.chains import RetrievalQAWithSourcesChain, StuffDocumentsChain, ConversationalRetrievalChain
from langchain.embeddings import BedrockEmbeddings
from langchain.llms.bedrock import Bedrock
from langchain.llms.sagemaker_endpoint import LLMContentHandler
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

from modules.config import bot_config
from modules.config.embedding_config import get_embeddings_by_name, EMBEDDINGS_BEDROCK
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
        input_str = json.dumps({"inputs": prompt})
        return input_str.encode('utf-8')

    def transform_output(self, output: bytes) -> str:
        response_json = json.loads(output.read())
        print(f"xx {response_json} ")
        # return response_json["answer"]
        return response_json[0]['generated_text']


# 构造大语言模型
def build_llm():
    return Bedrock(
        credentials_profile_name="bedrock-admin",
        model_id="amazon.titan-tg1-large"
    )


embeddings = get_embeddings_by_name(EMBEDDINGS_BEDROCK);

CHAT_MEMORY = ConversationBufferMemory(memory_key="chat_history", return_messages=True)


def build_chain(collection_name, conversational=True):
    # 大语言模型
    llm = build_llm();

    print(f"knowledge bases on collection {collection_name} ")

    if conversational is True:
        # memory

        # 问题生成器类型
        _template = """Given the following conversation and a follow up question, rephrase the follow up question to 
        be a standalone question, in its original language.\ Make sure to avoid using any unclear pronouns. 

        Chat History:
        {chat_history}
        Follow Up Input: {question}
        Standalone question:"""
        CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(_template)
        condense_question_chain = LLMChain(
            llm=llm,
            prompt=CONDENSE_QUESTION_PROMPT,
            verbose=True
        )

        # 常规的QA_Chain
        template = """Use the following pieces of context to answer the question at the end. 
        If you don't know the answer, just say that you don't know, don't try to make up an answer. 
        Use three sentences maximum and keep the answer as concise as possible. 
        Always say "感谢您的提问!" at the beginning of the answer.  ALWAYS return a "Source" part in your answer. 
        {context}
        Question: {question}
        Helpful Answer:"""
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
            retriever=build_retriever(embeddings, collection_name),
            memory=CHAT_MEMORY,
            verbose=True,
            combine_docs_chain=final_qa_chain,
        )
        # qa.__init__()
        return qa
    else:
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
            retriever=build_retriever(embeddings, collection_name),
            llm=llm,
            verbose=True,
            chain_type_kwargs=chain_type_kwargs
        )

        return qa

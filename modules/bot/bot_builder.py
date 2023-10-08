from langchain import PromptTemplate, LLMChain
from langchain.chains import StuffDocumentsChain, ConversationalRetrievalChain, RetrievalQAWithSourcesChain
from langchain.memory import ConversationBufferMemory

from modules.bot.embeddings_provider import EmbeddingsProvider
from modules.bot.llm_provider import LLMProvider
from modules.config import bot_config
from modules.vectorstore import store_pg
from modules.vectorstore.store_pg import compose_pg_connection_string


class BotBuilder:
    def __init__(self):
        self.embedding_provider = EmbeddingsProvider()
        self.llm_provider = LLMProvider()

    def __build_retriever(self, embeddings, collection_name, retrieve_size=2):
        connection_string = compose_pg_connection_string(*bot_config.get_config("pg_config"))
        print(f"build_retriever store for {connection_string} with collection name {collection_name}")
        return store_pg.as_retriever(embeddings, collection_name, connection_string, retrieve_size)

    def build_chain(self, collection_name, conversational_mode, llm_type, embedding_type):
        # 大语言模型
        llm = self.llm_provider.get_llm(llm_type)
        embeddings = self.embedding_provider.get_embeddings(embedding_type)
        retriever = self.__build_retriever(embeddings, collection_name, retrieve_size=5)

        if conversational_mode is True:
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
                retriever=retriever,
                memory=ConversationBufferMemory(memory_key="chat_history", return_messages=True),
                verbose=True,
                combine_docs_chain=final_qa_chain,
            )
            # qa.__init__()
            return qa
        else:
            staff_question_prompt_template = """
                下面将给你一个“问题”和一些“已知信息”，请判断这个“问题”是否可以从“已知信息”中得到答案。
                若可以从“已知信息”中获取答案，请直接输出答案。
                若不可以从“已知信息”中获取答案，请回答“根据已知信息无法回答”。ALWAYS return a "SOURCE" part in your answer from.

                 ==================================== 
                已知信息:
                {summaries}
                ====================================
                问题：
                {question}
                ====================================
                 AI:
                 Source:"""

            STAFF_QUESTION_PROMPT: PromptTemplate = PromptTemplate(template=staff_question_prompt_template,
                                                                   input_variables=["summaries", "question"])
            chain_type_kwargs = {
                "prompt": STAFF_QUESTION_PROMPT,  # Prompts
                "verbose": True
            }
            qa = RetrievalQAWithSourcesChain.from_chain_type(
                retriever=retriever,
                llm=llm,
                verbose=True,
                chain_type_kwargs=chain_type_kwargs
            )

            return qa

    # def talk(self, prompt, history=[]):
    #     """
    #     对话
    #     :param prompt:
    #     :param history:
    #     :return:
    #     """
    #     if self.chain is None:
    #         self.chain = self.build_chain()
    #
    #     test = self.chain({"question": prompt, "chat_history": history})
    #     print(f"chain最终返回值是{test}")
    #     return test['answer']

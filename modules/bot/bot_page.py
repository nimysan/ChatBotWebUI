import gradio as gr
from langchain.embeddings import OpenAIEmbeddings

# from modules.bot import bot_pg_chatgpt
from modules.bot import bot_pg_sagemaker
from modules.bot.bot import KnowledgeBot
from modules.bot.bot_builder import BotBuilder
# from modules.bot import bot_pg_bedrock
from modules.bot.bot_pg_chatgpt import CHAT_MEMORY
from modules.bot.bot_pg_sagemaker import SagemakerKnowledgeBot
from modules.bot.embeddings_builder import EmbeddingsProvider
from modules.config import bot_config
from modules.config.bot_config import get_config
from modules.vectorstore import store_pg
from modules.vectorstore.store_pg import refresh_collections, EXIST_COLLECTIONS, compose_pg_connection_string
import threading


# 调用链条去发布一个服务
def run_chain(chain, prompt: str, history=[]):
    return chain({"question": prompt, "chat_history": history})


def build_retriever(embeddings, collection_name, retrieve_size=2):
    """
    Retrieve的读写， Embeddings必须是同一个
    :param embeddings:
    :param collection_name:
    :param retrieve_size:
    :return:
    """
    connection_string = compose_pg_connection_string(*bot_config.get_config("pg_config"))
    print(f"build_retriever store for {connection_string} with collection name {collection_name}")
    return store_pg.as_retriever(embeddings, collection_name, connection_string, retrieve_size)


co = build_retriever(EmbeddingsProvider().embeddings(), "s3titan", 2)
bot = BotBuilder(co, False)
with gr.Blocks(
        theme=gr.themes.Monochrome(),
        css="""#btn {background: red; color: red} .abc {background-color:red; font-family: "Comic Sans MS", "Comic Sans",
        cursive !important} """
) as chatbot_page:
    # gr.themes.builder()
    gr.Markdown(
        """
        # 智能聊天机器人!
        you need to click *Build Bot* after you change configuration to make it work
        """
    )
    with gr.Column():
        with gr.Row():
            with gr.Column():
                chatbot = gr.Chatbot()
                msg = gr.Textbox(label="Input your query")
                clear = gr.ClearButton([msg, chatbot])

            # t_history = gr.Textbox(label="chat history")


        def langchain_bot(message, chat_history):
            chat_history.append((message, bot.talk(message)))
            return "", chat_history


        msg.submit(langchain_bot, [msg, chatbot],
                   [msg, chatbot])

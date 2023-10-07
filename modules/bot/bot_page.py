import gradio as gr
# from modules.bot import bot_pg_chatgpt
from modules.bot import bot_pg_sagemaker
from modules.bot.bot import KnowledgeBot
# from modules.bot import bot_pg_bedrock
from modules.bot.bot_pg_chatgpt import CHAT_MEMORY
from modules.bot.bot_pg_sagemaker import SagemakerKnowledgeBot
from modules.config.bot_config import get_config
from modules.vectorstore.store_pg import refresh_collections, EXIST_COLLECTIONS
import threading


# 调用链条去发布一个服务
def run_chain(chain, prompt: str, history=[]):
    return chain({"question": prompt, "chat_history": history})


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


        def langchain_bot(message, collection, conversation, chat_history):
            # bot = KnowledgeBot()
            # print(f"threading is {threading.current_thread()}")
            # if collection is None:
            #     gr.Warning("you must select collection")
            # print(f"arguments {message} -> collection {collection}  -> history: {chat_history}")
            #
            # # work_chain = chain
            # # if not callable(work_chain):
            # work_chain = bot_pg_sagemaker.build_chain(collection_name=collection)
            # resp = run_chain(work_chain, message, history=chat_history)  # 每次临时build一个？
            # resp_message = resp.get("answer", "")
            # chat_history.append((message, bot.talk(message)))
            return "", chat_history


        # msg.submit(langchain_bot, [msg, t_collection_selector, t_conversation_mode, chatbot],
        #            [msg, chatbot])

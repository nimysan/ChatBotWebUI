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


def list_collections():
    cos = refresh_collections();
    return gr.Dropdown.update(choices=cos)


with gr.Blocks(
        theme=gr.themes.Monochrome(),
        css="""#btn {background: red; color: red} .abc {background-color:red; font-family: "Comic Sans MS", "Comic Sans",
        cursive !important} """
) as chatbot_page:
    bot = SagemakerKnowledgeBot("test", True)


    def rebuild_bot(knowledge_collection, conversational_mode):
        """
        read config and build bot (Session Level)

        bot will be build by manager but user can choose their collection
        :return:
        """
        print(chatbot_page)

        return ""


    # gr.themes.builder()
    gr.Markdown(
        """
        # 智能聊天机器人!
        you need to click *Build Bot* after you change configuration to make it work
        """
    )
    cos = refresh_collections()
    cc = gr.State()
    with gr.Accordion("Bot Setup", open=False):
        with gr.Accordion("LLM settings"):
            gr.Markdown("lorem ipsum")

        with gr.Accordion("Embeddings settings"):
            gr.Markdown("lorem ipsum")

        with gr.Accordion("Knowledge settings"):
            t_collection_selector = gr.Dropdown(
                cos, label="Choose knowledge collection", info="Knowledge will bases on this",
            )
            t_refresh_collections = gr.Button(value="Load Collections")
            t_refresh_collections.click(fn=list_collections, outputs=t_collection_selector)

        with gr.Accordion("Conversational settings"):
            t_conversation_mode = gr.Checkbox(label="Conversational mode?")

        t_build_bot = gr.Button(value="Build Bot", elem_id="btn")
        t_build_bot.click(fn=rebuild_bot, inputs=[t_collection_selector, t_conversation_mode],
                          outputs=[])

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
            chat_history.append((message, bot.talk(message)))
            return "", chat_history


        msg.submit(langchain_bot, [msg, t_collection_selector, t_conversation_mode, chatbot],
                   [msg, chatbot])

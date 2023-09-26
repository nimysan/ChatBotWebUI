import gradio as gr
# from modules.bot import bot_pg_chatgpt
from modules.bot import bot_pg_sagemaker
# from modules.bot import bot_pg_bedrock
from modules.bot.bot_pg_chatgpt import CHAT_MEMORY
from modules.vectorstore.store_pg import refresh_collections, EXIST_COLLECTIONS
import threading


# 调用链条去发布一个服务
def run_chain(chain, prompt: str, history=[]):
    return chain({"question": prompt, "chat_history": history})


def list_collections():
    cos = refresh_collections();
    return gr.Dropdown.update(choices=cos)


current_chain = None;


def reload_chain(collection, conversation, state):
    # # current_chain = bot_pg_chatgpt.build_chain(collection, conversation)
    # print(CHAT_MEMORY)
    # # CHAT_MEMORY.clear()

    # TODO
    return ""


with gr.Blocks(
        css="""#btn {background: red; color: red} .abc {background-color:red; font-family: "Comic Sans MS", "Comic Sans", 
        cursive !important} """
) as chatbot_page:
    gr.Markdown(
        """
        # 智能聊天机器人!
        you need to click Reload Button after you change configuration to make it work
        """
    )
    cos = refresh_collections()
    cc = gr.State()
    # collections = EXIST_COLLECTIONS
    with gr.Row():
        with gr.Column(scale=1, min_width=600):
            with gr.Row():
                t_collection_selector = gr.Dropdown(
                    cos, label="Select Knowledge Collection", info="Knowledge will bases on this",
                )
                t_refresh_collections = gr.Button(value="Load Connections")
                t_refresh_collections.click(fn=list_collections, outputs=t_collection_selector)

            t_conversation_mode = gr.Checkbox(label="Conversational mode?")
            t_reload_chain = gr.Button(value="Reload", elem_id="btn", elem_classes=['abc'])

            t_reload_chain.click(fn=reload_chain, inputs=[t_collection_selector, t_conversation_mode],
                                 outputs=[])

        with gr.Row():
            with gr.Column():
                chatbot = gr.Chatbot()
                msg = gr.Textbox(label="Input your query")
                clear = gr.ClearButton([msg, chatbot])

            # t_history = gr.Textbox(label="chat history")


        def langchain_bot(message, collection, conversation, chat_history):
            print(f"threading is {threading.current_thread()}")
            if collection is None:
                gr.Warning("you must select collection")
            print(f"arguments {message} -> collection {collection}  -> history: {chat_history}")

            # work_chain = chain
            # if not callable(work_chain):
            work_chain = bot_pg_sagemaker.build_chain(collection_name=collection)
            resp = run_chain(work_chain, message, history=chat_history)  # 每次临时build一个？
            resp_message = resp.get("answer", "")
            chat_history.append((message, resp_message))
            return "", chat_history, work_chain
            # try:
            #     # work_chain = bot_pg_chatgpt.build_chain(collection, conversation)
            #
            # except Exception as e:
            #     raise gr.Error(f"Please check your configuration. The error is {e}")


        msg.submit(langchain_bot, [msg, t_collection_selector, t_conversation_mode, chatbot],
                   [msg, chatbot])

import gradio as gr

# from modules.bot import bot_pg_chatgpt
from modules.bot.bot_builder import BotBuilder
from modules.config import bot_config
from modules.vectorstore.store_pg import refresh_collections


# from modules.bot import bot_pg_bedrock

def list_collections():
    return gr.Dropdown.update(choices=refresh_collections())


# 调用链条去发布一个服务
def run_chain(bot_chain, prompt: str, history=[]):
    return bot_chain({"question": prompt, "chat_history": history})


bot_builder = BotBuilder()


def rebuild_bot(collection_name, conversational_mode):
    bot_config_value = bot_config.get_config("bot")
    llm_type = bot_config_value["llm"]
    embedding_type = bot_config_value["embeddings"]
    print(f"### build with {llm_type} and embeddings {embedding_type}")
    chain = bot_builder.build_chain(collection_name, conversational_mode, bot_config_value["llm"],
                                    bot_config_value["embeddings"])
    print(f"rebuild bot")
    return f"""
   > Chain information with 
   ```json
   {bot_config_value}
   ```
   in collection *{collection_name}* with conversation_mode: {conversational_mode}
   """


chain = BotBuilder().build_chain("s3titan", True, "bedrock", "bedrock")
with gr.Blocks(
        # theme=gr.themes.Monochrome(),
        # # css="""#btn {background: red; color: red} .abc {background-color:red; font-family: "Comic Sans MS", "Comic Sans",
        # # cursive !important} """
) as chatbot_page:
    with gr.Row():
        with gr.Column():
            with gr.Row():
                cos = refresh_collections()

                t_collection_selector = gr.Dropdown(
                    cos, label="Choose knowledge collection",
                    info="Knowledge will bases on this", scale=3
                )
                gr.Dropdown.update(choices=refresh_collections())
                t_refresh_collections = gr.Button(value="Load Collections", scale=1)
                t_refresh_collections.click(fn=list_collections, outputs=t_collection_selector)

            t_conversation_mode = gr.Checkbox(label="Conversational mode?")

            t_build_bot = gr.Button(value="Build Bot", elem_id="btn")

            bot_config_value = bot_config.get_config("bot")
            config_show = gr.Markdown("""
            """)
            t_build_bot.click(fn=rebuild_bot, inputs=[t_collection_selector, t_conversation_mode],
                              outputs=[config_show])
        with gr.Row():
            with gr.Column():
                chatbot = gr.Chatbot()
                msg = gr.Textbox(label="Input your query")
                clear = gr.ClearButton([msg, chatbot])


            def langchain_bot(message, chat_history):
                resp = chain({"question": message, "chat_history": chat_history})
                chat_history.append((message, resp['answer']))
                return "", chat_history


            msg.submit(langchain_bot, [msg, chatbot],
                       [msg, chatbot])

chatbot_page.launch(server_name="0.0.0.0", server_port=7862)

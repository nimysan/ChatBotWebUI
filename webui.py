import gradio as gr

from modules.bot.bot_builder import BotBuilder
from modules.config import bot_config
from modules.vectorstore.store_pg import refresh_collections


def list_collections():
    return gr.Dropdown.update(choices=refresh_collections())


bot_builder = BotBuilder()


def build_chain(collection_name, conversational_mode):
    print(f"the c name is {collection_name} and mode is {conversational_mode}")
    config_value = bot_config.get_config("bot")
    llm_type = config_value["llm"]
    embedding_type = config_value["embeddings"]
    print(f"### build with {llm_type} and embeddings {embedding_type}")
    bot_chain = bot_builder.build_chain(collection_name, conversational_mode, config_value["llm"],
                                        config_value["embeddings"])
    return bot_chain


def rebuild_bot(collection_name, conversational_mode, old_state):
    config_value = bot_config.get_config("bot")
    msg = f"""
   > Chain information with 
   ```json
   {config_value}
   ```
   in collection *{collection_name}* with conversation_mode: {conversational_mode}
   """
    return [msg, {
        'c': collection_name,
        'mode': conversational_mode,
        'chain': build_chain(collection_name, conversational_mode)
    }, '', []]


def show_session(session_bot):
    return session_bot


with gr.Blocks(
        # theme=gr.themes.Monochrome(),
        # # css="""#btn {background: red; color: red} .abc {background-color:red; font-family: "Comic Sans MS", "Comic Sans",
        # # cursive !important} """
) as chatbot_page:
    session_bot = gr.State({})
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
            # t_show_session = gr.Button(value="show session")

            bot_config_value = bot_config.get_config("bot")
            config_show = gr.Markdown("""
            """)
            # session_text = gr.TextArea(lines=20)

            # t_show_session.click(fn=show_session, inputs=[session_bot], outputs=[session_text])
        with gr.Row():
            with gr.Column():
                chatbot = gr.Chatbot()
                msg = gr.Textbox(label="Input your query")
                clear_btn = gr.ClearButton([msg, chatbot])


            def talk(message, chat_history, state):
                # if not hasattr(state, 'chain'):
                #     raise gr.Error("you must select collection and build bot before chat")
                #     return "", []
                chain_exist = 'chain' in state
                if chain_exist:

                    bot_chain = state['chain']

                    # print(f"bot_chain bot: {bot_chain}")
                    resp = bot_chain({"question": message, "chat_history": chat_history})
                    chat_history.append((message, resp['answer']))
                    return "", chat_history
                else:
                    raise gr.Error("you must select collection and build bot before chat")
                    return "", chat_history


            msg.submit(talk, [msg, chatbot, session_bot],
                       [msg, chatbot])

            t_build_bot.click(fn=rebuild_bot, inputs=[t_collection_selector, t_conversation_mode, session_bot],
                              outputs=[config_show, session_bot, msg, chatbot])

chatbot_page.launch(server_name="0.0.0.0", server_port=7865)

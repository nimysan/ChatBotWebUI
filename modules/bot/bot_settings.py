import gradio as gr

from modules.vectorstore.store_pg import refresh_collections


def rebuild_bot(knowledge_collection, conversational_mode):
    """
    read config and build bot (Session Level)

    bot will be build by manager but user can choose their collection
    :return:
    """
    # print(chatbot_page)

    return ""


def list_collections():
    cos = refresh_collections();
    return gr.Dropdown.update(choices=cos)


with gr.Blocks(
        theme=gr.themes.Monochrome(),
        css="""#btn {background: red; color: red} .abc {background-color:red; font-family: "Comic Sans MS", "Comic Sans",
        cursive !important} """
) as bot_settings_page:
    cos = refresh_collections()
    gr.Radio(["bedrock-claude-v2", "sagemaker-baichuan", "openai"], label="LLM", info="LLM for RAG?")
    gr.Radio(["sagemaker-baichuan", "openai"], label="Embedding", info="Embeddings for RAG?")
    t_collection_selector = gr.Dropdown(
        cos, label="Choose knowledge collection", info="Knowledge will bases on this",
    )
    t_refresh_collections = gr.Button(value="Load Collections")
    t_refresh_collections.click(fn=list_collections, outputs=t_collection_selector)

    t_conversation_mode = gr.Checkbox(label="Conversational mode?")

    t_build_bot = gr.Button(value="Build Bot", elem_id="btn")
    t_build_bot.click(fn=rebuild_bot, inputs=[t_collection_selector, t_conversation_mode],
                      outputs=[])

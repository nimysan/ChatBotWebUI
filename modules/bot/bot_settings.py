import gradio as gr

from modules.config import bot_config
from modules.config.bot_config import get_config, write_config
# from modules.config.pg_config import write_openai_config
from modules.sagemaker.sm_utils import SageMakerContext
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


def save_bedrock_llm(region, model_id):
    bot_config.write_config("bedrock_llm", {
        "region": region,
        "model_id": model_id
    })


def save_bedrock_embeddings(region, model_id):
    bot_config.write_config("bedrock_embeddings", {
        "region": region,
        "model_id": model_id
    })


def write_openai_config(key_input):
    return write_config("openai_key", key_input)


def save_sm_config(llm_endpoint_region, llm_endpoint, llm_endpoint_embedding_region,
                   llm_endpoint_embedding):
    """
    保存
    :param endpoint:
    :param embeddings_endpoint:
    :return:
    """
    write_config("sagemaker_embeddings_endpoint", {
        "endpoint": llm_endpoint_embedding,
        "region": llm_endpoint_embedding_region
    })
    write_config("sagemaker_llm_endpoint", {
        "endpoint": llm_endpoint,
        "region": llm_endpoint_region
    })
    # write_config("sm_embeddings_endpoint", embeddings_endpoint)


def save_bot(llm, embeddings):
    write_config("bot", {
        "llm": llm,
        "embeddings": embeddings
    })


with gr.Blocks() as bot_settings_page:
    with gr.Accordion("Bot LLM&Embeddings Setup"):
        gr.Markdown(
            """
            # Setup your Chatbot
            """)
        bot_config_value = bot_config.get_config("bot")
        bot_llm_radio = gr.Radio(["bedrock", "sagemaker", "openai"], label="LLM", info="LLM for RAG",
                                 value=bot_config_value['llm'])
        bot_embeddings_radio = gr.Radio(["bedrock", "sagemaker", "openai"], label="Embedding",
                                        info="Embeddings for RAG", value=bot_config_value['embeddings'])
        bot_btn = gr.Button(value="Save&Check")
        bot_btn.click(fn=save_bot, inputs=[bot_llm_radio, bot_embeddings_radio])

    with gr.Accordion("Amazon Bedrock"):
        gr.Markdown(
            """
            # Setup your bedrock!
            [Amazon Bedrock user guide](https://docs.aws.amazon.com/zh_cn/bedrock/latest/userguide/what-is-service.html)
            """)
        with gr.Row():
            with gr.Accordion("Amazon Bedrock LLM"):
                bedrock_llm_region = gr.Textbox(label="Amazon Bedrock Region", value="us-west-2")
                bedrock_llm_model_id = gr.Textbox(label="Amazon Bedrock Model Id", value="anthropic.claude-v2")
                btn_save_llm = gr.Button(value="Save")
                btn_save_llm.click(fn=save_bedrock_llm, inputs=[bedrock_llm_region, bedrock_llm_model_id])
            with gr.Accordion("Amazon Bedrock Embeddings"):
                bedrock_embeddings_region = gr.Textbox(label="Amazon Bedrock Region", value="us-west-2")
                bedrock_embeddings_model_id = gr.Textbox(label="Amazon Bedrock Model Id",
                                                         value="amazon.titan-embed-text-v1")
                btn_save_embeddings = gr.Button(value="Save")
                btn_save_embeddings.click(fn=save_bedrock_embeddings,
                                          inputs=[bedrock_embeddings_region, bedrock_embeddings_model_id])

    with gr.Accordion("Amazon SageMaker Endpoints"):
        gr.Markdown(
            """
            # Setup SageMaker Endpoints
            """
        )
        sagemaker_context = SageMakerContext(region="us-east-1")  # TODO close region for ec2
        with gr.Row() as deploy_action:
            with gr.Column() as sagemaker_llm_config:
                sample_prompts = """下面将给你一个“问题”和一些“已知信息”，请判断这个“问题”是否可以从“已知信息”中得到答案。
    若可以从“已知信息”中获取答案，请直接输出答案。
    若不可以从“已知信息”中获取答案，请回答“根据已知信息无法回答”。
     ==================================== 
    已知信息:
    S3支持智能分层
    ====================================
    问题：
    S3支持智能分层吗？
    ====================================
    AI:"""
                llm_endpoint = gr.Text(label="SageMaker Endpoint name for RAG(LLM)",
                                       value="ChatGLM-6B-SageMaker-2023-09-27-14-35-40-172")
                llm_endpoint_region = gr.Text(label="Region SageMaker Endpoint name for RAG",
                                              value="us-west-2")
                llm_endpoint_input = gr.Text(label="Input your question here", value=sample_prompts, lines=5)
                llm_endpoint_output = gr.Text(label="Output will display here")
                with gr.Row():
                    llm_deploy_btn = gr.Button(value="Deploy LLM Model")
                    try_llm_btn = gr.Button(value="Try LLM")

                    llm_deploy_btn.click(fn=sagemaker_context.deploy_llm_sm, inputs=[], outputs=[llm_endpoint])
                    try_llm_btn.click(sagemaker_context.call_llm_sm, inputs=[llm_endpoint, llm_endpoint_input],
                                      outputs=[llm_endpoint_output])

            with gr.Column() as sagemaker_embedding_config:
                llm_endpoint_embedding_region = gr.Text(label="Region SageMaker Endpoint name for RAG(Embedding)",
                                                        value="us-west-2")
                llm_endpoint_embedding = gr.Text(label="SageMaker Endpoint name for RAG(Embedding)",
                                                 value="huggingface-pytorch-inference-2023-09-28-08-24-28-262")
                llm_endpoint_embedding_input = gr.Text(label="Input your question here", value="this is happy person")
                llm_endpoint_embedding_output = gr.Text(label="Output will display here")

                with gr.Row():
                    embeddings_deploy_btn = gr.Button(value="Deploy Embeddings Model")
                    embeddings_deploy_btn.click(fn=sagemaker_context.deploy_embeddings_model, inputs=[],
                                                outputs=[llm_endpoint_embedding])
                    try_embedding_btn = gr.Button(value="Try Embedding")
                    try_embedding_btn.click(sagemaker_context.call_embeddings,
                                            inputs=[llm_endpoint_embedding, llm_endpoint_embedding_input],
                                            outputs=[llm_endpoint_embedding_output])

        with gr.Column() as sagemaker_embedding_save:
            save_btn = gr.Button(value="Save")
            save_btn.click(fn=save_sm_config,
                           inputs=[llm_endpoint_region, llm_endpoint, llm_endpoint_embedding_region,
                                   llm_endpoint_embedding], outputs=[])

    with gr.Accordion("OpenAI"):
        gr.Markdown(
            """
            # Setup your OpenAI
            [OpenAI account link](https://platform.openai.com)
            """)
        openapi_key = get_config("openai_key") or 'sk-xxxxxxxx'
        t_openai_key = gr.Text(placeholder="Please input your openai key", label="OpenAI Key", type="password",
                               value=openapi_key)
        t_openai_btn = gr.Button("Save")
        t_openai_btn.click(write_openai_config, inputs=t_openai_key)

    cos = refresh_collections()

    t_collection_selector = gr.Dropdown(
        cos, label="Choose knowledge collection", info="Knowledge will bases on this",
    )
    t_refresh_collections = gr.Button(value="Load Collections")
    t_refresh_collections.click(fn=list_collections, outputs=t_collection_selector)

    t_conversation_mode = gr.Checkbox(label="Conversational mode?")

    t_build_bot = gr.Button(value="Build Bot", elem_id="btn")
    t_build_bot.click(fn=rebuild_bot, inputs=[t_collection_selector, t_conversation_mode],
                      outputs=[])

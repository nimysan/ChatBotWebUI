import gradio as gr

from modules.sagemaker.sm_utils import SageMakerContext
from modules.config.bot_config import write_config


def save_sm_config(endpoint, embeddings_endpoint):
    """
    保存
    :param endpoint:
    :param embeddings_endpoint:
    :return:
    """
    write_config("sm_endpoint", endpoint)
    write_config("sm_embeddings_endpoint", embeddings_endpoint)


with gr.Blocks() as sm_configure_page:
    sagemaker_context = SageMakerContext(region="us-east-1")  # TODO close region for ec2
    gr.Markdown(
        """
        # 配置SageMaker
        Start typing below to see the output.
        """)
    with gr.Row() as deploy_action:
        llm_deploy_btn = gr.Button(value="部署ChatGLM")

        # llm_deploy_btn.click(fn=)
        embeddings_deploy_btn = gr.Button(value="部署Embedding")

    with gr.Column() as sagemaker_llm_config:
        sample_prompts = """
            下面将给你一个“问题”和一些“已知信息”，请判断这个“问题”是否可以从“已知信息”中得到答案。
            若可以从“已知信息”中获取答案，请直接输出答案。
            若不可以从“已知信息”中获取答案，请回答“根据已知信息无法回答”。
             ==================================== 
            已知信息:
            {context}
            ====================================
            问题：
            {question}
            ====================================
             AI:
        """
        llm_endpoint = gr.Text(label="SageMaker Endpoint name for RAG(LLM)",
                               value="ChatGLM-6B-SageMaker-2023-09-27-14-35-40-172")
        llm_endpoint_input = gr.Text(label="Input your question here", value=sample_prompts)
        llm_endpoint_output = gr.Text(label="Output will display here")
        try_llm_btn = gr.Button(value="Test LLM")

        try_llm_btn.click(sagemaker_context.call_llm_sm, inputs=[llm_endpoint, llm_endpoint_input],
                          outputs=[llm_endpoint_output])

    with gr.Column() as sagemaker_embedding_config:
        llm_endpoint_embedding = gr.Text(label="SageMaker Endpoint name for RAG(Embedding)",
                                         value="huggingface-pytorch-inference-2023-09-28-05-38-44-863")
        llm_endpoint_embedding_input = gr.Text(label="Input your question here", value="this is happy person")
        llm_endpoint_embedding_output = gr.Text(label="Output will display here")
        try_embedding_btn = gr.Button(value="Test Embedding")

        try_embedding_btn.click(sagemaker_context.call_embeddings,
                                inputs=[llm_endpoint_embedding, llm_endpoint_embedding_input],
                                outputs=[llm_endpoint_embedding_output])

        embeddings_deploy_btn.click(fn=sagemaker_context.deploy_embeddings_model, inputs=[],
                                    outputs=[llm_endpoint_embedding])
        llm_deploy_btn.click(fn=sagemaker_context.deploy_llm_sm, inputs=[], outputs=[llm_endpoint])

    with gr.Column() as sagemaker_embedding_save:
        save_btn = gr.Button(value="Save")
        save_btn.click(fn=save_sm_config, inputs=[llm_endpoint, llm_endpoint_embedding], outputs=[])

import json

import gradio as gr
from sagemaker import Predictor
from sagemaker.base_deserializers import JSONDeserializer
from sagemaker.base_serializers import JSONSerializer
from sagemaker.huggingface import HuggingFacePredictor

from modules.sagemaker.deploy_embedding_endpoint import deploy_embeddings_model
from modules.sagemaker.deploy_endpoint import deploy_llm_sm


def call_llm_sm(endpoint, input):
    print(f"endpoint")
    predictor = Predictor(endpoint,
                          serializer=JSONSerializer(),
                          deserializer=JSONDeserializer()
                          )
    inputs = {
        "ask": input
    }
    inference_response = predictor.predict(inputs)
    return inference_response["answer"]


"""
2023-09-26T09:30:07,729 [INFO ] W-shibing624__text2vec-bge--1-stdout com.amazonaws.ml.mms.wlm.WorkerLifeCycle - mms.service.PredictionException: "Unknown task sentence-similarity, available tasks are ['audio-classification', 'automatic-speech-recognition', 'conversational', 'depth-estimation', 'document-question-answering', 'feature-extraction', 'fill-mask', 'image-classification', 'image-segmentation', 'image-to-text', 'ner', 'object-detection', 'question-answering', 'sentiment-analysis', 'summarization', 'table-question-answering', 'text-classification', 'text-generation', 'text2text-generation', 'token-classification', 'translation', 'video-classification', 'visual-question-answering', 'vqa', 'zero-shot-classification', 'zero-shot-image-classification', 'zero-shot-object-detection', 'translation_XX_to_YY']" : 400
"""


def call_embeddings(endpoint, input):
    # predictor = Predictor(endpoint);
    hfp = HuggingFacePredictor(endpoint)
    inference_response = hfp.predict({
        "inputs": input
    })
    return inference_response


with gr.Blocks() as sm_configure_page:
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
        llm_endpoint = gr.Text(label="SageMaker Endpoint name for RAG(LLM)", value="chatglm-6b-2023-09-26-08-36-32-960")
        llm_endpoint_input = gr.Text(label="Input your question here", value=sample_prompts)
        llm_endpoint_output = gr.Text(label="Output will display here")
        try_llm_btn = gr.Button(value="Test LLM")

        try_llm_btn.click(call_llm_sm, inputs=[llm_endpoint, llm_endpoint_input], outputs=[llm_endpoint_output])

    with gr.Column() as sagemaker_embedding_config:
        llm_endpoint_embedding = gr.Text(label="SageMaker Endpoint name for RAG(Embedding)",
                                         value="huggingface-pytorch-inference-2023-09-27-01-19-46-799")
        llm_endpoint_embedding_input = gr.Text(label="Input your question here", value="this is happy person")
        llm_endpoint_embedding_output = gr.Text(label="Output will display here")
        try_embedding_btn = gr.Button(value="Test Embedding")

        try_embedding_btn.click(call_embeddings, inputs=[llm_endpoint_embedding, llm_endpoint_embedding_input],
                                outputs=[llm_endpoint_embedding_output])

        embeddings_deploy_btn.click(fn=deploy_embeddings_model, inputs=[], outputs=[llm_endpoint_embedding])
        llm_deploy_btn.click(fn=deploy_llm_sm, inputs=[], outputs=[llm_endpoint])

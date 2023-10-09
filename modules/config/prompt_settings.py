import gradio as gr

from modules.config.bot_config import write_config
from modules.config.bot_config import get_config


def write_configuration(condense_text, qa_conversation_prompt, qa_text):
    write_config("prompts", {
        "condense_prompt": condense_text,
        "qa_conversation_prompt": qa_conversation_prompt,
        "qa_prompt": qa_text
    })
    return [condense_text, qa_conversation_prompt, qa_text]


with gr.Blocks() as prompt_setting_config:
    with gr.Column():
        prompts_value = get_config("prompts") or {
            "condense_prompt":
                """鉴于以下对话和后续问题，将后续问题改写为
                是一个独立的问题，用其原始语言。确保避免使用任何不清楚的代词。
                Chat History:
                {chat_history}
                接下来的提问: {question}
                转化后的问题:""",
            "qa_conversation_prompt": """使用以下上下文来回答最后的问题。
                如果你不知道答案，就说你不知道，不要试图编造答案。
                最多使用三个句子，并尽可能保持答案简洁。
                总是说“谢谢您的提问！”在答案的开头。始终在答案中返回“来源”部分。 
                {context}
                问题: {question}
                我的答案是:""",
            "qa_prompt":
                """使用以下上下文来回答最后的问题。
                如果你不知道答案，就说你不知道，不要试图编造答案。
                最多使用三个句子，并尽可能保持答案简洁。
                总是说“谢谢您的提问！”在答案的开头。始终在答案中返回“来源”部分。 
                {context}
                问题: {question}
                我的答案是:"""
        }
        gr.Markdown("""
        # Prompts for difference model
        [Retrieval Augmented Generation (RAG)](https://docs.aws.amazon.com/zh_cn/sagemaker/latest/dg/jumpstart-foundation-models-customize-rag.html)
        """)
        t_condense_prompt = gr.Text(label="Condense Prompt", type="text", value=prompts_value['condense_prompt'],
                                    lines=8)
        t_qa_conversation_prompt = gr.Text(label="Conversation QA Prompt", type="text",
                                           value=prompts_value['qa_conversation_prompt'],
                                           lines=8)
        t_qa_prompt = gr.Text(label="QA Prompt", type="text", value=prompts_value['qa_prompt'], lines=8)
        btn = gr.Button("Save")
        btn.click(fn=write_configuration,
                  inputs=[t_condense_prompt, t_qa_conversation_prompt, t_qa_prompt],
                  outputs=[t_condense_prompt, t_qa_conversation_prompt, t_qa_prompt])

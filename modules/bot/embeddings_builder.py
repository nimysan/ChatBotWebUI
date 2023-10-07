from langchain.embeddings import BedrockEmbeddings, OpenAIEmbeddings

from modules.config import bot_config


class EmbeddingsProvider:
    def __init__(self):
        print("Embeddings provider")

    def __build_bedrock_titan_embeddings(self):
        embeddings = BedrockEmbeddings(
            region_name="us-west-2",
            model_id="amazon.titan-embed-text-v1",
            credentials_profile_name="gws"
        )
        return embeddings

    def __build_openai_embeddings(self):
        return OpenAIEmbeddings(openai_api_key=bot_config.get_config("openai_key"))

    def embeddings(self):
        return self.__build_bedrock_titan_embeddings()

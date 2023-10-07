import json
from typing import List, Dict

from langchain.embeddings import BedrockEmbeddings, OpenAIEmbeddings
from langchain.embeddings.sagemaker_endpoint import EmbeddingsContentHandler, SagemakerEndpointEmbeddings

from modules.config import bot_config


class EmbeddingsProvider:
    """
    given embedding provider
    """

    def __init__(self):
        self.__version__ = "1.0"

    def __build_bedrock_titan_embeddings(self):
        bedrock_embeddings_config = bot_config.get_config("bedrock_embeddings")
        embeddings = BedrockEmbeddings(
            region_name=bedrock_embeddings_config["region"],
            model_id=bedrock_embeddings_config["model_id"]
        )
        return embeddings

    def __build_openai_embeddings(self):
        return OpenAIEmbeddings(openai_api_key=bot_config.get_config("openai_key"))

    def __build_sagemaker_embeddings(self):
        class EmbeddingContentHandler(EmbeddingsContentHandler):
            content_type = "application/json"
            accepts = "application/json"

            def transform_input(self, inputs: list[str], model_kwargs: Dict) -> bytes:
                """
                Transforms the input into bytes that can be consumed by SageMaker endpoint.
                Args:
                    inputs: List of input strings.
                    model_kwargs: Additional keyword arguments to be passed to the endpoint.
                Returns:
                    The transformed bytes input.
                """
                # Example: inference.py expects a JSON string with a "inputs" key:
                print(f"input is {len(inputs)}")
                input_str = json.dumps({"inputs": inputs[1:3], **model_kwargs})
                return input_str.encode("utf-8")

            def transform_output(self, output: bytes) -> List[List[float]]:
                """
                Transforms the bytes output from the endpoint into a list of embeddings.
                Args:
                    output: The bytes output from SageMaker endpoint.
                Returns:
                    The transformed output - list of embeddings
                Note:
                    The length of the outer list is the number of input strings.
                    The length of the inner lists is the embedding dimension.
                """
                # Example: inference.py returns a JSON string with the list of
                # embeddings in a "vectors" key:

                # 参考实现： https://github.com/aws-solutions-library-samples/guidance-for-custom-search-of-an-enterprise-knowledge-base-on-aws/blob/jupyter/data_load/smart_search.py
                response_json = json.loads(output.read().decode("utf-8"))
                return response_json[0][0]
                # if language.find("chinese") >= 0:
                #
                # else:
                #     return response_json

        embedding_content_handler = EmbeddingContentHandler()
        sagemaker_embeddings_endpoint = bot_config.get_config("sagemaker_embeddings_endpoint")
        embeddings = SagemakerEndpointEmbeddings(
            # credentials_profile_name="credentials-profile-name",
            endpoint_name=sagemaker_embeddings_endpoint["endpoint"],
            region_name=sagemaker_embeddings_endpoint["region"],
            content_handler=embedding_content_handler,
        )
        return embeddings

    def get_embeddings(self, embeddings_type="bedrock"):
        """
                :param embeddings_type:  bedrock/sagemaker/openai
                """
        print(f"Embeddings provider type is {embeddings_type}")
        embeddings = None
        if embeddings_type is "bedrock":
            embeddings = self.__build_bedrock_titan_embeddings()
        elif embeddings_type is "sagemaker":
            embeddings = self.__build_sagemaker_embeddings()
        elif embeddings_type is "openai":
            embeddings = self.__build_openai_embeddings()
        else:
            raise "Embeddings type only allow: bedrock/sagemaker/openai"
        return embeddings

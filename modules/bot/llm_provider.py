import json

from langchain.llms.bedrock import Bedrock
from langchain.llms.openai import OpenAI
from langchain.llms.sagemaker_endpoint import LLMContentHandler, SagemakerEndpoint

from modules.config import bot_config


class SMContentHandler(LLMContentHandler):
    content_type = "application/json"
    accepts = "application/json"

    def transform_input(self, prompt: str, model_kwargs: dict) -> bytes:
        input_str = json.dumps({"ask": prompt})
        return input_str.encode('utf-8')

    def transform_output(self, output: bytes) -> str:
        response_json = json.loads(output.read())
        return response_json['answer']


class LLMProvider:
    def __init__(self):
        print("hello")

    def get_llm(self, llm_type="bedrock"):
        """
        :param llm_type:  bedrock/sagemaker/openai
        """
        print(f"LLM provider type is {llm_type}")
        llm = None
        if llm_type == "bedrock":
            print("------ inside build bedrock ###")
            llm = self.__build_bedrock_llm()
        elif llm_type == "sagemaker":
            llm = self.__build_sagemaker_llm()
        elif llm_type == "openai":
            llm = self.__build_openai_llm()
        else:
            raise "llm type only allow: bedrock/sagemaker/openai"
        return llm

    def __build_openai_llm(self):
        return OpenAI(batch_size=5, verbose=True, openai_api_key=bot_config.get_config("openai_key"))

    def __build_sagemaker_llm(self):
        content_handler = SMContentHandler()
        sagemaker_llm_endpoint = bot_config.get_config("sagemaker_llm_endpoint")
        print(f"endpoint name is {sagemaker_llm_endpoint}  ")
        llm = SagemakerEndpoint(
            endpoint_name=sagemaker_llm_endpoint["endpoint"],
            region_name=sagemaker_llm_endpoint["region"],
            model_kwargs={"temperature": 1e-10, "max_length": 500},
            content_handler=content_handler
        )
        return llm;

    def __build_bedrock_llm(self):
        bedrock_llm_config = bot_config.get_config("bedrock_llm")
        # embeddings = BedrockEmbeddings(
        llm = Bedrock(
            # credentials_profile_name="bedrock-admin",
            model_id=bedrock_llm_config['model_id'],
            region_name=bedrock_llm_config['region'],
        )
        return llm

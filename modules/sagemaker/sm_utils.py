import os
import boto3

import sagemaker
from sagemaker import Predictor
from sagemaker.huggingface import HuggingFacePredictor, HuggingFaceModel
from sagemaker.pytorch import PyTorchModel
from sagemaker.serializers import JSONSerializer
from sagemaker.deserializers import JSONDeserializer

from modules.sagemaker.ec2_utils import get_region_from_ec2_metadata


class SageMakerContext:

    def __init__(self, region='us-east-1', sagemaker_role=''):
        """
        请指定role
        :param region:
        :param sagemaker_role:
        """
        self.region = region
        self.sagemaker_role = sagemaker_role

    def _sm_session(self):
        return sagemaker.Session(boto3.session.Session(region_name=self.region))

    def call_llm_sm(self, endpoint, input_text):
        predictor = Predictor(
            endpoint,
            sagemaker_session=self._sm_session(),
            serializer=JSONSerializer(),
            deserializer=JSONDeserializer()
        )
        inputs = {
            "ask": input_text
        }
        inference_response = predictor.predict(inputs)
        return inference_response["answer"]

    def call_embeddings(self, endpoint, input_text):
        """
        -shibing624__text2vec-bge-
        :param endpoint:
        :param input_text:
        :return:
        """
        hfp = HuggingFacePredictor(
            sagemaker_session=self._sm_session(),
            endpoint_name=endpoint)
        inference_response = hfp.predict({
            "inputs": input_text
        })
        return inference_response

    def deploy_llm_sm(self, instance_type="ml.g4dn.2xlarge"):
        sagemaker_session = self._sm_session();
        bucket = sagemaker_session.default_bucket()
        s3_client = boto3.client("s3")
        print(f" cmd is {os.getcwd()}")
        model_tar = "model.tar.gz"
        response = s3_client.upload_file("./modules/sagemaker/" + model_tar, bucket, model_tar)
        print(f"the s3 upload response is {response}")
        # TODO  bucket will be created by CDK

        model_data = f"s3://{bucket}/{model_tar}"
        print(model_data)
        entry_point = 'inference-chatglm.py'
        framework_version = '1.13.1'
        py_version = 'py39'
        model_environment = {
            'SAGEMAKER_MODEL_SERVER_TIMEOUT': '600',
            'SAGEMAKER_MODEL_SERVER_WORKERS': '1',
        }

        model_name = "ChatGLM-6B-SageMaker";
        # role = "arn:aws:iam::390468416359:role/accelerate_sagemaker_execution_role";  # how to create it
        model = PyTorchModel(
            sagemaker_session=sagemaker_session,
            name=model_name,
            model_data=model_data,
            entry_point=entry_point,
            source_dir='./modules/sagemaker/code',
            role=self.sagemaker_role,
            framework_version=framework_version,
            py_version=py_version,
            env=model_environment
        )

        print(f"the model is {model}")
        endpoint_name = None
        instance_count = 1

        predictor = model.deploy(
            endpoint_name=endpoint_name,
            instance_type=instance_type,
            initial_instance_count=instance_count,
            serializer=JSONSerializer(),
            deserializer=JSONDeserializer()
        )

        return predictor

    def deploy_embeddings_model(self):
        # role = "arn:aws:iam::390468416359:role/accelerate_sagemaker_execution_role";  # how to create it
        # Hub Model configuration. https://huggingface.co/models
        # hub = {
        #     'HF_MODEL_ID': 'shibing624/text2vec-bge-large-chinese',
        #     'HF_TASK': 'feature-extraction'
        # }

        hub = {
            'HF_MODEL_ID': 'BAAI/bge-large-zh',
            'HF_TASK': 'feature-extraction'
        }
        # create Hugging Face Model Class
        huggingface_model = HuggingFaceModel(
            transformers_version='4.26.0',
            pytorch_version='1.13.1',
            py_version='py39',
            env=hub,
            role=self.sagemaker_role,
        )

        # deploy model to SageMaker Inference
        predictor = huggingface_model.deploy(
            initial_instance_count=1,  # number of instances
            instance_type='ml.g4dn.xlarge'  # ec2 instance type
        )

        return predictor;

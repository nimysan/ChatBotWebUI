import boto3
import sagemaker
from sagemaker.huggingface import HuggingFaceModel
from sagemaker.pytorch.model import PyTorchModel

role = "arn:aws:iam::390468416359:role/accelerate_sagemaker_execution_role";  # how to create it
# Hub Model configuration. https://huggingface.co/models
hub = {
	'HF_MODEL_ID':'shibing624/text2vec-bge-large-chinese',
	'HF_TASK':'feature-extraction'
}

# create Hugging Face Model Class
huggingface_model = HuggingFaceModel(
	transformers_version='4.26.0',
	pytorch_version='1.13.1',
	py_version='py39',
	env=hub,
	role=role,
)

# deploy model to SageMaker Inference
predictor = huggingface_model.deploy(
	initial_instance_count=1, # number of instances
	instance_type='ml.m5.xlarge' # ec2 instance type
)
# # 休眠2分钟,确保模型可以完全加载
# import time
#
# time.sleep(120)

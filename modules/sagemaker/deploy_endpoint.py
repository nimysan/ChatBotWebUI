import boto3
import sagemaker
from sagemaker.pytorch.model import PyTorchModel

account_id = boto3.client('sts').get_caller_identity().get('Account')
region_name = boto3.session.Session().region_name

sagemaker_session = sagemaker.Session()
bucket = sagemaker_session.default_bucket()
# role = sagemaker.get_execution_role()
print(f"sagemaker bucket is {bucket}")
s3_client = boto3.client("s3");
model_tar = "model.tar.gz"
response = s3_client.upload_file(model_tar, bucket, model_tar)
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
role = "arn:aws:iam::390468416359:role/accelerate_sagemaker_execution_role";  # how to create it
model = PyTorchModel(
    name="chatglm-6b",
    model_data=model_data,
    entry_point=entry_point,
    source_dir='./code',
    role=role,
    framework_version=framework_version,
    py_version=py_version,
    env=model_environment
)

print(f"the model is {model}")
endpoint_name = None
instance_type = 'ml.g4dn.2xlarge'
instance_count = 1

from sagemaker.serializers import JSONSerializer
from sagemaker.deserializers import JSONDeserializer

predictor = model.deploy(
    endpoint_name=endpoint_name,
    instance_type=instance_type,
    initial_instance_count=instance_count,
    serializer=JSONSerializer(),
    deserializer=JSONDeserializer()
)

# # 休眠2分钟,确保模型可以完全加载
# import time
#
# time.sleep(120)

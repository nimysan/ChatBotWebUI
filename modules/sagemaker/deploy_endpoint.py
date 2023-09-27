import os

import boto3
import sagemaker
from sagemaker.pytorch.model import PyTorchModel


def deploy_llm_sm():
    my_session = boto3.session.Session(region_name="us-east-1")
    print(f"my_session.region_name is {my_session.region_name}")
    sagemaker_session = sagemaker.Session(boto_session=my_session)
    bucket = sagemaker_session.default_bucket()
    # role = sagemaker.get_execution_role()
    print(f"sagemaker bucket is {bucket}")
    s3_client = boto3.session(my_session).client("s3");
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
    role = "arn:aws:iam::390468416359:role/accelerate_sagemaker_execution_role";  # how to create it
    model = PyTorchModel(
        sagemaker_session=sagemaker_session,
        name=model_name,
        model_data=model_data,
        entry_point=entry_point,
        source_dir='./modules/sagemaker/code',
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

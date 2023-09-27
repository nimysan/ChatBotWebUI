#参考Gradio

https://www.gradio.app/guides/creating-a-chatbot-fast

## 本地调试 需一个支持PG vector扩展的库

构造一个镜像 - 如需要

```bash
docker build -t my_postgres .
```

启动容器

```bash
docker run --name vg_my_postgres -e POSTGRES_PASSWORD=mysecretpassword -p 5432:5432 -d vg_postgres

## aws rds只i给你
```

## Flacon 7B deploy

```python
import json
import sagemaker
import boto3
from sagemaker.huggingface import HuggingFaceModel, get_huggingface_llm_image_uri

try:
    role = sagemaker.get_execution_role()
except ValueError:
    iam = boto3.client('iam')
    role = iam.get_role(RoleName='sagemaker_execution_role')['Role']['Arn']

# Hub Model configuration. https://huggingface.co/models
hub = {
    'HF_MODEL_ID': 'Linly-AI/Chinese-Falcon-7B',
    'SM_NUM_GPUS': json.dumps(1)
}

# create Hugging Face Model Class
huggingface_model = HuggingFaceModel(
    image_uri=get_huggingface_llm_image_uri("huggingface", version="0.9.3"),
    env=hub,
    role=role,
)

# deploy model to SageMaker Inference
predictor = huggingface_model.deploy(
    initial_instance_count=1,
    instance_type="ml.g5.2xlarge",
    container_startup_health_check_timeout=300,
)

# send request
predictor.predict({
    "inputs": "My name is Julien and I like to",
})

```

## Bedrock

内部试用入口： https://prod.onboard.bedrock.aws.dev/
console访问: https://us-west-2.awsc-integ.aws.amazon.com/bedrock/home?region=us-west-2#/overview
sdk访问:   https://prod.us-west-2.frontend.bedrock.aws.dev/

```json
{
  "modelId": "amazon.titan-tg1-large",
  "contentType": "application/json",
  "accept": "*/*",
  "body": "{\"inputText\":\"waht's genai?\",\"textGenerationConfig\":{\"maxTokenCount\":512,\"stopSequences\":[],\"temperature\":0,\"topP\":0.9}}"
}
```

## AWS 内部workshop链接

https://catalog.us-east-1.prod.workshops.aws/workshops/486e5ddd-b414-4e7f-9bfd-3884a89353e3/zh-CN/01introduction

## 无法成功访问的问题

/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin
/home/ec2-user/.local/bin:/home/ec2-user/bin:/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin

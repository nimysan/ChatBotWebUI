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

## EC2获取region

https://repost.aws/questions/QUnvPR1W46TS6wQWdf1sK82w/i-am-getting-401-unauthorized-when-i-hit-meta-data-api

```bash

TOKEN=`curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600"`

curl http://169.254.169.254/latest/meta-data/profile -H "X-aws-ec2-metadata-token: $TOKEN"

curl --silent http://169.254.169.254/latest/dynamic/instance-identity/document -H "X-aws-ec2-metadata-token: $TOKEN"| jq -r .region

```

## 内部pip安装的问题

> 无论是nopace, 还是pip install被killed，在将实例从t4g.micro修改到t4g.meduim后， 问题都解决了

## Amazon Bedrock model summary

```json

{
  "ResponseMetadata": {
    "RequestId": "40d9024f-8c8d-42fb-9d7a-11dfb06679d9",
    "HTTPStatusCode": 200,
    "HTTPHeaders": {
      "date": "Sat, 07 Oct 2023 06:06:39 GMT",
      "content-type": "application/json",
      "content-length": "5729",
      "connection": "keep-alive",
      "x-amzn-requestid": "40d9024f-8c8d-42fb-9d7a-11dfb06679d9"
    },
    "RetryAttempts": 0
  },
  "modelSummaries": [
    {
      "modelArn": "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-tg1-large",
      "modelId": "amazon.titan-tg1-large",
      "modelName": "Titan Text Large",
      "providerName": "Amazon",
      "inputModalities": [
        "TEXT"
      ],
      "outputModalities": [
        "TEXT"
      ],
      "responseStreamingSupported": true,
      "customizationsSupported": [
        "FINE_TUNING"
      ],
      "inferenceTypesSupported": [
        "ON_DEMAND"
      ]
    },
    {
      "modelArn": "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-e1t-medium",
      "modelId": "amazon.titan-e1t-medium",
      "modelName": "Titan Text Embeddings",
      "providerName": "Amazon",
      "inputModalities": [
        "TEXT"
      ],
      "outputModalities": [
        "EMBEDDING"
      ],
      "customizationsSupported": [],
      "inferenceTypesSupported": [
        "ON_DEMAND"
      ]
    },
    {
      "modelArn": "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-g1-text-02",
      "modelId": "amazon.titan-embed-g1-text-02",
      "modelName": "Titan Text Embeddings v2",
      "providerName": "Amazon",
      "inputModalities": [
        "TEXT"
      ],
      "outputModalities": [
        "EMBEDDING"
      ],
      "customizationsSupported": [],
      "inferenceTypesSupported": [
        "ON_DEMAND"
      ]
    },
    {
      "modelArn": "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-text-express-v1",
      "modelId": "amazon.titan-text-express-v1",
      "modelName": "Titan Text G1 - Express",
      "providerName": "Amazon",
      "inputModalities": [
        "TEXT"
      ],
      "outputModalities": [
        "TEXT"
      ],
      "responseStreamingSupported": true,
      "customizationsSupported": [],
      "inferenceTypesSupported": [
        "ON_DEMAND"
      ]
    },
    {
      "modelArn": "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v1",
      "modelId": "amazon.titan-embed-text-v1",
      "modelName": "Titan Embeddings G1 - Text",
      "providerName": "Amazon",
      "inputModalities": [
        "TEXT"
      ],
      "outputModalities": [
        "EMBEDDING"
      ],
      "responseStreamingSupported": true,
      "customizationsSupported": [],
      "inferenceTypesSupported": [
        "ON_DEMAND"
      ]
    },
    {
      "modelArn": "arn:aws:bedrock:us-east-1::foundation-model/stability.stable-diffusion-xl",
      "modelId": "stability.stable-diffusion-xl",
      "modelName": "Stable Diffusion XL",
      "providerName": "Stability AI",
      "inputModalities": [
        "TEXT",
        "IMAGE"
      ],
      "outputModalities": [
        "IMAGE"
      ],
      "customizationsSupported": [],
      "inferenceTypesSupported": [
        "ON_DEMAND"
      ]
    },
    {
      "modelArn": "arn:aws:bedrock:us-east-1::foundation-model/stability.stable-diffusion-xl-v0",
      "modelId": "stability.stable-diffusion-xl-v0",
      "modelName": "Stable Diffusion XL",
      "providerName": "Stability AI",
      "inputModalities": [
        "TEXT",
        "IMAGE"
      ],
      "outputModalities": [
        "IMAGE"
      ],
      "customizationsSupported": [],
      "inferenceTypesSupported": [
        "ON_DEMAND"
      ]
    },
    {
      "modelArn": "arn:aws:bedrock:us-east-1::foundation-model/ai21.j2-grande-instruct",
      "modelId": "ai21.j2-grande-instruct",
      "modelName": "J2 Grande Instruct",
      "providerName": "AI21 Labs",
      "inputModalities": [
        "TEXT"
      ],
      "outputModalities": [
        "TEXT"
      ],
      "responseStreamingSupported": false,
      "customizationsSupported": [],
      "inferenceTypesSupported": [
        "ON_DEMAND"
      ]
    },
    {
      "modelArn": "arn:aws:bedrock:us-east-1::foundation-model/ai21.j2-jumbo-instruct",
      "modelId": "ai21.j2-jumbo-instruct",
      "modelName": "J2 Jumbo Instruct",
      "providerName": "AI21 Labs",
      "inputModalities": [
        "TEXT"
      ],
      "outputModalities": [
        "TEXT"
      ],
      "responseStreamingSupported": false,
      "customizationsSupported": [],
      "inferenceTypesSupported": [
        "ON_DEMAND"
      ]
    },
    {
      "modelArn": "arn:aws:bedrock:us-east-1::foundation-model/ai21.j2-mid",
      "modelId": "ai21.j2-mid",
      "modelName": "Jurassic-2 Mid",
      "providerName": "AI21 Labs",
      "inputModalities": [
        "TEXT"
      ],
      "outputModalities": [
        "TEXT"
      ],
      "responseStreamingSupported": false,
      "customizationsSupported": [],
      "inferenceTypesSupported": [
        "ON_DEMAND"
      ]
    },
    {
      "modelArn": "arn:aws:bedrock:us-east-1::foundation-model/ai21.j2-mid-v1",
      "modelId": "ai21.j2-mid-v1",
      "modelName": "Jurassic-2 Mid",
      "providerName": "AI21 Labs",
      "inputModalities": [
        "TEXT"
      ],
      "outputModalities": [
        "TEXT"
      ],
      "responseStreamingSupported": false,
      "customizationsSupported": [],
      "inferenceTypesSupported": [
        "ON_DEMAND"
      ]
    },
    {
      "modelArn": "arn:aws:bedrock:us-east-1::foundation-model/ai21.j2-ultra",
      "modelId": "ai21.j2-ultra",
      "modelName": "Jurassic-2 Ultra",
      "providerName": "AI21 Labs",
      "inputModalities": [
        "TEXT"
      ],
      "outputModalities": [
        "TEXT"
      ],
      "responseStreamingSupported": false,
      "customizationsSupported": [],
      "inferenceTypesSupported": [
        "ON_DEMAND"
      ]
    },
    {
      "modelArn": "arn:aws:bedrock:us-east-1::foundation-model/ai21.j2-ultra-v1",
      "modelId": "ai21.j2-ultra-v1",
      "modelName": "Jurassic-2 Ultra",
      "providerName": "AI21 Labs",
      "inputModalities": [
        "TEXT"
      ],
      "outputModalities": [
        "TEXT"
      ],
      "responseStreamingSupported": false,
      "customizationsSupported": [],
      "inferenceTypesSupported": [
        "ON_DEMAND"
      ]
    },
    {
      "modelArn": "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-instant-v1",
      "modelId": "anthropic.claude-instant-v1",
      "modelName": "Claude Instant",
      "providerName": "Anthropic",
      "inputModalities": [
        "TEXT"
      ],
      "outputModalities": [
        "TEXT"
      ],
      "responseStreamingSupported": true,
      "customizationsSupported": [],
      "inferenceTypesSupported": [
        "ON_DEMAND"
      ]
    },
    {
      "modelArn": "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-v1",
      "modelId": "anthropic.claude-v1",
      "modelName": "Claude",
      "providerName": "Anthropic",
      "inputModalities": [
        "TEXT"
      ],
      "outputModalities": [
        "TEXT"
      ],
      "responseStreamingSupported": true,
      "customizationsSupported": [],
      "inferenceTypesSupported": [
        "ON_DEMAND"
      ]
    },
    {
      "modelArn": "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-v2",
      "modelId": "anthropic.claude-v2",
      "modelName": "Claude",
      "providerName": "Anthropic",
      "inputModalities": [
        "TEXT"
      ],
      "outputModalities": [
        "TEXT"
      ],
      "responseStreamingSupported": true,
      "customizationsSupported": [],
      "inferenceTypesSupported": [
        "ON_DEMAND"
      ]
    },
    {
      "modelArn": "arn:aws:bedrock:us-east-1::foundation-model/cohere.command-text-v14",
      "modelId": "cohere.command-text-v14",
      "modelName": "Command",
      "providerName": "Cohere",
      "inputModalities": [
        "TEXT"
      ],
      "outputModalities": [
        "TEXT"
      ],
      "responseStreamingSupported": true,
      "customizationsSupported": [],
      "inferenceTypesSupported": [
        "ON_DEMAND"
      ]
    }
  ]
}


```

## 知识入库的向量和查询时候的向量需要用一致的模型

否则可能出现以下问题

1. 维度不一样无法查询

```bash
# openaishi 1536  shibing624/text2vec-bge-large-chinese  1024 dim
sqlalchemy.exc.DataError: (psycopg2.errors.DataException) different vector dimensions 1536 and 1024
```

2. 查询不准确
   message": "The size of tensor a (589) must match the size of tensor b (512) at non-singleton dimension 1"\n}

## vector

```bash
radio.exceptions.Error: 'Failed to import, the error detail is (psycopg2.errors.UndefinedObject) type "vector" does not exist
```

### pgvector数据查看

```sql
select document, cmetadata
from langchain_pg_embedding
where collection_id = (select uuid from langchain_pg_collection where name = 'collection_name')
```

## sample model id in Amazon Bedrock

cohere.command-text-v14
anthropic.claude-v2
anthropic.claude-v1

### prompts sample

[参考](./prompts.md)
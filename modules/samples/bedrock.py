import json
import boto3

boto3_bedrock = boto3.client("bedrock")  # 列出模型用这个invoke-model要用这个。
models = boto3_bedrock.list_foundation_models()

## inference runtime
client = boto3.client('bedrock-runtime',
                      "us-west-2",
                      # endpoint_url="https://bedrock-runtime.us-east-1.amazonaws.com"

                      )  # invoke-model要用这个。

## claude-v2
modelId = "anthropic.claude-v2"
accept = "application/json"
contentType = "application/json"

body = json.dumps(
    {
        "prompt": "\n\nHuman: 可以帮我写一篇7言绝句的唐诗吗?\n\nAssistant:",
        "max_tokens_to_sample": 100,
    }
)
response = client.invoke_model(
    body=body, modelId=modelId, accept=accept, contentType=contentType

)
response_body = json.loads(response.get("body").read())
print(response_body.get("completion"))
## claude-v2 embedding

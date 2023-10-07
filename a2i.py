import boto3
import json

response = boto3.client("sts").get_caller_identity()

print(response)

bedrock = boto3.client(service_name='bedrock-runtime')

body = json.dumps({"prompt": "Translate to spanish: 'Amazon Bedrock is the easiest way to build and scale generative AI applications with base models (FMs)'.", "maxTokens": 200,
    "temperature": 0.5,"topP": 0.5})

modelId = 'ai21.j2-mid-v1'
accept = 'application/json'
contentType = 'application/json'

response = bedrock.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)

response_body = json.loads(response.get('body').read())

# text
print(response_body.get("completions")[0].get("data").get("text"))
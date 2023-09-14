import boto3
from langchain.embeddings import BedrockEmbeddings

session = boto3.Session()
client_params = {
    # "endpoint_url": "https://prod.us-west-2.frontend.bedrock.aws.dev"
    # "verbose": True
}

client = session.client("bedrock", region_name="us-west-2",
    endpoint_url="https://prod.us-west-2.frontend.bedrock.aws.dev", **client_params)

becrock = BedrockEmbeddings(
    region_name="us-west-2",
    client=client
)

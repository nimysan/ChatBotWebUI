from typing import Dict

import boto3
from langchain.embeddings import BedrockEmbeddings


# bedrock_embeddings_instance = BedrockEmbeddings(
#     credentials_profile_name="bedrock-admin", region_name="us-east-1"
# )
# BEDROCK_EMBEDDING_INSTANCE = None;


###
### embeddings.embed_documents(["This is a content of the document", "This is another document"])
###

class PrewviewStageBedrock(BedrockEmbeddings):
    def validate_environment(cls, values: Dict) -> Dict:
        """Validate that AWS credentials to and python package exists in environment."""

        # Skip creating new client if passed in constructor
        if values["client"] is not None:
            return values

        try:
            import boto3
            print(f"############profile name {values['credentials_profile_name']}")
            if values["credentials_profile_name"] is not None:
                session = boto3.Session(profile_name=values["credentials_profile_name"])
            else:
                # use default credentials
                session = boto3.Session()

            # preview
            client_params = {
                "endpoint_url": "https://prod.us-west-2.frontend.bedrock.aws.dev/"
            }
            if values["region_name"]:
                client_params["region_name"] = values["region_name"]

            values["client"] = session.client("bedrock", **client_params)

        except ImportError:
            raise ModuleNotFoundError(
                "Could not import boto3 python package. "
                "Please install it with `pip install boto3`."
            )
        except Exception as e:
            raise ValueError(
                "Could not load credentials to authenticate with AWS client. "
                "Please check that credentials in the specified "
                "profile name are valid."
            ) from e

        return values


bedrock_embeddings_instance = None


def build_bedrock_embeddings():
    global bedrock_embeddings_instance
    session = boto3.Session()
    client_params = {
        "endpoint_url": "https://prod.us-west-2.frontend.bedrock.aws.dev"
    }
    client = session.client("bedrock", **client_params)

    if bedrock_embeddings_instance is None:
        bedrock_embeddings_instance = BedrockEmbeddings(
            region_name="us-west-2",
            client=client
        )
    return bedrock_embeddings_instance


EMBEDDINGS_BEDROCK = "aws_bedrock"


def get_embeddings_by_name(name=EMBEDDINGS_BEDROCK):
    if (EMBEDDINGS_BEDROCK == name):
        return build_bedrock_embeddings();
    else:
        raise f"The embedings with {name} is not ready"

from typing import Dict

from langchain.llms import Bedrock


class PrewviewStageBedrock(Bedrock):
    def validate_environment(cls, values: Dict) -> Dict:
        """Validate that AWS credentials to and python package exists in environment."""

        # Skip creating new client if passed in constructor
        if values["client"] is not None:
            return values

        try:
            import boto3

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

import requests


def get_region_from_ec2_metadata():
    """
    TOKEN=`curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600"` \
    && curl -H "X-aws-ec2-metadata-token: $TOKEN" -v http://169.254.169.254/latest/meta-data/

    参考链接： https://docs.aws.amazon.com/zh_cn/AWSEC2/latest/UserGuide/instancedata-data-retrieval.html
    """
    session = requests.Session()
    headers = {
        'X-aws-ec2-metadata-token-ttl-seconds': '21600',
        # "Content-Type": "application/json"
    }
    token_response = session.put("http://169.254.169.254/latest/api/token", headers=headers)
    token = token_response.text

    md_headers = {
        'X-aws-ec2-metadata-token': token,
        "Content-Type": "application/json"
    }
    instance_identity_url = "http://169.254.169.254/latest/dynamic/instance-identity/document"
    r = requests.get(instance_identity_url, headers=md_headers)
    response_json = r.json()
    region = response_json.get("region")
    return region

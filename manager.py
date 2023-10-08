import gradio as gr
import langchain
import boto3

from modules.config import bot_config
from modules.config.pg_config import configure_page
from modules.doc.import_web_doc import component_import_data as import_web_page
from modules.config.bot_settings import bot_settings_page

# import pydevd_pycharm
# pydevd_pycharm.settrace('localhost', port=12345, stdoutToServer=True, stderrToServer=True)
langchain.verbose = True
with gr.Blocks() as bot_manager:
    # 创建多个选项卡
    # gr.LogoutButton()
    multi_tab_interface = gr.TabbedInterface(
        interface_list=[import_web_page, configure_page, bot_settings_page],
        tab_names=["FAQ Import", "VectorStore Settings", "Bot Settings"]
    )


def auth_manager(username, password):
    # boto_sess = boto3.Session(region_name="us-west-2")
    client = boto3.client('cognito-idp')
    cognito_config = bot_config.get_config("cognito")
    print(f"pool config is {cognito_config}")
    response = client.admin_initiate_auth(
        UserPoolId=cognito_config['poolId'],
        ClientId=cognito_config['clientId'],
        AuthFlow='ADMIN_NO_SRP_AUTH',
        AuthParameters={
            'USERNAME': username,
            'PASSWORD': password
        }
    )

    print(f"---response -- {response}")
    # return True
    # try:
    #
    # # except client.exceptions.NotAuthorizedException:
    # #     raise gr.Error("用户名或密码错误")
    #
    # except Exception as e:
    #     print(f"---exception is: {e}")
    #     # print(f"Exception as {e}")
    #     return False


bot_manager.launch(server_name="0.0.0.0", auth=auth_manager, server_port=7865, root_path="/manage")

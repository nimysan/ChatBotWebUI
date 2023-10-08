import gradio as gr
import langchain
import boto3

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
    client = boto3.client('cognito-idp')

    try:
        response = client.admin_initiate_auth(
            UserPoolId='us-east-1_a1xrQ2abR',
            ClientId='1thbob5g10mhr6alhnn6eulcq5',
            AuthFlow='ADMIN_NO_SRP_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password
            }
        )

        print(f"----- {response}")
        return True
    # except client.exceptions.NotAuthorizedException:
    #     raise gr.Error("用户名或密码错误")

    except Exception as e:
        print(f"----- {e}")
        # print(f"Exception as {e}")
        return False


bot_manager.launch(server_name="0.0.0.0", auth=auth_manager, auth_message="hey man")

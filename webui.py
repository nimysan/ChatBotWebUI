import gradio as gr

from modules.config.pg_config import configure_page
from modules.config.sm_config import sm_configure_page
from modules.doc.import_web_doc import component_import_data as import_web_page
from modules.bot.bot_page import chatbot_page

# import pydevd_pycharm
# pydevd_pycharm.settrace('localhost', port=12345, stdoutToServer=True, stderrToServer=True)

# 创建多个选项卡
multi_tab_interface = gr.TabbedInterface(
    interface_list=[chatbot_page, configure_page, import_web_page, sm_configure_page],
    tab_names=['Chat(咨询中心)', 'Settings(设置)', "FAQ Import(网页FAQ导入", "SageMaker(私有模型部署和配置)"]
)

multi_tab_interface.launch(server_name="0.0.0.0")

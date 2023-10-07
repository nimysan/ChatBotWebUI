import gradio as gr
import langchain

from modules.config.pg_config import configure_page
from modules.doc.import_web_doc import component_import_data as import_web_page
from modules.config.bot_settings import bot_settings_page

# import pydevd_pycharm
# pydevd_pycharm.settrace('localhost', port=12345, stdoutToServer=True, stderrToServer=True)
langchain.verbose = True
# 创建多个选项卡
multi_tab_interface = gr.TabbedInterface(
    interface_list=[import_web_page, configure_page, bot_settings_page],
    tab_names=["FAQ Import", "VectorStore Settings", "Bot Settings"]
)

multi_tab_interface.launch(server_name="0.0.0.0")

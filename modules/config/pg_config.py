import gradio as gr

from modules.config.bot_config import write_config
from modules.config.bot_config import get_config


def write_configuration(*args):
    return write_config("pg_config", args)


with gr.Blocks() as configure_page:
    with gr.Column() as pg_config:
        local_pg_config = get_config("pg_config") or ["localhost", "5432", "postgres", "postgres", "mysecretpassword"]
        # print(f"local_pg_config is {local_pg_config}")
        gr.Markdown("配置向量存储库")
        t_pg_host = gr.Text(label="PG Host", type="text", value=local_pg_config[0])
        t_pg_port = gr.Text(label="PG port", type="text", value=local_pg_config[1])
        t_pg_database = gr.Text(label="PG database", type="text", value=local_pg_config[2])
        t_pg_username = gr.Text(label="PG User Name", type="text", value=local_pg_config[3])
        t_pg_password = gr.Text(label="PG Password", type="password", value=local_pg_config[4])

        # print(f"insdie webui {t_pg_host}")
        btn = gr.Button("保存数据库配置")
        out = gr.Textbox()
        # dict((name, locals()[name]) for name in []z)
        btn.click(fn=write_configuration,
                  inputs=[t_pg_host, t_pg_port, t_pg_database, t_pg_username, t_pg_password],
                  outputs=out
                  )

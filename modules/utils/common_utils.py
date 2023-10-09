import os


def is_under_proxy():
    """
    确认部署模式是否在proxy后面
    :return:
    """
    return os.getenv("BOT_UNDER_PROXY", None) is not None

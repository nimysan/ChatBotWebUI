# Global Configuration Local or by database

import json

from langchain.embeddings import OpenAIEmbeddings

APP_CONFIG_KEY_PG_CONN = "pg_conn"
OPENAI_EMBEDDINGS = OpenAIEmbeddings()


# give me a function to load json file
def load_config():
    fileObject = open("config.json", "r")
    jsonContent = fileObject.read()
    config_object = json.loads(jsonContent)
    # print(f"the config is {config_object}")
    return config_object


def save_config(config_object):
    jsonString = json.dumps(config_object)
    jsonFile = open("config.json", "w")
    jsonFile.write(jsonString)
    jsonFile.close()


def get_config(key):
    return GLOBAL_CONFIG_OBJECT.get(key, None)


def get_pg_config():
    return GLOBAL_CONFIG_OBJECT.get("pg_config", None)


def get_embeddings_by_key(key):
    return OPENAI_EMBEDDINGS;  # TODO


def write_config(key, value):
    GLOBAL_CONFIG_OBJECT[key] = value
    save_config(GLOBAL_CONFIG_OBJECT)


GLOBAL_CONFIG_OBJECT = load_config()

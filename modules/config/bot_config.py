# Global Configuration Local or by database

import json

from langchain.embeddings import OpenAIEmbeddings

# from langchain.embeddings import OpenAIEmbeddings

APP_CONFIG_KEY_PG_CONN = "pg_conn"


# OPENAI_EMBEDDINGS = OpenAIEmbeddings()


# give me a function to load json file
def load_config():
    fileObject = open("config.json", "r")
    jsonContent = fileObject.read()
    config_object = json.loads(jsonContent)
    # print(f"the config is {config_object}")
    return config_object


def save_config(config_object):
    jsonString = json.dumps(config_object, indent=2)
    jsonFile = open("config.json", "w")
    jsonFile.write(jsonString)
    jsonFile.close()


def get_config(key):
    return GLOBAL_CONFIG_OBJECT.get(key, None)


def get_pg_config():
    return GLOBAL_CONFIG_OBJECT.get("pg_config", None)


def write_config(key, value):
    print(f"the key is {key} with value {value}")
    GLOBAL_CONFIG_OBJECT[key] = value
    save_config(GLOBAL_CONFIG_OBJECT)


def get_embeddings_by_key(key):
    return OpenAIEmbeddings(openai_api_key=get_config("openai_key"))


GLOBAL_CONFIG_OBJECT = load_config()

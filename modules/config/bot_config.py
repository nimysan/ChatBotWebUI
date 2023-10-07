# Global Configuration Local or by database

import json

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
    return load_config().get(key, None)


def get_pg_config():
    return load_config().get("pg_config", None)


def write_config(key, value):
    print(f"the key is {key} with value {value}")
    tmp_config = load_config()
    tmp_config[key] = value
    save_config(tmp_config)

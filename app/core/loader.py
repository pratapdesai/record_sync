import json
from app.systems.file import FileSource, FileSink
from app.core.logger import logger


def load_systems_from_config(path: str):
    with open(path) as f:
        config = json.load(f)

    system_a_conf = config["system_a"]
    system_b_conf = config["system_b"]

    from_sys = ""
    to_sys = ""
    # Dispatch based on type
    if system_a_conf["type"] == "file_source":
        from_sys = FileSource(system_a_conf["path"])
    elif system_a_conf["type"] == "sqlite_source":
        ...
    else:
        raise Exception("Unsupported System A")

    if system_b_conf["type"] == "file_sink":
        to_sys = FileSink(system_b_conf["path"])
    elif system_b_conf["type"] == "salesforce":
        ...
    else:
        raise Exception("Unsupported System B")

    return from_sys, to_sys

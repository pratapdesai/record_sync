import json, inspect
import configparser
from app.systems.sqlite import SQLiteSource
from app.systems.postgres import PostgresSource
from app.systems.file import FileSource, FileSink
from app.core.logger import logger
from app.crms.registry import crm_registry

config = configparser.ConfigParser()
config.read("config.ini")


def load_systems_from_config(path: str):
    with open(path) as f:
        json_config = json.load(f)

    system_a_conf = json_config["system_a"]
    system_b_conf = json_config["system_b"]

    # ---------- SYSTEM A ----------
    a_type = system_a_conf["type"]
    if a_type == "sqlite_source":
        from_sys = SQLiteSource(
            db_path=system_a_conf["db_path"],
            table_name=system_a_conf["table"]
        )

    elif a_type == "postgres_source":
        source_key = system_a_conf["source_key"]
        section = f"sources.{source_key}"
        if section not in config:
            raise Exception(f"Missing config for {section} in config.ini")

        dsn = config[section]["dsn"]
        from_sys = PostgresSource(dsn=dsn, table=system_a_conf["table"])

    elif a_type == "file_source":
        from_sys = FileSource(system_a_conf["path"])

    else:
        raise Exception(f"Unsupported system A type: {a_type}")

    # --------- SYSTEM B (sink) ---------
    b_type = system_b_conf["type"]
    if b_type == "file_sink":
        to_sys = FileSink(system_b_conf["path"])

    elif b_type in crm_registry:
        crm_key = system_b_conf["crm_key"]
        section = f"crms.{crm_key}"

        if section not in config:
            raise Exception(f"Missing CRM config: {section}")

        creds = config[section]
        CRMClass = crm_registry[b_type]

        # Validate keys
        schema = CRMClass.config_schema()
        missing = [key for key in schema if key not in creds]
        if missing:
            raise Exception(f"Missing keys in config.ini [{section}]: {missing}")

        # Pass only expected fields (optional)
        # filtered_creds = {k: creds[k] for k in schema}
        sig = inspect.signature(CRMClass.__init__)
        param_names = list(sig.parameters.keys())

        # Case 1: expects a 'config' dict (recommended)
        if 'config' in param_names:
            to_sys = CRMClass(config=creds)

        # Case 2: expects individual fields (fallback)
        else:
            allowed_args = set(param_names) - {"self"}
            filtered_creds = {k: v for k, v in creds.items() if k in allowed_args}
            to_sys = CRMClass(**filtered_creds)

        # # to_sys = CRMClass(**creds)
        # to_sys = CRMClass(**filtered_creds)

    else:
        raise Exception(f"Unsupported sink type: {b_type}")

    logger.info(f"Loaded System A ({a_type}) and System B ({b_type})")
    return from_sys, to_sys

    # elif b_type == "salesforce":
    #     crm_key = system_b_conf["crm_key"]
    #     section = f"crms.{crm_key}"
    #     if section not in config:
    #         raise Exception(f"Missing CRM config: {section}")
    #
    #     creds = config[section]
    #     to_sys = SalesforceCRM({
    #         "client_id": creds["client_id"],
    #         "client_secret": creds["client_secret"],
    #         "auth_url": creds["auth_url"],
    #         "api_url": creds["api_url"],
    #         "private_key": creds["private_key"]
    #     }
    #     )
    #
    # elif b_type == "outreach":
    #     crm_key = system_b_conf["crm_key"]
    #     section = f"crms.{crm_key}"
    #     if section not in config:
    #         raise Exception(f"Missing CRM config: {section}")
    #
    #     creds = config[section]
    #     to_sys = OutreachCRM(
    #         {
    #             "client_id": creds["client_id"],
    #             "client_secret": creds["client_secret"],
    #             "token_url": creds["token_url"],
    #             "api_url": creds["api_url"],
    #         }
    #     )

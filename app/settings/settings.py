from dynaconf import Dynaconf


class CustomerSettings:
    settings = Dynaconf(
        settings_files=['customer_settings.toml'],
    )

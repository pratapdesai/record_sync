import configparser
from threading import Lock

class ConfigManager:
    _instance = None
    _lock = Lock()

    def __init__(self, config_file="config.ini"):
        self.config_file = config_file
        self.parser = configparser.ConfigParser()
        self.parser.read(self.config_file)

    @classmethod
    def get_instance(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = ConfigManager()
            return cls._instance

    def get(self, section, key, fallback=None):
        return self.parser.get(section, key, fallback=fallback)

    def override(self, section, key, value):
        if not self.parser.has_section(section):
            self.parser.add_section(section)
        self.parser.set(section, key, value)
        with open(self.config_file, "w") as f:
            self.parser.write(f)


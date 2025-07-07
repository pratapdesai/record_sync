from app.core.config import ConfigManager
from app.models.config import ConfigOverride
from app.core.logger import logger

class ConfigService:
    def __init__(self):
        self.config = ConfigManager.get_instance()

    def override_crm_config(self, payload: ConfigOverride):
        logger.info(f"Overriding config for {payload.crm}")
        self.config.override(payload.crm, "batch_size", str(payload.batch_size))
        self.config.override(payload.crm, "flush_interval", str(payload.flush_interval))
        self.config.override(payload.crm, "rate_limit_per_minute", str(payload.rate_limit_per_minute))

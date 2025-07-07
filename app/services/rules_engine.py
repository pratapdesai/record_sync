import json
from app.core.logger import logger
from threading import Lock

class RulesEngine:
    def __init__(self):
        # load initial rules from a local file or hardcoded
        try:
            with open("rules.json", "r") as f:
                self.rules = json.load(f)
        except Exception:
            logger.warning("No local rules.json found, using defaults.")
            self.rules = {
                "salesforce": {
                    "required_fields": ["email"],
                    "disallow_if": {"do_not_sync": True}
                }
            }
        self.lock = Lock()

    def should_sync(self, crm: str, record: dict) -> bool:
        with self.lock:
            rules = self.rules.get(crm)
        if not rules:
            return True  # no rules, allow by default

        data = record.get("data", {})

        # required fields
        for field in rules.get("required_fields", []):
            if field not in data or not data[field]:
                return False

        # disallow if
        for field, value in rules.get("disallow_if", {}).items():
            if data.get(field) == value:
                return False

        return True

    def update_rules(self, new_rules: dict):
        if not isinstance(new_rules, dict):
            raise ValueError("Rules must be a dictionary")
        with self.lock:
            self.rules = new_rules
        # you could also dump to file:
        with open("rules.json", "w") as f:
            json.dump(new_rules, f, indent=2)
        logger.info("Rules updated and persisted locally.")

import json
from app.core.logger import logger
from threading import Lock


class RulesEngine:
    def __init__(self, rules_path="rules.json"):
        # load initial rules from a local file or hardcoded
        try:
            with open(rules_path, "r") as f:
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

    def match(self, record: dict) -> bool:
        filters = self.rules.get("filters", {})
        for key, expected in filters.items():
            if record.get(key) != expected:
                return False
        return True

    def transform(self, record: dict) -> dict:
        mappings = self.rules.get("mappings", {})
        if not mappings:
            logger.warning(f"[RulesEngine] No mappings configured!")
        transformed = {
            to_key: record[from_key]
            for from_key, to_key in mappings.items()
            if from_key in record
        }
        if not transformed:
            logger.warning(f"[RulesEngine] No fields mapped for record: {record}")
        return transformed

    def update_rules(self, new_rules: dict):
        if not isinstance(new_rules, dict):
            raise ValueError("Rules must be a dictionary")
        with self.lock:
            self.rules = new_rules
        with open("rules.json", "w") as f:
            json.dump(new_rules, f, indent=2)
        logger.info("Rules updated and persisted locally.")

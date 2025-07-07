# This can be used when rules needs to be imported from S3
"""

s3://my-config-bucket/rules.json

{
  "salesforce": {
    "required_fields": ["email"],
    "disallow_if": {"do_not_sync": true}
  },
  "outreach": {
    "required_fields": ["email", "first_name"],
    "disallow_if": {"status": "archived"}
  }
}


"""
import boto3
import json
from app.core.logger import logger

class RulesEngineS3:
    def __init__(self, bucket_name="my-config-bucket", key="rules.json"):
        self.s3 = boto3.client("s3")
        self.bucket = bucket_name
        self.key = key
        self.rules = {}
        self.load_rules()

    def load_rules(self):
        try:
            logger.info(f"Loading rules from S3://{self.bucket}/{self.key}")
            response = self.s3.get_object(Bucket=self.bucket, Key=self.key)
            content = response["Body"].read()
            self.rules = json.loads(content)
            logger.info("Rules successfully loaded from S3.")
        except Exception as e:
            logger.error(f"Error loading rules from S3, fallback to defaults: {e}")
            self.rules = {
                "salesforce": {
                    "required_fields": ["email"],
                    "disallow_if": {"do_not_sync": True}
                }
            }

    def should_sync(self, crm: str, record: dict) -> bool:
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
        """
        Overwrites rules in S3 and reloads from S3
        """
        # validate the new_rules is a dict with expected keys
        if not isinstance(new_rules, dict):
            raise ValueError("Rules must be a dictionary")

        # write to s3
        try:
            self.s3.put_object(
                Bucket=self.bucket,
                Key=self.key,
                Body=json.dumps(new_rules),
                ContentType="application/json"
            )
            logger.info(f"New rules pushed to S3://{self.bucket}/{self.key}")
            # reload rules
            self.load_rules()
        except Exception as e:
            logger.error(f"Failed to update rules: {e}")
            raise e
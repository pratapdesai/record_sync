from .base import BaseCRM
from app.core.logger import logger
from app.utils.circuit_breaker import CircuitBreaker


class SalesforceCRM(BaseCRM):
    def __init__(self, config):
        self.config = config
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60
        )
        self.secret = "salesforce_secret"

    def identify(self) -> str:
        return "salesforce"

    def transform(self, data: dict) -> dict:
        # simple passthrough for now
        crm_data = data.get("data", {})
        return {
            "FirstName": crm_data.get("first_name"),
            "LastName": crm_data.get("last_name"),
            "Email": crm_data.get("email"),
            "AccountId": crm_data.get("account_id")
        }

    async def push(self, data: dict):
        if not self.circuit_breaker.allow_request():
            logger.warning("Salesforce circuit breaker is OPEN, skipping push")
            raise Exception("Salesforce circuit breaker is OPEN")
        try:
            # mock JWT token
            token = self._get_jwt_token()
            logger.info(f"Sending to Salesforce with JWT: {token}, data: {data}")
            # simulate push with a log
            # simulate external API call
            # await actual HTTP call in real
            self.circuit_breaker.record_success()
        except Exception as e:
            logger.error(f"Push to Salesforce failed: {e}")
            self.circuit_breaker.record_failure()
            raise

    async def fetch_recent_changes(self, since_timestamp):
        """
        Use SOQL or a dummy pull to get records modified after since_timestamp
        """
        logger.info(f"Fetching Salesforce changes since {since_timestamp.isoformat()}")

        # for now, a mocked record:
        return [
            {
                "operation": "update",
                "record_id": "rec12345",
                "data": {
                    "first_name": "PolledFirst",
                    "email": "poll@example.com",
                    "account_id": "ACC12345"
                },
                "crm": "salesforce"
            }
        ]

        # later, replace with:
        # soql = f"SELECT Id, FirstName, LastName, Email FROM Contact WHERE LastModifiedDate > {since_timestamp.isoformat()}"
        # response = await httpx call with soql

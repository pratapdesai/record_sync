from .base import BaseCRM
from app.core.logger import logger
from app.utils.circuit_breaker import CircuitBreaker
from app.crms.registry import register_crm
import httpx
from typing import Dict
from app.services.status import status_tracker
from datetime import datetime
from app.utils.rate_limiter import SlidingWindowRateLimiter
from app.core.constants import DEFAULT_MAX_REQUESTS, DEFAULT_WINDOW_SIZE

rate_limiter = SlidingWindowRateLimiter()


@register_crm("salesforce")
class SalesforceCRM(BaseCRM):
    mock_store = []  # fake in-memory DB

    def __init__(self, config):
        super().__init__(config)
        self.config = config
        SlidingWindowRateLimiter.max_requests = DEFAULT_MAX_REQUESTS
        SlidingWindowRateLimiter.window = DEFAULT_WINDOW_SIZE
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60
        )
        self.secret = "salesforce_secret"

    @classmethod
    def config_schema(cls):
        return {
            "client_id": "OAuth client ID",
            "client_secret": "OAuth client secret",
            "auth_url": "Salesforce token endpoint URL",
            "api_url": "Salesforce API base URL",
            "private_key": "Private key used for JWT"
        }

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

    # push mock
    async def push(self, data: dict):
        if not rate_limiter.allow("salesforce"):
            logger.warning(f"[RateLimiter] CRM salesforce rate limit exceeded. Skipping or delaying push.")
            # Optionally retry or delay
            return
        else:
            logger.info("Salesforce Rate Limiting Not breached")
        SalesforceCRM.mock_store.append(data)
        status_tracker.update_stat("last_sync_success", datetime.utcnow().isoformat())
        status_tracker.increment("total_synced")
        logger.info(f"[Mock Salesforce] Record pushed: {data}")

    # pull mock
    async def pull(self):
        logger.info("[Mock Salesforce] Pulling mock data...")
        return SalesforceCRM.mock_store.copy()

    async def push_actual(self, data: dict):
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
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }

            url = "https://fake.salesforce.com/sobjects/Account"

            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=data, headers=headers)
                response.raise_for_status()  # This raises HTTPStatusError on 500

            status_tracker.update_stat("last_sync_success", datetime.utcnow().isoformat())
            status_tracker.increment("total_synced")

            self.circuit_breaker.record_success()
        except Exception as e:
            logger.error(f"Push to Salesforce failed: {e}")
            self.circuit_breaker.record_failure()
            raise

    async def write_record(self, record: Dict, allow_duplicates: bool = False):

        if not allow_duplicates:
            record_ids = {r.get("record_id") for r in SalesforceCRM.mock_store if "record_id" in r}
            if record["record_id"] in record_ids:
                logger.info(f"[Dedup] Skipping already synced record {record['record_id']}")
                return

        SalesforceCRM.mock_store.append(record)
        status_tracker.update_stat("last_sync_success", datetime.utcnow().isoformat())
        status_tracker.increment("total_synced")

        logger.info(f"Wrote record {record['record_id']} to salesforce")

    async def fetch_recent_changes(self, since_timestamp):
        """
        Use SOQL or a dummy pull to get records modified after since_timestamp
        """
        logger.info(f"Fetching Salesforce changes since {since_timestamp.isoformat()}")

        # for now, a mocked record:
        return [
            {
                "operation": "update",
                "record_id": "rec_salesforce_123",
                "data": {
                    "first_name": "PolledFirst",
                    "email": "poll@sf.com",
                    "account_id": "ACC-SF-1"
                },
                "crm": "salesforce"
            }
        ]

        # later, replace with:
        # soql = f"SELECT Id, FirstName, LastName, Email FROM Contact WHERE LastModifiedDate > {since_timestamp.isoformat()}"
        # response = await httpx call with soql

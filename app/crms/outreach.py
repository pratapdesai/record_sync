from app.crms.base import BaseCRM
from app.utils.circuit_breaker import CircuitBreaker
from app.core.logger import logger
import httpx


class OutreachCRM(BaseCRM):
    def __init__(self, config):
        self.config = config
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60
        )

    def identify(self) -> str:
        return "outreach"

    def transform(self, data: dict) -> dict:
        crm_data = data.get("data", {})
        transformed = {
            "firstName": crm_data.get("first_name"),
            "lastName": crm_data.get("last_name"),
            "emails": [
                {
                    "type": "work",
                    "value": crm_data.get("email")
                }
            ],
            "externalId": crm_data.get("account_id"),
        }
        # if rules indicate we allow duplicates:
        if crm_data.get("allow_duplicate"):
            transformed["allowDuplicate"] = True
        return transformed

    async def push(self, data: dict):
        if not self.circuit_breaker.allow_request():
            logger.warning("Outreach circuit breaker is OPEN, skipping push")
            raise Exception("Outreach circuit breaker is OPEN")

        try:
            token = self._get_jwt_token()
            logger.info(f"[MOCK] Pushing to Outreach with JWT {token}: {data}")
            self.circuit_breaker.record_success()
        except Exception as e:
            logger.error(f"Mock Outreach push failed: {e}")
            self.circuit_breaker.record_failure()
            raise

    # ACTUAL PUSH TO OUTREACH
    # async def push(self, data: dict):
    #     if not self.circuit_breaker.allow_request():
    #         logger.warning("Outreach circuit breaker is OPEN, skipping push")
    #         raise Exception("Outreach circuit breaker is OPEN")
    #
    #     try:
    #         token = self._get_jwt_token()
    #         url = "https://api.outreach.io/api/v2/prospects"
    #         headers = {
    #             "Authorization": f"Bearer {token}",
    #             "Content-Type": "application/json"
    #         }
    #         async with httpx.AsyncClient(timeout=10) as client:
    #             response = await client.post(url, headers=headers, json=data)
    #
    #         if response.status_code in [200, 201]:
    #             logger.info(f"Successfully synced record to Outreach: {response.status_code}")
    #             self.circuit_breaker.record_success()
    #         else:
    #             logger.error(f"Outreach error {response.status_code}: {response.text}")
    #             self.circuit_breaker.record_failure()
    #             raise Exception(f"Outreach returned {response.status_code}")
    #     except Exception as e:
    #         logger.error(f"Push to Outreach failed: {e}")
    #         self.circuit_breaker.record_failure()
    #         raise

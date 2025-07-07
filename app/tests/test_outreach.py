import pytest
import respx
import httpx
from app.crms.outreach import OutreachCRM

@pytest.mark.asyncio
@respx.mock
async def test_outreach_push_success():
    respx.post("https://api.outreach.io/api/v2/prospects").mock(
        return_value=httpx.Response(201, json={"data": {"id": "001DEF"}})
    )

    crm = OutreachCRM(config={})
    data = {
        "firstName": "Jane",
        "lastName": "Smith",
        "emails": [{"type": "work", "value": "jane@example.com"}],
        "externalId": "ACC456"
    }
    await crm.push(data)

@pytest.mark.asyncio
@respx.mock
async def test_outreach_push_failure():
    respx.post("https://api.outreach.io/api/v2/prospects").mock(
        return_value=httpx.Response(500, json={"error": "server error"})
    )

    crm = OutreachCRM(config={})
    data = {
        "firstName": "Jane",
        "lastName": "Smith",
        "emails": [{"type": "work", "value": "jane@example.com"}],
        "externalId": "ACC456"
    }
    with pytest.raises(Exception):
        await crm.push(data)

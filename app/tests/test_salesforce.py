import pytest
import respx
import httpx
import asyncio
from app.crms.salesforce import SalesforceCRM

@pytest.mark.asyncio
@respx.mock
async def test_salesforce_push_success():
    respx.post("https://fake.salesforce.com/sobjects/Account").mock(
        return_value=httpx.Response(201, json={"id": "001ABC"})
    )

    crm = SalesforceCRM(config={})
    data = {
        "FirstName": "John",
        "LastName": "Doe",
        "Email": "john@example.com",
        "AccountId": "ACC123"
    }
    await crm.push_actual(data)

@pytest.mark.asyncio
@respx.mock
async def test_salesforce_push_failure():
    respx.post("https://fake.salesforce.com/sobjects/Account").mock(
        return_value=httpx.Response(500, json={"error": "server error"})
    )

    crm = SalesforceCRM(config={})
    data = {
        "FirstName": "John",
        "LastName": "Doe",
        "Email": "john@example.com",
        "AccountId": "ACC123"
    }

    # with pytest.raises(Exception, match="Push failed"):
    #     await crm.push(data)

    with pytest.raises(httpx.HTTPStatusError):
        await crm.push_actual(data)

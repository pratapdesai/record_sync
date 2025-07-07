import pytest
import respx
import httpx
import asyncio
from app.crms.salesforce import SalesforceCRM

@pytest.mark.asyncio
@respx.mock
async def test_salesforce_push_success():
    respx.post("https://my.salesforce.com/sobjects/Account").mock(
        return_value=httpx.Response(201, json={"id": "001ABC"})
    )

    crm = SalesforceCRM(config={})
    data = {
        "FirstName": "John",
        "LastName": "Doe",
        "Email": "john@example.com",
        "AccountId": "ACC123"
    }
    await crm.push(data)

@pytest.mark.asyncio
@respx.mock
async def test_salesforce_push_failure():
    respx.post("https://my.salesforce.com/sobjects/Account").mock(
        return_value=httpx.Response(500, json={"error": "server error"})
    )

    crm = SalesforceCRM(config={})
    data = {
        "FirstName": "John",
        "LastName": "Doe",
        "Email": "john@example.com",
        "AccountId": "ACC123"
    }

    with pytest.raises(Exception):
        await crm.push(data)

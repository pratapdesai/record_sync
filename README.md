# 📦 Record Sync Service

- Bi-directional, event-driven microservice to synchronize CRUD record changes between an internal system (System A) and external CRMs (System B, e.g., Salesforce, Outreach). Designed for high scale, dynamic configuration, rules-based decisioning, and extensibility to new CRMs.


- A high-performance, extensible, production-grade Record Synchronization Service that facilitates data transfer and sync across heterogeneous systems such as CRMs (Salesforce, Outreach), databases (PostgreSQL, SQLite), and flat file storage. Supports real-time and batch sync with rule-based transformation, conflict resolution, retry, deduplication, and observability.
---
## Design Document

Design document can be found out in [DESIGN.md](DESIGN.md)


## 🚀 Features

✅ Bidirectional Sync (System A ↔ System B) 
✅ Extensible CRM support (strategy pattern)  
✅ Dynamic rules engine to determine CRUD triggers  
✅ Rate-limiting with a sliding window algorithm  
✅ Configurable flush intervals and batch sizes  
✅ Reliable queue-based design (using Redis or mock)  
✅ Retry/circuit-breaker mechanism  
✅ Manual retry capability  
✅ Idempotency by record ID  
✅ Status tracking with queryable endpoints  
✅ Dynamic rules editing (no redeploy required)  
✅ Strong input/output validation with Pydantic  
✅ Structured JSON logs (Loguru) for observability  
✅ Dockerized for cloud deployment  
✅ Designed for AWS (ECS/Fargate, ALB, Redis, CloudWatch)

---

## 📄 Endpoints

### ⚙️ Sync APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /v1/sync/ | Accept sync events (`operation` in body: create, read, update, delete) |
| POST | /v1/sync/retry/{record_id} | Manually retry a failed sync |
| GET | /v1/sync/status/{record_id} | Query sync status |
| POST | /v1/sync/config-override | Dynamically override batch/flush/rate-limit |
| POST | /v1/sync/rules | Update rules engine dynamically |

### ⚙️ CRM APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /v1/crms/available| List all registered CRMs |
| GET | /v1/crms/{crm}/schema | Schema requirements for CRM config |


### ⚙️ Mock APIs (for testing CRMs)

| Method | Endpoint                      | Description |
|--------|-------------------------------|-------------|
| POST   | /v1/crms/mock/salesforce/push | Push fake data to mock Salesforce |
| POST   | /v1/crms/mock/outreach/push   | Push fake data to mock Outreach |

### Sample Payloads

- Mock Salesforce Push
    ```
    curl -X POST http://localhost:8000/v1/crms/mock/salesforce/push \
      -H "Content-Type: application/json" \
      -d '{
            "record_id": 303,
            "full_name": "Mock303 User",
            "email_address": "mock@sf.com"
          }'
    ```
- Mock Outreach Push
  ```
  curl -X POST http://localhost:8000/v1/crms/mock/outreach/push \
    -H "Content-Type: application/json" \
    -d '{
          "record_id": 301,
          "full_name": "Mock User",
          "email_address": "mock@sf.com"
        }'
  ```
- GET Available CRMS
    ```
    curl -X GET http://localhost:8000/v1/crms/available
    ```
- GET Current Rules Config
  
    ```
    curl -X GET http://localhost:8000/v1/sync/rules
    ```
- PUSH/POST New Rules
  
  ```
  curl -X POST http://localhost:8000/v1/sync/rules \
  -H "Content-Type: application/json" \
  -d '{
      "filters": {},
      "mappings": {
         "record_id": "record_id",
         "full_name": "name",
         "email_address": "email"
      }
  }'
  ```
- GET the status of the sync

  ```
  curl -X GET http://localhost:8000/v1/sync/status
  ```


## Swagger Docs

Swagger docs: http://localhost:8000/docs




## 📦 Running locally

  ### How to Run
  ```
  make run
  ```
  ### How to Test

  ```
  make test
  ```
  ### How to Build Docker
  ```
  docker build -t record-sync .
  docker run -p 8000:8000 record-sync
  ```

## 🚀 🚀 What Happens When You Run the Service
#### By default, the Record Sync Service launches an automated bi-directional synchronization between:

- System A → SQLite database (users table)

- System B → Salesforce CRM (mocked or real, based on config)

#### 🔄 What Exactly Starts?

- Pollers are initialized on both sides:
  - One polls the SQLite DB for new/updated records. 
  - One polls the Salesforce CRM for new/updated records.

- Records are:
  - Transformed based on rules.json 
  - Enqueued for syncing 
  - Flushed in controlled batches using the Queue Manager

- Sync is processed via:
  - Retry Manager for failed pushes 
  - Rate Limiter to throttle outbound API calls 
  - Circuit Breaker to isolate failing systems

- Observability is enabled:
  - All actions are logged as structured JSON 
  - Sync status (queued, synced, failed) is tracked per record 
  - All logs currently get stored to /logs/record_sync.log

System can be monitored using the /v1/status API or by tailing the logs.

## What are tested till now ?
### Refer [main.py](app/main.py)

- SQLite to File Bidirectional Sync
- SQLite to Salesforce Bidirectional Sync
- File to File Bidirectional Sync

## For Triggering Customer Based Bidirectional Sync

- Add the Customer specific CRM values in [customer_settings.toml](customer_settings.toml)
- If there is nothing for the customer, default values are considered.
- Below is the process to run the SQLITE to Salesforce Bidirectional Sync.
  - > make run
  - Trigger the SQLITE to Salesforce Bidirectional Sync
  ```
  curl -X POST 'http://localhost:8000/v1/sync/sqlite-to-salesforce?customer_id=customer1'
  curl -X POST 'http://localhost:8000/v1/sync/sqlite-to-salesforce?customer_id=surya'
  ```
- How to Insert data into sqlite
  - Independent [insert_demo_Data.py](app/scripts/insert_demo_data.py) script writes dummy data to data/demo.sqlite
  - Please run the above script using below command
    - ``` python3 insert_demo_data.py```
    

- How to Insert data in Salesforce
  - Mock Salesforce Push
    ```
    curl -X POST http://localhost:8000/v1/crms/mock/salesforce/push \
      -H "Content-Type: application/json" \
      -d '{
            "record_id": 303,
            "full_name": "Mock303 User",
            "email_address": "mock@sf.com"
            "status" : "active"
          }'
    ```
#### Note  
  - Poller or Reading data from CRM is also accounted for RateLimiting 
  - Push or Writing data to CRM is also accounted for RateLimiting
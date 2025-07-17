# 📦 Record Sync Service

Bi-directional, event-driven microservice to synchronize CRUD record changes between an internal system (System A) and external CRMs (System B, e.g., Salesforce, Outreach). Designed for high scale, dynamic configuration, rules-based decisioning, and extensibility to new CRMs.
A high-performance, extensible, production-grade Record Synchronization Service that facilitates data transfer and sync across heterogeneous systems such as CRMs (Salesforce, Outreach), databases (PostgreSQL, SQLite), and flat file storage. Supports real-time and batch sync with rule-based transformation, conflict resolution, retry, deduplication, and observability.
---

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
- 


## Swagger Docs

Swagger docs: http://localhost:8000/docs


---

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


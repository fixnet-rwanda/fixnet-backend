# FixNet Error Handling & Logging Strategy

- **Document Version**: 1.0
- **Status**: Draft — Pending Engineering Sign-off
- **Scope**: Customer App · Technician App · FixNet Admin Portal · Backend API · Background Jobs

---

## 1. Error Classification & Standard Response Format

All API errors return consistent JSON structures:

```json
{
  "error_code": "RESOURCE_NOT_FOUND",
  "message": "The requested resource could not be found.",
  "request_id": "req_88a91c0b-4f62-4361-9c88-123456789abc",
  "details": {}
}
```

### Key Error Codes:
- `VALIDATION_ERROR`: Input validation failed (HTTP 400).
- `AUTHENTICATION_FAILED`: Invalid token, wrong password, or invalid OTP (HTTP 401).
- `PERMISSION_DENIED`: RBAC rule violation (HTTP 403).
- `RESOURCE_NOT_FOUND`: Target entity not found (HTTP 404).
- `RATE_LIMIT_EXCEEDED`: Rate limit breached (HTTP 429).
- `BUSINESS_RULE_VIOLATION`: Domain rule prevented operation (HTTP 422).
- `INTERNAL_SERVER_ERROR`: Unhandled exception (HTTP 500).

---

## 2. Correlation & Tracing

- **`X-Request-ID`**: Every incoming HTTP request must receive or generate a unique UUID `request_id`.
- The `request_id` must be:
  1. Attached to the response header `X-Request-ID`.
  2. Included in all log statements.
  3. Propagated to Celery background tasks and outbound integration calls.

---

## 3. Logging Levels & Rules

| Level | Usage | Production Destination |
| :--- | :--- | :--- |
| **DEBUG** | Diagnostic detail during development | Staging/Dev only |
| **INFO** | Normal business operations (e.g. status transitions) | Central log store |
| **WARNING** | Recoverable issues (e.g. SMS provider failover) | Central log store + dashboard |
| **ERROR** | Operation failed for single user/request | Sent to Sentry (grouped by fingerprint) |
| **CRITICAL** | System-wide failure (DB down, queue stalled) | Sentry + On-call engineer page |

### PII & Sensitive Data Redaction:
Never log:
- OTP codes or passwords
- Payment tokens / PINs / credit card numbers
- Raw national ID numbers or unmasked phone numbers in error strings

---

## 4. Retries & Resilience

- **SMS / OTP**: Up to 3 attempts with exponential backoff; automatic failover from Africa's Talking to Twilio.
- **Push Notifications (FCM)**: Best-effort, single retry.
- **Booking Payments**: Non-automatic retry (user triggered to avoid double charge).
- **Webhooks**: Idempotent processing by `transaction_id`.

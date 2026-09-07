# FIXNET Authentication & Authorization Design

**Technical Design Document — Identity, Access Control & Security Policy**
- **Document Version**: 1.0
- **Status**: Draft for Review
- **Related Document**: [API Design Specification](API_DESIGN_SPECIFICATION.md)

---

## 1. Overview

FIXNET supports two distinct user populations:
1. **Customers & Technicians**: Access via mobile app, passwordless SMS OTP.
2. **Administrative Staff** (`support_agent`, `finance_admin`, `system_admin`): Access via browser-based Admin Portal, Email + Password + TOTP MFA.

---

## 2. Authentication Flows

### 2.1 Mobile OTP Flow (Customers & Technicians)
- **Step 1 — Request OTP**: E.164 phone number (e.g. `+25078XXXXXXX`). Generates 6-digit cryptographic numeric code valid for 5 minutes. Stored hashed in Redis with rate-limit counter. Dispatched via Africa's Talking / Twilio.
- **Step 2 — Verify OTP**: User submits phone number + 6-digit code. Validated against hashed code in Redis with attempt count check.
- **Step 3 — Token Issuance**: Returns short-lived JWT Access Token (15 mins) and long-lived Refresh Token (30 days).

### 2.2 Admin Portal Login Flow
- **Step 1 — Credentials Check**: Admin enters email + password. Password verified with `bcrypt` (work factor $\ge 12$).
- **Step 2 — MFA Challenge**: Interim `mfa_token` issued (valid for 3 minutes).
- **Step 3 — TOTP Verification**: 6-digit TOTP code submitted. On success, standard JWT Access Token (15 mins) and Refresh Token (30 days) are issued.

---

## 3. Token Architecture

### 3.1 Access Token
- **Format**: Bearer JWT passed in `Authorization: Bearer <token>`
- **Lifespan**: 15 minutes
- **Issuer (`iss`)**: `fixnet-auth-service`
- **Payload Schema**:
  ```json
  {
    "sub": "usr_9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
    "role": "technician",
    "phone_number": "+250788123456",
    "language": "rw",
    "iat": 1787400000,
    "exp": 1787400900,
    "iss": "fixnet-auth-service"
  }
  ```

### 3.2 Refresh Token
- **Format**: Cryptographically random opaque string
- **Lifespan**: 30 days
- **Client Storage**: `SecureStorage` (Flutter mobile app); `HttpOnly` Cookie (React Admin Portal).
- **Rotation Policy**: Every call to `/auth/token/refresh` invalidates the old refresh token and issues a new access/refresh pair.

---

## 4. Security Policies & Middleware Rules

- **Rate Limiting (REQ-SEC-005)**: OTP request and verify endpoints limited to 10 requests per minute per IP and phone number independently.
- **Brute-Force Lockout (REQ-ACC-003)**: 5 incorrect OTP attempts within 15 minutes triggers a 30-minute lockout on that phone number. Device metadata logged.
- **Presigned URLs (REQ-SEC-002)**: ID documents in private S3 buckets, accessed only via temporary pre-signed URLs (maximum 15 minutes expiration).
- **Data Encryption (REQ-SEC-001)**: TLS 1.3 in transit; AES-256 at rest.

---

## 5. Role-Based Access Control (RBAC) Matrix

| Endpoint Group | Customer | Technician | Support Agent | Finance Admin | System Admin |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Customer Discovery & Chat** | Full | None | Read-only | None | Read-only |
| **Quotes & Service Execution** | Accept | Create | Read-only | None | Read-only |
| **Deposit Payments** | Full | None | Read-only | Read-only | Read-only |
| **Technician Verification & Content Moderation** | None | None | Full | None | Full |
| **Disputes & Refunds** | None | None | Full | Full | Full |
| **Global Pricing & Config** | None | None | None | None | Full |
| **Financial CSV Reports** | None | None | None | Full | Full |
| **User Suspension & Audits** | None | None | None | None | Full |

### Notable Authorization Rules:
1. **Financial Separation of Duties**: `finance_admin` can process refunds and generate financial reports but cannot moderate content or verify technicians.
2. **Support Agent Scope**: `support_agent` can moderate content and resolve disputes/refunds with read-only access to customer chat; no access to global pricing.
3. **System Admin Scope**: Full administrative access across all domains.
4. **Customer / Technician Isolation**: Cannot access administrative surfaces.

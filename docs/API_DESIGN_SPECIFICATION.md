# FIXNET API Design Specification

**Detailed Endpoint Reference — v1**
- **Document Version**: 1.0
- **Status**: Draft for Review
- **Base Path**: `/v1`
- **Related Document**: [Authentication & Authorization Design](AUTHENTICATION_AUTHORIZATION_DESIGN.md)

---

## 1. Overview & Conventions

All endpoints under `/v1` follow standard RESTful conventions:
- **Monetary Values**: Represented as integers in the smallest currency unit (RWF or cents) to avoid floating-point errors (REQ-PAY-002).
- **Authentication**: All authenticated endpoints require `Authorization: Bearer <access_token>`.
- **Timestamps**: ISO 8601 UTC strings (e.g. `2026-08-23T10:15:00Z`).
- **Roles**: `customer`, `technician`, `support_agent`, `finance_admin`, `system_admin`.

---

## 2. Authentication & User Management — `/v1/auth`, `/v1/users`

### 1. Request SMS OTP
- **Method & Path**: `POST /v1/auth/otp/request`
- **Access**: Public (rate limited: 10 req/min per IP / phone number)
- **Request Body**:
  ```json
  {
    "phone_number": "+250788123456",
    "channel": "sms"
  }
  ```
- **Success Response (200 OK)**:
  ```json
  {
    "status": "success",
    "message": "OTP sent successfully via SMS",
    "expires_in_seconds": 300
  }
  ```
- **Error Response (429 Too Many Requests)**:
  ```json
  {
    "error_code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many attempts. Locked out for 30 minutes."
  }
  ```

### 2. Verify SMS OTP & Login
- **Method & Path**: `POST /v1/auth/otp/verify`
- **Access**: Public
- **Request Body**:
  ```json
  {
    "phone_number": "+250788123456",
    "code": "582910"
  }
  ```
- **Success Response (200 OK)**:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1Ni...",
    "refresh_token": "ref_a1b2c3d4e5f6...",
    "token_type": "Bearer",
    "expires_in": 900,
    "user": {
      "id": "a2c3b4d5-0000-1111-2222-333344445555",
      "phone_number": "+250788123456",
      "role": "customer",
      "preferred_language": "rw"
    }
  }
  ```

### 3. Refresh Access Token
- **Method & Path**: `POST /v1/auth/token/refresh`
- **Access**: Public
- **Request Body**:
  ```json
  {
    "refresh_token": "ref_a1b2c3d4e5f6..."
  }
  ```
- **Behavior**: Returns a new `access_token` and rotated `refresh_token`; previous refresh token is immediately invalidated.

### 4. Admin Portal Login & MFA Challenge
- **Method & Path**: `POST /v1/auth/admin/login`
- **Access**: Public
- **Request Body**:
  ```json
  {
    "email": "support@fixnet.rw",
    "password": "SecurePassword123!"
  }
  ```
- **Success Response (202 Accepted — MFA Required)**:
  ```json
  {
    "mfa_required": true,
    "mfa_token": "mfa_temp_token_9988776655"
  }
  ```

### 5. Admin TOTP Verification
- **Method & Path**: `POST /v1/auth/admin/mfa-verify`
- **Access**: Public (requires valid `mfa_token`)
- **Request Body**:
  ```json
  {
    "mfa_token": "mfa_temp_token_9988776655",
    "totp_code": "123456"
  }
  ```
- **Response**: Full `access_token` and `refresh_token`, matching the mobile response shape.

### 6. Get Current User Profile
- **Method & Path**: `GET /v1/users/me`
- **Access**: Authenticated (all roles)
- **Response (200 OK)**:
  ```json
  {
    "id": "a2c3b4d5-0000-1111-2222-333344445555",
    "phone_number": "+250788123456",
    "role": "technician",
    "preferred_language": "rw",
    "created_at": "2026-08-10T10:00:00Z"
  }
  ```

### 7. Update Language Preference
- **Method & Path**: `PATCH /v1/users/me/language`
- **Access**: Authenticated (all roles)
- **Request Body**:
  ```json
  {
    "preferred_language": "en"
  }
  ```

---

## 3. Technician Profiles & Onboarding — `/v1/technicians`

### 1. Register Technician Profile
- **Method & Path**: `POST /v1/technicians/register`
- **Access**: Authenticated (`technician` role)
- **Request Body**:
  ```json
  {
    "business_type": "individual",
    "service_categories": ["plumbing", "electrical"],
    "id_document_url": "s3://private-docs/id_12345.pdf"
  }
  ```
- **Success Response (201 Created)**:
  ```json
  {
    "profile_id": "tech_profile_778899",
    "verification_status": "pending",
    "subscription_status": "lapsed",
    "message": "Registration submitted. Pending admin verification."
  }
  ```

### 2. Search & Filter Technicians (Customer)
- **Method & Path**: `GET /v1/technicians`
- **Query Params**: `category=plumbing&lat=-1.9441&lng=30.0619&radius_km=10&page=1`
- **Access**: Authenticated (`customer`)
- **Success Response (200 OK)**:
  ```json
  {
    "count": 12,
    "results": [
      {
        "id": "tech_profile_778899",
        "business_name": "Kigali Quick Fix",
        "service_categories": ["plumbing"],
        "rating": 4.8,
        "completed_jobs": 34,
        "is_top_rated": true,
        "distance_km": 2.3
      }
    ]
  }
  ```

### 3. Fetch Single Technician Profile
- **Method & Path**: `GET /v1/technicians/{id}`
- **Access**: Authenticated (`customer`)
- Returns profile details, uploaded portfolio content, star ratings, and review summaries.

### 4. Upload Work Portfolio or Spare Part Content
- **Method & Path**: `POST /v1/technicians/me/content`
- **Access**: Authenticated (`technician`)
- **Request Body**:
  ```json
  {
    "type": "photo",
    "media_url": "https://storage.fixnet.rw/content/work_1.jpeg",
    "description": "Fixed leaking pipe under kitchen sink"
  }
  ```

### 5. Fetch Technician Dashboard
- **Method & Path**: `GET /v1/technicians/me/dashboard`
- **Access**: Authenticated (`technician`)
- **Success Response (200 OK)**:
  ```json
  {
    "trial_ends_at": "2026-09-10T00:00:00Z",
    "trial_days_remaining": 22,
    "leads_received_this_month": 18,
    "quotes_accepted": 12,
    "earnings_this_month_rwf": 150000
  }
  ```

### 6. Complete Safety & Scam Training
- **Method & Path**: `POST /v1/technicians/me/onboarding-complete`
- **Access**: Authenticated (`technician`)
- **Request Body**:
  ```json
  { "training_completed": true }
  ```

---

## 4. Messaging, Quotes & AI Assistant — `/v1/conversations`, `/v1/ai`

### 1. Query Technician AI Assistant
- **Method & Path**: `POST /v1/ai/chat`
- **Access**: Authenticated (`customer`)
- **Request Body**:
  ```json
  {
    "technician_id": "tech_profile_778899",
    "prompt": "Does this plumber handle copper pipes on weekends?"
  }
  ```
- **Success Response (200 OK)**:
  ```json
  {
    "response": "Based on the technician's uploaded portfolio, they specify working on standard PVC and copper pipes. No explicit weekend hours are listed. Would you like to chat with them directly?",
    "confidence_score": 0.92,
    "can_answer": true
  }
  ```

### 2. Initiate Chat Thread
- **Method & Path**: `POST /v1/conversations`
- **Access**: Authenticated (`customer`)
- **Request Body**:
  ```json
  { "technician_id": "tech_profile_778899" }
  ```
- **Response (201 Created)**:
  ```json
  {
    "conversation_id": "conv_11223344",
    "status": "chat_opened"
  }
  ```

### 3. List User Conversations
- **Method & Path**: `GET /v1/conversations`
- **Access**: Authenticated (`customer`, `technician`)

### 4. Get Conversation Messages
- **Method & Path**: `GET /v1/conversations/{id}/messages`
- **Query Params**: `limit=50&before_id=msg_99`
- **Access**: Participant / Support Agent
- **Success Response (200 OK)**:
  ```json
  {
    "messages": [
      {
        "id": "msg_101",
        "sender_type": "customer",
        "content": "Hello, my water heater is leaking.",
        "is_masked": false,
        "created_at": "2026-08-23T10:15:00Z"
      },
      {
        "id": "msg_102",
        "sender_type": "technician",
        "content": "I can fix it today. My phone is [REDACTED]",
        "is_masked": true,
        "created_at": "2026-08-23T10:16:00Z"
      }
    ]
  }
  ```

### 5. Send Structured Quote
- **Method & Path**: `POST /v1/conversations/{id}/quotes`
- **Access**: Authenticated (`technician`)
- **Request Body**:
  ```json
  {
    "total_price_rwf": 25000,
    "scope_notes": "Replacing heater valve and sealing joint"
  }
  ```
- **Response (201 Created)**:
  ```json
  {
    "quote_id": "quote_556677",
    "status": "quote_sent"
  }
  ```

### 6. Respond to Quote (Accept/Decline)
- **Method & Path**: `POST /v1/quotes/{id}/respond`
- **Access**: Authenticated (`customer`)
- **Request Body**:
  ```json
  { "action": "accept" }
  ```
- **Response (200 OK)**:
  ```json
  {
    "status": "quote_accepted",
    "required_booking_deposit_rwf": 2500,
    "payment_next_step_url": "/v1/payments/booking-deposit"
  }
  ```

---

## 5. Payments & Subscriptions — `/v1/payments`, `/v1/subscriptions`

### 1. Pay Booking Deposit
- **Method & Path**: `POST /v1/payments/booking-deposit`
- **Access**: Authenticated (`customer`)
- **Request Body**:
  ```json
  {
    "quote_id": "quote_556677",
    "payment_method": "momo",
    "phone_number": "+250788123456"
  }
  ```
- **Success Response (202 Accepted)**:
  ```json
  {
    "transaction_id": "tx_momo_990011",
    "status": "pending",
    "user_instruction": "Approve the MoMo USSD prompt on your phone."
  }
  ```

### 2. Payment Gateway Webhook
- **Method & Path**: `POST /v1/payments/webhook`
- **Access**: Payment provider gateway (verified via signature header)
- **Request Body**:
  ```json
  {
    "transaction_id": "tx_momo_990011",
    "quote_id": "quote_556677",
    "status": "successful",
    "amount_rwf": 2500
  }
  ```
- **Server Action**: Atomically unlocks technician phone number in chat and transitions job to `deposit_paid_unlocked`.

### 3. Get Payment Receipt PDF
- **Method & Path**: `GET /v1/payments/{id}/receipt`
- **Access**: Authenticated (payer customer)
- Returns PDF binary stream download.

### 4. Technician Subscription Payment
- **Method & Path**: `POST /v1/subscriptions/subscribe`
- **Access**: Authenticated (`technician`)
- **Request Body**:
  ```json
  {
    "plan_id": "plan_monthly_pro",
    "payment_method": "momo",
    "phone_number": "+250788123456"
  }
  ```

---

## 6. Job Lifecycle & Service History — `/v1/jobs`

### 1. View Service History
- **Method & Path**: `GET /v1/jobs/history`
- **Access**: Authenticated (`customer`)
- **Response (200 OK)**:
  ```json
  {
    "jobs": [
      {
        "job_id": "job_001",
        "technician_name": "Jean-Pierre N.",
        "service_category": "plumbing",
        "date": "2026-08-15",
        "deposit_paid_rwf": 2500,
        "status": "completed"
      }
    ]
  }
  ```

### 2. One-Tap Re-Book
- **Method & Path**: `POST /v1/jobs/{id}/rebook`
- **Access**: Authenticated (`customer`)
- Directly creates or re-opens chat with former technician.

### 3. Confirm Job Completion
- **Method & Path**: `POST /v1/jobs/{id}/complete`
- **Access**: Authenticated (`customer`)
- **Request Body**: `{ "completed": true }`

### 4. Submit Rating & Review
- **Method & Path**: `POST /v1/jobs/{id}/reviews`
- **Access**: Authenticated (`customer`)
- **Request Body**:
  ```json
  {
    "rating": 5,
    "comment": "Fast and clean plumbing work!",
    "photo_url": "https://storage.fixnet.rw/reviews/rev_1.jpeg"
  }
  ```

---

## 7. Admin Portal Endpoints — `/v1/admin`

### 1. Verify or Reject Technician
- **Method & Path**: `PATCH /v1/admin/technicians/{id}/verify`
- **Access**: `support_agent`, `system_admin`
- **Request Body**:
  ```json
  {
    "verification_status": "verified",
    "rejection_reason": null
  }
  ```

### 2. Moderate Uploaded Content
- **Method & Path**: `DELETE /v1/admin/content/{id}`
- **Access**: `support_agent`, `system_admin`
- **Request Body**: `{ "reason": "Inappropriate content violation" }`

### 3. Resolve Dispute & Process Deposit Refund
- **Method & Path**: `POST /v1/admin/disputes/{id}/refund`
- **Access**: `support_agent`, `finance_admin`, `system_admin`
- **Request Body**:
  ```json
  {
    "refund_amount_rwf": 2500,
    "internal_notes": "Technician failed to show up for appointment."
  }
  ```

### 4. Global Pricing Configuration
- **Method & Path**: `POST /v1/admin/config/pricing`
- **Access**: `system_admin`
- **Request Body**:
  ```json
  {
    "booking_deposit_type": "flat",
    "default_deposit_amount_rwf": 2000,
    "default_trial_days": 30
  }
  ```

### 5. Generate Monthly Financial CSV Report
- **Method & Path**: `GET /v1/admin/reports/revenue?month=2026-08&format=csv`
- **Access**: `finance_admin`, `system_admin`
- Returns CSV file download.

### 6. Account Suspension (With Audit Log)
- **Method & Path**: `POST /v1/admin/users/{id}/suspend`
- **Access**: `system_admin`
- **Request Body**: `{ "reason": "Repeated off-platform payment scam reports" }`

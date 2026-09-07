# FixNet Business Logic Rules Detailed

## 1. Authentication & Identity
- **AUTH-01 — Phone Registration via OTP**: Primary user identifier is phone number formatted in E.164. Passwordless SMS OTP.
- **AUTH-02 — OTP Brute-Force Protection**: 5 failed OTP attempts within 15 minutes triggers a 30-minute lock on that phone number.
- **AUTH-03 — JWT Session Management**: Short access tokens (15 mins) and rotating refresh tokens (30 days).
- **AUTH-04 — Role-Based Access Control (RBAC)**: Roles: `customer`, `technician`, `support_agent`, `finance_admin`, `system_admin`.
- **AUTH-05 — Multi-Factor Authentication for Admins**: Email + password + mandatory TOTP 2FA.

## 2. Technician Lifecycle & Onboarding
- **TECH-01 — Business Type Selection**: Individual or Company.
- **TECH-02 — Service Category Selection**: Must select at least one category (e.g. plumbing, electrical).
- **TECH-03 — Verification Gate Before Going Live**: Newly registered profiles have `is_searchable = FALSE` and `verification_status = "pending"` until approved by Support Agent/Admin.
- **TECH-04 — Mandatory Safety & Digital Training**: After verification, technician must complete safety tutorial (`onboarding-complete`) before `is_searchable` becomes `TRUE`.
- **TECH-05 — Automatic Free Trial Activation**: Once verified and trained, a 30-day free trial activates (`subscription_status = "trial_active"`).
- **TECH-06 — Trial Expiry Warning**: Warning displayed at 5 or fewer days remaining without cutting off active chats.
- **TECH-07 — Trial Lapse**: If trial ends without paid subscription, `subscription_status = "lapsed"` and `is_searchable = FALSE`.
- **TECH-08 — Subscription Payment Failure Grace Period**: 3-day grace period on recurring MoMo charge failure before lapsing.

## 3. Customer Discovery & AI Assistant
- **SEARCH-01 — Search Result Filtering**: Only profiles with `is_searchable = TRUE` AND `verification_status = "verified"` are returned.
- **SEARCH-02 — AI Assistant Knowledge Boundary**: RAG queries restricted strictly to that technician's uploaded portfolio and verified fields. No general LLM hallucinations.
- **SEARCH-03 — AI Fallback to Human Chat**: If information is absent, respond with clear admission and offer button to open direct chat.

## 4. In-App Messaging & Negotiation
- **CHAT-01 — Conversation Creation & Technician Notification**: Customer initiating chat sends instant push notification and SMS to technician.
- **CHAT-02 — Automatic Contact Information Masking**: Phone numbers, emails, and URLs are masked to `[Contact hidden until deposit paid]` before deposit payment.
- **CHAT-03 — Structured Quote Creation**: Technician submits structured quote (RWF amount, scope notes) producing Accept/Decline card.
- **CHAT-04 — Quote Expiry**: Quotes expire automatically after 48 hours without response.
- **CHAT-05 — Quote Acceptance & Booking Creation**: Accepting quote creates booking in `quote_accepted` status and prompts deposit payment.
- **CHAT-06 — Admin Dispute Oversight**: Chat logs accessible for dispute resolution by support agents.

## 5. Booking Deposit & Contact Unlock
- **BOOK-01 — Deposit Labeling & Framing**: Booking deposit framed towards the overall service cost.
- **BOOK-02 — Successful Payment & Contact Unlock**: Verified payment atomically sets booking to `deposit_paid` and reveals technician contact in chat.
- **BOOK-03 — Failed Payment Handling**: Booking remains `quote_accepted` and contact remains locked.
- **BOOK-04 — Customer Declines to Pay**: Option to cancel or decline quote.
- **BOOK-05 — Booking Auto-Expiry**: Unpaid bookings expire if not funded within defined timeline.

## 6. Service Completion, Ratings & Reviews
- **REVIEW-01 — Post-Service Completion Prompt**: Customer prompted 24 hours post-contact unlock via push + SMS to confirm completion.
- **REVIEW-02 — Review Submission Flow**: Customer confirms completion, rates 1–5 stars, optional comment, optional photo.
- **REVIEW-03 — Reputation Score Recalculation**: Weighted average recalculation with recency bias.
- **REVIEW-04 — Top Rated Badge Automation**: Awarded if `reputation_score >= 4.5` AND `completed_jobs >= 10`.
- **REVIEW-05 — One-Tap Re-Booking**: Direct chat initiation with former technician from service history.

## 7. Payments & Financial Integrity
- **PAY-01 — Integer-Only Currency Storage**: All currency amounts stored as integers in RWF (or cents) to prevent rounding errors.
- **PAY-02 — Instant Receipt Generation**: Generate downloadable PDF receipt on successful payment.
- **PAY-03 — Dispute Refund Processing**: Support / Finance / System Admin can process deposit refunds.
- **PAY-04 — Recurring Subscription Billing**: Monthly billing for technician platform subscriptions.

## 8. Admin Portal Operations
- **ADMIN-01 — Technician Identity Verification**: Review ID documents and approve/reject.
- **ADMIN-02 — Content Moderation**: Remove inappropriate portfolio content.
- **ADMIN-03 — Account Suspension**: Suspend fraudulent users with immutable audit logs.
- **ADMIN-04 — Dynamic Deposit Pricing**: Global configuration for deposit amounts and trial periods.

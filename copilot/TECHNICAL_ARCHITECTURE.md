# QuestionCraft: Technical Architecture & Implementation Details

---

## 1. CURRENT SYSTEM ARCHITECTURE

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Frontend (React + Tailwind)                       │
│  Landing → Auth → Dashboard → GeneratePaper → Preview → Export          │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │ HTTP POST multipart/form-data
                               │ (currently unauthenticated)
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          FastAPI Backend                                 │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  API Layer (paper.py, regenerate.py, utilities.py)             │   │
│  │  ├─ POST /api/v1/generate-paper/                               │   │
│  │  ├─ POST /api/v1/validate-paper/                               │   │
│  │  └─ POST /api/v1/regenerate-question/                          │   │
│  └───────────┬───────────────────────────────────────────────────┘   │
│  ┌───────────▼─────────────────────────────────────────────────────┐  │
│  │  PaperService (Orchestration)                                    │  │
│  │  ├─ generate(): orchestrates full pipeline                       │  │
│  │  ├─ regenerate_question(): regenerates single question           │  │
│  │  └─ validate_paper(): structural validation                      │  │
│  └───────────┬────────────────────────┬────────────────────────────┘  │
│  ┌───────────▼──────────────┐  ┌──────▼─────────────────────────────┐ │
│  │  RAG Pipeline            │  │  Generation Pipeline               │ │
│  │  ├─ ensure_indexed()     │  │  ├─ extract_topics()              │ │
│  │  ├─ retrieve()           │  │  ├─ generate_queries()            │ │
│  │  └─ IndexStore           │  │  ├─ generate_question()           │ │
│  │    ├─ Indexer            │  │  ├─ extract_pattern()             │ │
│  │    │ ├─ Loader           │  │  ├─ distribute_topics()           │ │
│  │    │ ├─ Chunker          │  │  └─ validate_paper()              │ │
│  │    │ ├─ Embedder         │  │                                    │ │
│  │    └─ Retriever          │  │                                    │ │
│  │      ├─ DenseSearch      │  │                                    │ │
│  │      ├─ SparseSearch     │  │                                    │ │
│  │      ├─ Fusion (RRF)     │  │                                    │ │
│  │      └─ Reranker         │  │                                    │ │
│  └──────────────────────────┘  └────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Core (Config, Logging, Error Handling, Middleware)             │  │
│  │  ├─ config.py: pydantic Settings                                │  │
│  │  ├─ logging.py: structured JSON logging                         │  │
│  │  ├─ middleware.py: request timing, error handling               │  │
│  │  └─ exceptions.py: custom exception hierarchy                   │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                │                      │                      │
                │ Calls                │ Calls                │ Calls
                ▼                      ▼                      ▼
         OpenAI API         Cohere API (optional)      File Storage
         (embeddings,       (reranking)               (./uploaded_files)
          generation)                                (./rag_index)
```

---

## 2. PRODUCTION SAAS ARCHITECTURE (Proposed)

### Multi-Tenant, Enterprise-Ready

```
┌────────────────────────────────────────────────────────────────────────┐
│                         CDN (CloudFront)                               │
│  Static assets, PDFs, images, JavaScript bundles                      │
└────────────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────▼──────────┐
                    │   Load Balancer    │
                    │  (Round-robin)     │
                    └─────┬─────┬────────┘
                    ┌─────▼─────▼─────────────────────────────────┐
                    │ Frontend (Static, served by S3/CloudFront) │
                    │ React SPA + Tailwind CSS                   │
                    └───────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
    ┌────▼───┐        ┌────────▼─────┐      ┌────▼────┐
    │  API   │        │   API        │      │   API  │
    │Instance│        │  Instance    │      │Instance│
    │   1    │        │      2       │      │   3    │
    └────┬───┘        └────────┬─────┘      └────┬────┘
         │                     │                  │
         └─────────────────────┼──────────────────┘
                               │
         ┌─────────────────────┼──────────────────┐
         │                     │                  │
    ┌────▼────┐         ┌──────▼────┐      ┌─────▼────┐
    │ Redis   │         │PostgreSQL │      │  S3      │
    │ Cache   │         │ Database  │      │ Storage  │
    │(3 replica)        │(Primary + │      │(FAISS    │
    │         │         │  Replicas)       │ indexes) │
    └────────┘         └───────────┘      └──────────┘
                             │
                    ┌────────┼─────────┐
                    │        │         │
                    ▼        ▼         ▼
            ┌──────────┬──────────┬────────────┐
            │ Backups  │  Snapshots│ Monitoring│
            │(daily)   │  (hourly) │ (DataDog) │
            └──────────┴──────────┴────────────┘
```

### Request Flow (Multi-Tenant)

```
1. CLIENT REQUEST
   ↓
2. LOAD BALANCER
   ├─ Routes to available API instance
   └─ SSL termination
   ↓
3. API GATEWAY (FastAPI)
   ├─ Extract JWT from Authorization header
   ├─ Validate signature with Supabase
   ├─ Extract user_id, organization_id, role
   └─ Add to request.state
   ↓
4. AUTHENTICATION MIDDLEWARE
   ├─ Verify JWT not expired
   ├─ Check user still active
   └─ Abort if auth fails
   ↓
5. AUTHORIZATION MIDDLEWARE (RBAC)
   ├─ Check user role for endpoint
   ├─ Example: require_role("admin")
   └─ Abort if insufficient permissions
   ↓
6. TENANCY MIDDLEWARE
   ├─ Verify organization_id from JWT matches request
   ├─ Set request.state.organization_id
   └─ All queries filtered by this
   ↓
7. BUSINESS LOGIC (PaperService)
   ├─ Access user/org context from request.state
   ├─ Retrieve only papers owned by this org
   ├─ Generate questions respecting org quotas
   └─ Log all actions to audit_logs table
   ↓
8. RESPONSE
   ├─ Add X-Request-ID header
   ├─ Add X-Response-Time header
   └─ Return JSON (or error)
   ↓
9. LOGGING
   ├─ Structured JSON log with:
   │  ├─ request_id
   │  ├─ user_id
   │  ├─ organization_id
   │  ├─ endpoint
   │  ├─ status_code
   │  ├─ response_time
   │  └─ error (if any)
   ├─ Send to CloudWatch
   └─ Aggregate in Datadog
```

---

## 3. DATABASE SCHEMA (PostgreSQL)

```sql
-- Users (Supabase Auth manages this via RLS)
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    full_name VARCHAR,
    organization_id INT NOT NULL REFERENCES organizations(id),
    role VARCHAR DEFAULT 'teacher',  -- student, teacher, admin, dept_head, super_admin
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Organizations (Universities, Departments, Institutes)
CREATE TABLE organizations (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    slug VARCHAR UNIQUE NOT NULL,  -- URL-safe name
    plan VARCHAR DEFAULT 'pro',  -- free, pro, enterprise
    api_quota_per_month INT DEFAULT 1000,  -- Questions per month
    api_quota_used INT DEFAULT 0,
    features JSONB DEFAULT '{}',  -- Custom features per tier
    branding JSONB DEFAULT '{}',  -- Logo, colors, etc.
    sso_config JSONB,  -- SAML/OAuth configuration
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Papers (Generated Question Papers)
CREATE TABLE papers (
    id SERIAL PRIMARY KEY,
    organization_id INT NOT NULL REFERENCES organizations(id),
    user_id UUID NOT NULL REFERENCES users(id),
    title VARCHAR NOT NULL,
    subject VARCHAR NOT NULL,
    description TEXT,
    content JSONB NOT NULL,  -- Full paper structure
    status VARCHAR DEFAULT 'draft',  -- draft, final, archived
    index_key VARCHAR,  -- For regeneration without re-upload
    syllabus_hash VARCHAR,  -- Hash of uploaded files
    total_marks INT,
    version INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    exported_at TIMESTAMP,  -- Last export time
    UNIQUE(organization_id, id)  -- RLS: only see own org
);

-- Paper Versions
CREATE TABLE paper_versions (
    id SERIAL PRIMARY KEY,
    paper_id INT NOT NULL REFERENCES papers(id) ON DELETE CASCADE,
    version_number INT NOT NULL,
    content JSONB NOT NULL,
    created_by UUID NOT NULL REFERENCES users(id),
    change_reason VARCHAR,  -- "user_feedback", "auto_improve", "question_regenerated"
    created_at TIMESTAMP DEFAULT NOW()
);

-- Questions (Reusable Question Bank)
CREATE TABLE questions (
    id SERIAL PRIMARY KEY,
    organization_id INT NOT NULL REFERENCES organizations(id),
    created_by UUID NOT NULL REFERENCES users(id),
    subject VARCHAR NOT NULL,
    topic VARCHAR,
    subtopic VARCHAR,
    question_text TEXT NOT NULL,
    question_type VARCHAR,  -- "short_answer", "long_answer", "mcq"
    marks INT,
    blooms_level VARCHAR,  -- "remember", "understand", "apply", etc.
    difficulty VARCHAR,  -- "easy", "medium", "hard"
    correct_answer TEXT,
    explanation TEXT,
    tags JSONB DEFAULT '[]',  -- ["chapter1", "economics"]
    usage_count INT DEFAULT 0,
    quality_score NUMERIC(3,2),  -- 0-1, based on feedback
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Audit Logs (GDPR/FERPA Compliance)
CREATE TABLE audit_logs (
    id BIGSERIAL PRIMARY KEY,
    organization_id INT NOT NULL REFERENCES organizations(id),
    user_id UUID REFERENCES users(id),  -- NULL for system actions
    action VARCHAR NOT NULL,  -- "generated_paper", "regenerated_question"
    resource_type VARCHAR,  -- "paper", "question"
    resource_id INT,
    details JSONB,  -- { "paper_id": 123, "changes": {...} }
    ip_address INET,
    user_agent VARCHAR,
    status VARCHAR,  -- "success", "failure"
    error_message TEXT,
    timestamp TIMESTAMP DEFAULT NOW(),
    INDEX audit_logs_org_user (organization_id, user_id)
);

-- API Keys (for integrations)
CREATE TABLE api_keys (
    id SERIAL PRIMARY KEY,
    organization_id INT NOT NULL REFERENCES organizations(id),
    name VARCHAR,
    key_hash VARCHAR UNIQUE NOT NULL,  -- bcrypt hash
    last_used_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,
    rate_limit_per_min INT DEFAULT 100
);

-- Subscriptions & Billing
CREATE TABLE subscriptions (
    id SERIAL PRIMARY KEY,
    organization_id INT NOT NULL UNIQUE REFERENCES organizations(id),
    stripe_customer_id VARCHAR,
    stripe_subscription_id VARCHAR,
    plan VARCHAR NOT NULL,  -- "free", "pro", "enterprise"
    billing_period_start DATE,
    billing_period_end DATE,
    amount_usd NUMERIC(10, 2),
    status VARCHAR,  -- "active", "past_due", "canceled"
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- LMS Integrations
CREATE TABLE lms_integrations (
    id SERIAL PRIMARY KEY,
    organization_id INT NOT NULL REFERENCES organizations(id),
    lms_type VARCHAR NOT NULL,  -- "canvas", "moodle", "blackboard"
    api_endpoint VARCHAR NOT NULL,
    api_key_encrypted TEXT,  -- Encrypted at rest
    course_id VARCHAR,  -- Canvas course ID, etc.
    sync_enabled BOOLEAN DEFAULT FALSE,
    last_sync_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Analytics Snapshots
CREATE TABLE analytics (
    id BIGSERIAL PRIMARY KEY,
    organization_id INT NOT NULL,
    paper_id INT REFERENCES papers(id),
    metric_name VARCHAR,  -- "avg_question_difficulty", "student_performance"
    metric_value NUMERIC,
    dimensions JSONB,  -- { "subject": "Physics", "bloom_level": "remember" }
    recorded_at TIMESTAMP DEFAULT NOW(),
    INDEX analytics_org_date (organization_id, recorded_at)
);

-- Row-Level Security Policies
CREATE POLICY papers_isolation ON papers
    FOR ALL TO authenticated
    USING (organization_id IN (
        SELECT organization_id FROM users WHERE id = current_user_id()
    ));

CREATE POLICY questions_isolation ON questions
    FOR ALL TO authenticated
    USING (organization_id IN (
        SELECT organization_id FROM users WHERE id = current_user_id()
    ));

CREATE POLICY audit_logs_isolation ON audit_logs
    FOR ALL TO authenticated
    USING (organization_id IN (
        SELECT organization_id FROM users WHERE id = current_user_id()
    ));
```

---

## 4. API ENDPOINTS (Production Version)

### Authentication
```
POST /api/v1/auth/signup
  Input: { email, password, full_name }
  Output: { user_id, token, organization_id }

POST /api/v1/auth/login
  Input: { email, password }
  Output: { user_id, token, organization_id, role }

POST /api/v1/auth/refresh
  Input: { refresh_token }
  Output: { access_token, expires_in }

POST /api/v1/auth/logout
  Input: { user_id }
  Output: { success: true }

POST /api/v1/auth/sso/google
  Input: { code }
  Output: { user_id, token, organization_id }

POST /api/v1/auth/sso/saml/acs
  Input: SAML assertion
  Output: Redirect to dashboard
```

### Paper Management
```
POST /api/v1/papers/generate
  Requires: Bearer token, role=teacher
  Input: (multipart/form-data)
    - syllabus_files (PDF, PPTX)
    - subject
    - difficulty_level
    - manual_pattern (optional)
  Output: { paper_id, index_key, content, warnings }
  Rate limit: 10 per hour per user

GET /api/v1/papers
  Requires: Bearer token
  Query: ?organization_id=X&page=1&limit=20
  Output: { papers: [...], total, page, limit }

GET /api/v1/papers/{paper_id}
  Requires: Bearer token
  Output: { id, title, subject, content, created_at, versions: [...] }

PUT /api/v1/papers/{paper_id}
  Requires: Bearer token, ownership
  Input: { title, subject, status }
  Output: { id, ...updated fields }

DELETE /api/v1/papers/{paper_id}
  Requires: Bearer token, ownership
  Output: { success: true }

POST /api/v1/papers/{paper_id}/versions
  Input: { version_number }
  Output: { content, created_at }

POST /api/v1/papers/{paper_id}/export
  Input: { format: "pdf" | "docx", include_answers: bool }
  Output: { url, expires_at }
```

### Question Regeneration
```
POST /api/v1/papers/{paper_id}/regenerate-question
  Input: { section, question_index }
  Output: { question }

POST /api/v1/papers/{paper_id}/regenerate-section
  Input: { section }
  Output: { section }
```

### Admin/Organization Management
```
POST /api/v1/organizations
  Requires: Bearer token, role=super_admin
  Input: { name, plan, features }
  Output: { organization_id }

GET /api/v1/organizations/{org_id}
  Requires: Bearer token, org membership
  Output: { name, plan, users_count, api_quota_used }

PUT /api/v1/organizations/{org_id}
  Requires: Bearer token, role=admin
  Input: { name, plan, sso_config }
  Output: { ...updated }

POST /api/v1/organizations/{org_id}/users
  Requires: Bearer token, role=admin
  Input: { email, role }
  Output: { user_id, email, role }

DELETE /api/v1/organizations/{org_id}/users/{user_id}
  Requires: Bearer token, role=admin
  Output: { success: true }
```

### Analytics
```
GET /api/v1/organizations/{org_id}/analytics
  Requires: Bearer token, role=admin
  Query: ?metric=question_difficulty&period=month
  Output: { data: [...], total_papers, avg_marks }

GET /api/v1/papers/{paper_id}/analytics
  Requires: Bearer token
  Output: { student_performance: {...}, question_difficulty: [...] }
```

### LMS Integration
```
POST /api/v1/integrations/canvas/connect
  Input: { api_endpoint, api_token, course_id }
  Output: { integration_id }

POST /api/v1/integrations/canvas/publish
  Input: { paper_id }
  Output: { assignment_id, url }

GET /api/v1/integrations/{integration_id}/sync
  Output: { status, last_sync_at }
```

### Audit Logs
```
GET /api/v1/audit-logs
  Requires: Bearer token, role=admin
  Query: ?organization_id=X&start_date=2024-01-01&end_date=2024-01-31
  Output: { logs: [...], total }

GET /api/v1/audit-logs/export
  Requires: Bearer token, role=admin
  Query: ?format=csv
  Output: CSV file
```

---

## 5. SECURITY ARCHITECTURE

### Authentication Flow
```
User Login
    ↓
Frontend: Supabase Auth (sign in with email/password or OAuth)
    ↓
Supabase: Hash password, validate, return JWT
    ↓
Frontend: Store JWT in localStorage (or secure cookie)
    ↓
API Request: Include "Authorization: Bearer {JWT}"
    ↓
Backend Middleware: Verify JWT signature with Supabase public key
    ↓
Backend: Extract user_id, organization_id from JWT claims
    ↓
Add to request.state for use in handlers
```

### Authorization (RBAC) Levels
```
Level 1: User exists (authenticated)
  - Can access /papers (own only)
  - Can generate papers (rate limited)

Level 2: Teacher role
  - Can create/edit papers
  - Can regenerate questions
  - Can view class analytics

Level 3: Admin role
  - Can manage all org papers
  - Can view all audit logs
  - Can manage users
  - Can change organization settings

Level 4: Dept Head role
  - Can manage papers across assigned departments
  - Can view department analytics

Level 5: Super Admin role
  - Can manage all organizations
  - Can manage billing
  - Can access all audit logs
```

### API Key Security
```
Generate API Key
    ↓
Hash with bcrypt (80+ iterations)
    ↓
Store hash in database
    ↓
Return to user ONCE (never again)
    ↓
When used:
    ├─ API key in header: X-API-Key: {key}
    ├─ Hash the incoming key
    ├─ Compare with stored hash
    ├─ Validate organization_id matches
    └─ Check rate limits per org
```

### Data Encryption
```
At Rest:
  - Passwords: Supabase (bcrypt)
  - LMS API keys: AES-256 in DB
  - SAML configs: Encrypted at rest

In Transit:
  - All connections: TLS 1.3+
  - API responses: No sensitive data in URL
  - Logs: Scrub API keys, passwords

In Memory:
  - No sensitive data logged
  - JWT expires in 1 hour
  - Refresh tokens rotate with use
```

---

## 6. SCALABILITY ROADMAP

### Current Bottlenecks
1. **FAISS indexes in memory** → Use Redis/S3 instead
2. **Sequential embedding** → Batch OpenAI calls
3. **Single database** → Add read replicas
4. **No caching** → Add Redis for papers, questions

### Phase 1: Scaling (Weeks 7-8)
```
✅ Redis caching layer
  - Cache generated papers (24 hours)
  - Cache embeddings (24 hours)
  - Cache frequently accessed questions

✅ Database optimization
  - Add indexes on (organization_id, created_at)
  - Add indexes on (user_id, paper_id)
  - Separate read replica for analytics

✅ Async job queue
  - Move long operations to Celery/RQ
  - Example: batch embedding computation
  - Parallel section generation (already done)
```

### Phase 2: Scaling (Months 3-4)
```
✅ FAISS index partitioning
  - By organization (separate index per org)
  - By subject (prevent mixing subjects)

✅ Load balancing
  - Multiple API instances (3-5)
  - Health checks every 30s
  - Auto-restart on failure

✅ CDN
  - Static assets (frontend)
  - PDF exports (cache 24 hours)
  - Reduce TTFB by 50%
```

### Phase 3: Enterprise Scale (Month 6+)
```
✅ Kubernetes deployment
  - Horizontal pod autoscaling (CPU > 70%)
  - Node auto-scaling (EKS/GKE)
  - StatefulSet for FAISS servers

✅ Data partitioning
  - Papers by date (hot storage: 30 days, warm: 1 year)
  - Old papers to archive (Glacier)
  - Reduce database size by 80%

✅ Global distribution
  - API regions: US-East, EU-West, Asia-Pacific
  - Latency-based routing
  - Local FAISS replicas
```

---

## 7. MONITORING & OBSERVABILITY

### Metrics to Track
```
Application Metrics:
  - Requests per second (by endpoint)
  - p50/p95/p99 latency
  - Error rate (by status code)
  - Generate-paper completion time
  - AI generation latency (OpenAI call time)

Business Metrics:
  - Questions generated per day
  - Papers per organization per month
  - Average paper quality (user satisfaction)
  - LMS publication success rate
  - API key usage per org

Infrastructure Metrics:
  - Database connections
  - Redis memory usage
  - CPU usage per instance
  - Network I/O
  - Disk I/O
```

### Alerting Rules
```
🔴 CRITICAL:
  - API error rate > 1% for 5 minutes
  - Database connection pool exhausted
  - FAISS service down
  - OpenAI API failing

🟠 HIGH:
  - Generate-paper latency > 120 seconds
  - API error rate > 0.1% for 10 minutes
  - Redis memory > 80% capacity
  - Database replicas lagging > 30 seconds

🟡 MEDIUM:
  - Generate-paper latency > 90 seconds
  - API CPU usage > 80%
  - Disk usage > 70%
```

### Dashboards
```
Real-Time Operations Dashboard:
  - API health (status codes over time)
  - Generate-paper latency distribution
  - Concurrent users
  - Error logs (searchable)

Business Dashboard:
  - Questions generated today/week/month
  - Papers by organization
  - Most active users
  - LMS integration health

Security Dashboard:
  - Failed login attempts
  - Suspicious API key usage
  - Audit log searchable
  - Rate limit violations
```

---

## 8. DEPLOYMENT CHECKLIST

### Pre-Production (Staging)
- [ ] Database fully migrated to PostgreSQL
- [ ] Supabase Auth working (sign up, login, SSO test)
- [ ] RBAC tested for all roles
- [ ] HTTPS working (self-signed OK for staging)
- [ ] Rate limiting functional
- [ ] Sentry error tracking active
- [ ] Load tests passing (100 concurrent users)
- [ ] Backup/restore tested
- [ ] 50+ beta testers signed up
- [ ] Security audit passed (no critical vulnerabilities)

### Production (GA)
- [ ] SSL certificate (AWS ACM)
- [ ] Database automated backups (hourly)
- [ ] Database replicas in different AZ
- [ ] Monitoring dashboard (Datadog)
- [ ] Alerting configured (PagerDuty)
- [ ] Incident response runbook written
- [ ] Legal review (ToS, Privacy Policy)
- [ ] GDPR compliance verified
- [ ] SOC 2 audit scheduled
- [ ] Support ticketing system ready
- [ ] 24/7 on-call rotation established

---

## 9. ESTIMATED EFFORT BY COMPONENT

| Component | Backend | Frontend | Effort | Timeline |
|---|---|---|---|---|
| Supabase Auth | 2 days | 2 days | 4 days | Week 1 |
| Database schema + migrations | 3 days | - | 3 days | Week 1 |
| JWT middleware + RBAC | 2 days | 1 day | 3 days | Week 1 |
| Multi-tenancy isolation | 3 days | 1 day | 4 days | Week 2 |
| Paper history/versioning | 2 days | 2 days | 4 days | Week 2 |
| Admin dashboard | 2 days | 4 days | 6 days | Week 3 |
| Canvas LMS integration | 5 days | 1 day | 6 days | Week 4 |
| Audit logging | 2 days | 1 day | 3 days | Week 2 |
| Question review workflow | 2 days | 3 days | 5 days | Week 3 |
| Plagiarism detection | 3 days | 1 day | 4 days | Week 4 |
| Analytics queries + charts | 4 days | 3 days | 7 days | Week 4 |
| Docker + CI/CD | - | - | 3 days | Week 2 |
| Unit tests (50% coverage) | 5 days | 3 days | 8 days | Week 3 |
| Load testing | 2 days | - | 2 days | Week 2 |
| **TOTAL** | **38 days** | **22 days** | **60 days** | **12 weeks** |

---

## 10. COST ANALYSIS

### Monthly Infrastructure Costs (Production)

| Service | Usage | Cost/Month |
|---------|-------|-----------|
| **Compute (API Servers)** | 5 x t3.large (60% avg usage) | $250 |
| **Database (PostgreSQL)** | db.r5.large, 2 replicas, 500 GB storage | $400 |
| **Redis** | cache.r6g.xlarge | $150 |
| **S3 Storage** | 1 TB papers + indexes | $20 |
| **CDN (CloudFront)** | ~50 TB/month | $300 |
| **OpenAI API** | ~500K questions/month @ $0.01/question | $5,000 |
| **Cohere Reranking** | ~50K reranks/month @ $0.001 | $50 |
| **Monitoring (Datadog)** | 500K events/day | $300 |
| **Error Tracking (Sentry)** | 1M events/month | $100 |
| **Load Testing/QA** | BrowserStack, Locust | $200 |
| **Domain + SSL** | Renewal | $50 |
| **Backups (AWS Backup)** | Daily snapshots + S3 replication | $200 |
| **Support/Slack Apps** | Integrations | $50 |
| **TOTAL** | | **$7,070/month** |

### Unit Economics
- **Cost per question generated:** $0.01 (OpenAI) + $0.009 (infrastructure) = **$0.019**
- **Revenue per question:** $0.50 (Pro tier averaged) - $2.00 (Enterprise)
- **Gross margin per question:** 95%+ (highly profitable)

### Pricing Strategy Impact
| Plan | Price | Q/Month | Revenue/Month | Margin |
|------|-------|---------|---|---|
| Freemium (2 papers × 10 Q) | Free | 20Q | $0 | - |
| Pro ($150/year) | $12.50/month | 500Q | $12.50 | 90% |
| Org License ($10K/year) | $833/month | 5000Q | $833 | 92% |
| Enterprise | $3000+/month | 10000Q+ | $3000+ | 93% |

---

## END OF TECHNICAL ARCHITECTURE DOCUMENT

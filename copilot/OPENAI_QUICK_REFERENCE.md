# OpenAI Integration: Quick Reference Card

## The 30-Second Version

| Question | Answer |
|----------|--------|
| **Get API key from?** | https://platform.openai.com → Billing → API Keys → Create |
| **Cost per question paper?** | ~$0.13 (very cheap!) |
| **One API key or per-user?** | **ONE SHARED KEY** on backend only |
| **How to charge users?** | Track token usage in database → bill monthly per tier |
| **Where to store key?** | `.env` file (NEVER commit) |
| **How to prevent over-usage?** | Monthly quota check BEFORE API call |
| **Can frontend see key?** | NO. Keep it secret on backend. |
| **What happens if key leaks?** | Rotate it on OpenAI dashboard (5 min fix) |

---

## Token Economics

```
📊 VERY PROFITABLE

Cost to you (OpenAI):     $0.13 per paper
Your price (to users):    $50 per paper (Starter tier)
─────────────────────────────────────
Margin per paper:         $49.87 (99.7%)

At 1,000 papers/month:
  Revenue:  $50,000
  Cost:     $130
  Profit:   $49,870  ← This is beautiful!
```

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│  Your Backend Server (Python/FastAPI)                   │
│                                                         │
│  .env contains:                                         │
│  OPENAI_API_KEY=sk-proj-secret-key-here               │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │ OpenAIService Class                              │  │
│  │  - generate_questions(prompt, user_id, paper_id) │  │
│  │  - Calls OpenAI                                  │  │
│  │  - Logs usage to UsageLog table                  │  │
│  │  - Returns questions + token count              │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Database (PostgreSQL/Supabase)                   │  │
│  │                                                  │  │
│  │  users                                           │  │
│  │  ├─ id, email, subscription_tier                │  │
│  │                                                  │  │
│  │  usage_logs ← LOG EVERY API CALL HERE!           │  │
│  │  ├─ user_id                                      │  │
│  │  ├─ input_tokens, output_tokens                 │  │
│  │  ├─ cost_usd                                     │  │
│  │  ├─ resource_id (paper_id)                      │  │
│  │  └─ created_at                                   │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
              │
              ↓
         🔗 HTTPS ONLY 🔗
              │
              ↓
    ┌──────────────────────┐
    │  OpenAI API          │
    │  (chat.completions)  │
    │  Returns tokens used │
    └──────────────────────┘
```

---

## Pricing Tiers (Recommended)

```
TIER 1: Starter ($50/month)
├─ 50,000 input tokens
├─ 100,000 output tokens
└─ ~10-15 question papers

TIER 2: Professional ($150/month)
├─ 200,000 input tokens
├─ 500,000 output tokens
└─ ~50 question papers

TIER 3: Enterprise ($500/month)
├─ 1,000,000 input tokens
├─ 2,000,000 output tokens
└─ Unlimited (practical limit)
```

**Cost to you:**
- Tier 1: $13/month to OpenAI (margin = 99.7%)
- Tier 2: $65/month to OpenAI (margin = 99.6%)
- Tier 3: $260/month to OpenAI (margin = 99.5%)

---

## Implementation: 3-Step Setup

### Step 1️⃣: Create `.env` File

```bash
# Create this file in your project root
# .env (DO NOT COMMIT!)

OPENAI_API_KEY=sk-proj-your-actual-key-here
OPENAI_ORGANIZATION_ID=org-xxxxx  # optional
```

**Important:** Add to `.gitignore`:
```
.env
.env.local
*.env
```

### Step 2️⃣: Create Database Table

```sql
CREATE TABLE usage_logs (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR NOT NULL REFERENCES users(id),
    organization_id VARCHAR NOT NULL REFERENCES organizations(id),
    input_tokens INT DEFAULT 0,
    output_tokens INT DEFAULT 0,
    cost_usd FLOAT DEFAULT 0.0,
    resource_type VARCHAR,  -- "question_generation"
    resource_id VARCHAR,    -- paper_id
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_month ON usage_logs(user_id, created_at);
```

### Step 3️⃣: Write OpenAI Service

```python
from openai import OpenAI
from app.models.usage import UsageLog

class OpenAIService:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
    
    async def generate_questions(self, prompt, user_id, org_id, paper_id):
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000
        )
        
        # Log usage immediately
        usage = UsageLog(
            user_id=user_id,
            organization_id=org_id,
            input_tokens=response.usage.prompt_tokens,
            output_tokens=response.usage.completion_tokens,
            cost_usd=(
                response.usage.prompt_tokens * 0.15 / 1_000_000 +
                response.usage.completion_tokens * 0.60 / 1_000_000
            ),
            resource_type="question_generation",
            resource_id=paper_id
        )
        db.add(usage)
        db.commit()
        
        return response.choices[0].message.content
```

---

## Quota Enforcement (Prevent Over-Usage)

### Check BEFORE API Call

```python
async def check_quota(user_id, db):
    user = db.query(User).get(user_id)
    tier_limits = {
        "starter": 100_000,
        "pro": 700_000,
        "enterprise": 3_000_000
    }
    
    month_start = datetime.now().replace(day=1, hour=0, minute=0)
    used = db.query(func.sum(UsageLog.output_tokens)).filter(
        UsageLog.user_id == user_id,
        UsageLog.created_at >= month_start
    ).scalar() or 0
    
    if used >= tier_limits[user.tier]:
        raise QuotaExceededError("Monthly quota exceeded")
    
    return True

# In your API endpoint:
@app.post("/generate")
async def generate(req, user=Depends(auth)):
    await check_quota(user.id, db)  # ← Check FIRST
    result = openai_service.generate(req.prompt, user.id)  # ← Then call
    return result
```

---

## Monitoring & Alerts

### Dashboard Endpoint

```python
@app.get("/api/billing/status")
async def billing_status(user=Depends(auth)):
    month_start = datetime.now().replace(day=1, hour=0, minute=0)
    used = db.query(func.sum(UsageLog.output_tokens)).filter(
        UsageLog.user_id == user.id,
        UsageLog.created_at >= month_start
    ).scalar() or 0
    
    tier = user.subscription_tier
    limit = {"starter": 100_000, "pro": 700_000, "enterprise": 3_000_000}[tier]
    
    return {
        "tokens_used": used,
        "tokens_limit": limit,
        "percent_used": (used / limit) * 100,
        "papers_generated": db.query(Paper).filter(
            Paper.user_id == user.id,
            Paper.created_at >= month_start
        ).count()
    }
```

**Frontend shows:**
```
Your Usage (June 2024)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
75,500 / 100,000 tokens (75%)  ⚠️ Getting close!

Papers generated: 12

Next reset: July 1, 2024
```

---

## Common Mistakes & Fixes

| ❌ Mistake | 🔧 Fix | ✅ Result |
|-----------|--------|----------|
| Commit `.env` to git | Add to `.gitignore` | Key stays secret |
| Create per-user keys | Use 1 shared key | Centralized billing |
| No quota checking | Check before API call | Can't go over budget |
| Log sensitive data | Hash PII before logging | GDPR compliant |
| Ignore API errors | Add circuit breaker | Graceful degradation |
| No usage tracking | Log every call | Can bill accurately |

---

## Pricing Strategy Example

**You charge: Per Paper (Starter = $50/paper)**

```
Day 1: User generates 1 paper
  Your cost: $0.13
  Your revenue: $50
  ✓ Margin: 99.7%

Day 2: User generates 15 papers
  Your cost: $1.95
  Your revenue: $750
  ✓ Margin: 99.7%

Per month: 100 papers
  Your cost: $13
  Your revenue: $5,000
  ✓ VERY profitable
```

**OR charge: Subscription (Starter = $50/month)**

```
User's quota: 100,000 tokens (~20 papers)
  Your cost: $13
  Your revenue: $50
  
If user generates 1 paper: margin = 99.7%
If user generates 20 papers: margin = 99.7%
If user generates 0 papers: margin = 100%

✓ Predictable recurring revenue
```

Both models work. Subscription is more SaaS-like. Per-paper is pay-as-you-go.

---

## Quick Decision Tree

```
Q: Do I create a new API key for each user?
└─ NO. Use ONE shared key. Track usage in database.

Q: Where do I put my API key?
└─ In .env file (add to .gitignore).

Q: What if my key leaks?
└─ Go to OpenAI dashboard, rotate it (5 min).

Q: Should I use GPT-4 or GPT-4o-mini?
└─ Start with gpt-4o-mini. Charge users upgrade for gpt-4o.

Q: How do I make sure users don't bankrupt me?
└─ Check quota BEFORE every API call.

Q: How do I show users their usage?
└─ Query usage_logs table, divide by tier limit, show as %.

Q: Is this a cost center or profit center?
└─ PROFIT CENTER. You spend $0.13, charge $50. 99.7% margin!
```

---

## File Checklist

- [ ] `.env` file created with `OPENAI_API_KEY`
- [ ] `.env` added to `.gitignore`
- [ ] `UsageLog` table created in database
- [ ] `OpenAIService` class written
- [ ] `check_quota()` function before API calls
- [ ] Rate limiting added (`@limiter.limit("5/minute")`)
- [ ] `/api/billing/usage` endpoint built
- [ ] Daily spend alert set up
- [ ] Test with small prompt (verify logging works)
- [ ] Documentation for team

---

## Links

- **Create API Key:** https://platform.openai.com/api-keys
- **Pricing Calculator:** https://openai.com/pricing
- **FastAPI Rate Limiting:** https://github.com/laurenceisla/slowapi
- **Monitoring Best Practices:** https://openai.com/docs/guides/tokens/introduction

---

## Support

**Stuck?** Ask your engineer:

> "I need to set up OpenAI API integration. Can you help me:
> 1. Create the API key?
> 2. Set up the `.env` file?
> 3. Create `UsageLog` table?
> 4. Wrap the generation endpoint with quota checking?"
>
> Hand them this guide. Everything is here.

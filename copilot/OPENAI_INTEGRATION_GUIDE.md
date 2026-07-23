# OpenAI API Integration Guide for QuestionCraft

## 1. GETTING AN OPENAI API KEY

### Step 1: Create Account
- Go to https://platform.openai.com
- Sign up with email or Google/GitHub
- Verify email

### Step 2: Set Up Billing
 "Overview"
- Add payment method (credit card)
- Set monthly budget limits (e.g., $100/month) to prevent surprises
- Note: Free trial gives $5 credit (expires after 3 months)

### Step 3: Create API Keys
 "Create new secret key"
- Copy and store securely (only shown once!)
- Name it (e.g., "questioncraft-prod", "questioncraft-dev")
- You can create multiple keys (rotate periodically for security)

---

## 2. OPENAI PRICING STRUCTURE

### GPT-4.1 (or GPT-4o) Pricing (as of 2024):

**Input (per 1M tokens):** ~$5-10
**Output (per 1M tokens):** ~$15-30

Example for GPT-4o mini (cheaper):
- Input: $0.15 per 1M tokens
- Output: $0.60 per 1M tokens

### What is a "Token"?
- ~4 characters = 1 token (rough estimate)
-  1,500 tokenswords 
- For questions:  5,000-10,000 tokens outputquestions 

### Real-world Cost Example:
Generating 100 questions (GPT-4o):
- Input (prompt + context): ~2,000 tokens = $0.03
- Output (100 questions): ~8,000 tokens = $0.48
- **Total per paper: ~$0.50**

At 1000 papers/month:
- Cost: $500/month
- With pricing (Tier 1 = $50/paper): Revenue = $50,000
- **Margin: $49,500/ Very profitable!month** 

---

## 3. ARCHITECTURE: SHARED KEY vs PER-USER KEYS

### Option A: Shared API Key (RECOMMENDED FOR SAAS)
```

   Your Backend Server               
   (Single OpenAI API Key)           
                                     
  API_KEY = "sk-proj- Secret, stored in .envxxxx"  

           
    
                              
/opt/homebrew/bin/python3 /Users/rishikesh4089/Desktop/College/                   CC/blckchain.py
User BUser                    A
                   

Benefits:
 Single key to manage
 Easy to revoke if compromised
 Usage tracking per-user (in your database)
 Billing centralized (you pay OpenAI, users pay you)
 Better cost negotiation with OpenAI

Risks:
 If key leaked, attacker can use your quota
 Need strong rate limiting per user
```

### Option B: Per-User API Keys
```

   Your Backend Server               
                                     
 OpenAI           
 OpenAI           
 OpenAI           


Problems:
 Users pay OpenAI directly (complex)
 No revenue collection mechanism
 Support nightmare (billing disputes)
 Can't implement fair usage limits
 NOT recommended for SaaS
```

---

## 4. IMPLEMENTATION STRATEGY (RECOMMENDED)

### Step 1: Store API Key Securely
```python
# backend/app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str  # Load from environment
    openai_organization_id: str | None = None  # Optional
    
    class Config:
        env_file = ".env"

# .env (NOT committed to git)
OPENAI_API_KEY=sk-proj-your-key-here
OPENAI_ORGANIZATION_ID=org-xxxxx  # Optional, for cost center tracking
```

### Step 2: Track Usage Per User
```python
# backend/app/models/usage.py
from sqlalchemy import Column, String, Integer, DateTime
from datetime import datetime

class UsageLog(Base):
    __tablename__ = "usage_logs"
    
    id: int = Column(Integer, primary_key=True)
    user_id: str = Column(String, ForeignKey("users.id"))
    organization_id: str = Column(String, ForeignKey("organizations.id"))
    
    # Input and output tokens for billing
    input_tokens: int = Column(Integer, default=0)
    output_tokens: int = Column(Integer, default=0)
    
    # Cost calculation (for analytics)
    cost_usd: float = Column(Float, default=0.0)
    
    # What was used for
    resource_type: str = Column(String)  # "question_generation"
    resource_id: str = Column(String)    # paper_id
    
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
```

### Step 3: Wrapper Function for API Calls
```python
# backend/app/services/openai_service.py
from openai import OpenAI
from datetime import datetime

class OpenAIService:
    def __init__(self, config: Settings):
        self.client = OpenAI(api_key=config.openai_api_key)
        self.input_price = 0.005  # Per 1K tokens for GPT-4o mini
        self.output_price = 0.015
    
    async def generate_questions(
        self, 
        prompt: str, 
        user_id: str,
        organization_id: str,
        paper_id: str
    ) -> dict:
        """Generate questions and track usage"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # or "gpt-4.1" if available
                messages=[
                    {"role": "system", "content": "You are an expert question generator..."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # Extract usage
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            cost = (input_tokens * self.input_price + 
                   output_tokens * self.output_price) / 1000
            
            # Log usage for billing
            usage = UsageLog(
                user_id=user_id,
                organization_id=organization_id,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost_usd=cost,
                resource_type="question_generation",
                resource_id=paper_id,
                created_at=datetime.utcnow()
            )
            db.add(usage)
            db.commit()
            
            return {
                "content": response.choices[0].message.content,
                "tokens_used": input_tokens + output_tokens,
                "cost": cost
            }
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
```

---

## 5. TOKEN ALLOCATION TO USERS

### Strategy A: Monthly Quota (RECOMMENDED)
```
Tier 1 (Starter - $50/month)
 50,000 input tokens/month
 100,000 output tokens/month
 Can generate ~10-15 question papers

Tier 2 (Professional - $150/month)
 200,000 input tokens/month
 500,000 output tokens/month
 Can generate ~50-75 question papers

Tier 3 (Enterprise - $500/month)
 1,000,000 input tokens/month
 2,000,000 output tokens/month
 Unlimited (realistic limit)
```

Implementation:
```python
# Check before API call
async def validate_quota(user_id: str, org_id: str):
    user = db.query(User).filter(User.id == user_id).first()
    tier = user.subscription_tier  # "starter", "pro", "enterprise"
    
    # Get current month usage
    current_month_start = datetime.now().replace(day=1, hour=0, minute=0)
    usage = db.query(func.sum(UsageLog.output_tokens)).filter(
        UsageLog.user_id == user_id,
        UsageLog.created_at >= current_month_start
    ).scalar() or 0
    
    # Tier limits
    limits = {
        "starter": 100_000,      # total tokens
        "pro": 700_000,
        "enterprise": 3_000_000
    }
    
    if usage >= limits[tier]:
        raise QuotaExceededError(f"Quota exceeded. Used {usage}/{limits[tier]} tokens.")
    
    return True
```

### Strategy B: Credit-Based (Alternative)
```
1 Question Paper = 50 credits
1 Credit = $0.01

Starter = 500 credits ($5/month)
Professional = 2000 credits ($20/month)
Enterprise = Unlimited

User sees: "You have 487 credits remaining"
```

---

## 6. COST MANAGEMENT BEST PRACTICES

### Rate Limiting (Prevent Abuse)
```python
# Add to FastAPI middleware
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/generate-paper")
@limiter.limit("5/minute")  # Max 5 papers per minute per user
async def generate_paper(request: Request):
    pass
```

### Caching (Reduce API Calls)
```python
# Cache embeddings for 30 days
 reuse cached embeddings
@cache.cached(timeout=30*24*3600, key_prefix="embeddings_")
async def get_embedding(text: str):
    response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding
```

### Cost Monitoring
```python
# Daily alert if over budget
async def check_daily_spend():
    today = datetime.now().date()
    daily_cost = db.query(func.sum(UsageLog.cost_usd)).filter(
        func.date(UsageLog.created_at) == today
    ).scalar() or 0
    
    if daily_cost > 50:  # Alert if over $50/day
        send_email("cost-alert", f"Today's spend: ${daily_cost:.2f}")
```

---

## 7. WHAT NOT TO DO

 Store API key in frontend (it WILL leak)
 Create per-user API keys (complexity + cost)
 Commit .env file to git
 Use free tier in production (unstable)
 Allow unlimited token usage
 Log full prompts with PII (privacy risk)

---

## 8. QUICK START CHECKLIST

- [ ] Sign up at https://platform.openai.com
- [ ] Add payment method
- [ ] Create API key
- [ ] Store in .env (add to .gitignore!)
- [ ] Create UsageLog table in database
- [ ] Wrap OpenAI calls with token tracking
- [ ] Implement monthly quota per tier
- [ ] Add rate limiting middleware
- [ ] Set up cost alerts
- [ ] Test with small quota ($5/day limit initially)


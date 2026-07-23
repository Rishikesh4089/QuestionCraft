# QuestionCraft: Executive Summary for SaaS Transformation

**Date:** June 7, 2026  
**Status:** ⚠️ MVP Ready → Production SaaS Transformation Required  
**Estimated Timeline:** 12 weeks | **Budget:** $550K | **Team:** 18 FTE at scale

---

## 🎯 The Opportunity

QuestionCraft is a **high-potential SaaS** positioned in a **$5M+ addressable market**:

- 25,000 universities, 40,000 colleges, 100,000+ coaching institutes globally
- **Pain point:** Question paper generation takes professors 10+ hours per exam
- **Solution:** AI-powered automated generation with learning outcomes alignment
- **Unique advantage:** Only product combining RAG + Bloom's taxonomy in market
- **TAM:** $50M+ (if penetrate 1% of higher ed globally)

**Comparable Companies:**
- Gradescope (assessment grading) — $1.5B acquisition
- Canvas LMS (learning management) — $11B market
- Google Classroom (free tier) — distribution channel only
- ExamSoft (proctoring) — $500M+ valuation

---

## 📊 Current State Assessment

### What Works ✅
- **Core algorithm:** RAG + LLM generation produces credible questions
- **Tech stack:** Modern, scalable (FastAPI, React, FAISS, OpenAI)
- **UX:** Clean Tailwind UI, multi-step wizard
- **Performance:** Generates 10-question paper in 60 seconds
- **Architecture:** Modular, well-separated concerns

### What's Broken ❌
| Area | Status | Impact | Severity |
|------|--------|--------|----------|
| **Authentication** | None | Anyone can access API | 🔴 CRITICAL |
| **Database** | None | No persistent storage, data loss on restart | 🔴 CRITICAL |
| **Authorization** | None | No permission checks, single-user | 🔴 CRITICAL |
| **Multi-tenancy** | None | Can't separate institutions | 🔴 CRITICAL |
| **Audit logs** | None | GDPR/FERPA non-compliant | 🔴 CRITICAL |
| **Monitoring** | None | No error tracking, can't debug production | 🟠 HIGH |
| **Testing** | None | 0% unit/integration test coverage | 🟠 HIGH |
| **Deployment** | Manual | No Docker, no CI/CD | 🟠 HIGH |

**SaaS Readiness Score: 2.8/10** (Research-grade prototype)

---

## 💡 12-Week Transformation Plan

### Week 1-2: Emergency Hardening 🚨
**Goal:** Make product secure enough to require login

- [ ] Supabase Auth integration (sign up, login, logout)
- [ ] Database: users, papers, audit_logs tables
- [ ] JWT middleware on all API endpoints
- [ ] HTTPS enforcement + rate limiting (10 req/min)
- [ ] File upload validation (type, size, malware scan)
- [ ] Error tracking (Sentry)

**Cost:** $20K | **Risk:** Low

### Week 3-6: Enterprise MVP 🏢
**Goal:** Multi-tenant, RBAC, compliant

- [ ] Multi-tenancy (org isolation, row-level security)
- [ ] RBAC (Student, Teacher, Admin, Dept Head roles)
- [ ] SSO setup (SAML placeholder, Google OAuth)
- [ ] Paper versioning + history
- [ ] Unit tests (50% coverage)
- [ ] Docker + CI/CD pipeline

**Cost:** $150K | **Revenue enabled:** $0 (closed beta)

### Week 7-12: Revenue Ready 💰
**Goal:** Enterprise features, go-to-market

- [ ] LMS integrations (Canvas, Moodle)
- [ ] Plagiarism detection
- [ ] Exam analytics (difficulty, discrimination index)
- [ ] Question review workflow
- [ ] Billing/Stripe integration
- [ ] Public launch

**Cost:** $300K | **Revenue:** $250K-500K (Year 1)

---

## 🎯 Business Model Recommendation

### Hybrid Licensing + Usage-Based
```
INSTITUTION LICENSE (Recommended)
├─ $5K-20K/year (based on faculty count)
├─ Includes: up to 100 users, unlimited papers, SSO, integrations
└─ Target: Mid-tier universities (500-5000 faculty)

INDIVIDUAL/SMB (Coaching Institutes)
├─ Freemium: 2 papers/month free
├─ Pro: $150/year (unlimited papers, all features)
└─ Target: Teaching coaches, online education

ENTERPRISE (500+ institutions)
├─ Custom pricing ($50K+/year)
├─ Includes: white-label, dedicated support, custom integrations
└─ Target: Large universities, government education ministries
```

### Revenue Projections
| Year | Institutions | Individuals | Total Revenue |
|------|---|---|---|
| Year 1 | 25 | 300 | $250K |
| Year 2 | 100 | 1,500 | $1.2M |
| Year 3 | 250 | 5,000 | $3.5M |

**Break-even:** Month 18 | **Target:** $1M ARR by Month 24

---

## 🏆 Competitive Position

| Feature | QuestionCraft | Canvas | Moodle | Gradescope | ExamSoft |
|---------|---|---|---|---|---|
| **AI Question Generation** | ✅ YES | ❌ No | ❌ No | ❌ No | ❌ No |
| **Learning Outcomes Alignment** | ✅ YES | ⚠️ Basic | ⚠️ Basic | ❌ No | ❌ No |
| **LMS Integration** | 🚧 Building | ✅ Native | ✅ Native | ✅ Yes | ✅ Yes |
| **Exam Grading** | ❌ No | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Market Share** | NEW | 23% | 13% | Growing | 15% law schools |

**Positioning:** *"The AI tutor for exam creation — save 10+ hours per exam with questions that automatically align to learning outcomes."*

---

## 🚀 Go-to-Market Strategy

### Segment 1: Coaching Institutes (India) — HIGHEST ROI
- **TAM:** 10,000 institutes × $20/month = $2.4M/year
- **Sales cycle:** 2-4 weeks
- **Pitch:** "10x faster exams, consistent quality"
- **Channels:** Direct outreach, demo days, content marketing
- **Timeline:** Start Month 2, target 50 by Month 6

### Segment 2: Mid-Tier Universities (US/UK/India)
- **TAM:** 500 institutions × $10K/year = $5M/year
- **Sales cycle:** 6-12 months (procurement process)
- **Pitch:** "Pass accreditation audits with AI-generated papers"
- **Channels:** Higher ed conferences, inbound, partnerships
- **Timeline:** Start Month 6, target 50 by Month 12

### Segment 3: Enterprise Universities (50+ faculty)
- **TAM:** 100 institutions × $40K/year = $4M/year
- **Sales cycle:** 12-18 months (RFP process)
- **Pitch:** "Institutional compliance + faculty productivity"
- **Channels:** Consulting partnerships, CAO networks, RFP responses
- **Timeline:** Start Month 9, target 10-20 by Month 24

### Segment 4: LMS Partnerships (Long-term)
- **Partners:** Canvas, Moodle, Blackboard
- **Revenue:** 10-20% of SaaS revenue or per-question fees
- **Timeline:** 12+ months to negotiate, 6+ months to integrate
- **Benefit:** Distribution at scale

---

## ⚠️ Critical Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|-----------|
| **Supabase Auth fails** | Blocks launch | 5% | Fallback: Firebase Auth (same API) |
| **OpenAI API changes pricing** | Cost increases 3-5x | 20% | Add Claude API alternative, local embeddings option |
| **LMS integrations complex** | 2+ weeks per LMS | 80% | Pre-build Canvas/Moodle, test with sandbox accounts |
| **Enterprise sales cycle long** | Revenue delayed | 100% | Focus on SMB first, get quick wins |
| **Competitor launches similar** | Price/feature war | 30% | Move fast in Months 1-6, focus on Bloom's + outcomes differentiation |
| **Scaling issues discovered** | Latency increases | 40% | Add Redis caching, FAISS partitioning from start |

---

## 👥 Team Requirements

### Core Team (Immediate)
- **Backend Engineer (1.5 FTE):** Auth, DB, multi-tenancy, API
- **Frontend Engineer (1 FTE):** Auth UI, dashboard, integrations
- **Product Manager (0.5 FTE):** Requirements, prioritization
- **DevOps (0.5 FTE):** Docker, CI/CD, monitoring

**Ramp to full team:**
- Month 2: +QA engineer (testing, load tests)
- Month 3: +Sales engineer (technical due diligence)
- Month 4: +Solutions architect (LMS integrations)
- Month 6: +Data scientist (analytics, ML difficulty prediction)

**Full team by Month 12:** 18 FTE (4 eng, 3 sales, 2 support, 1 marketing, 1 product, operations)

---

## 💰 Investment Summary

### Total 12-Month Budget: $550K

| Category | Cost |
|----------|------|
| **Payroll (core team)** | $300K |
| **Infrastructure & Tools** | $80K (Supabase, OpenAI, Cohere, AWS, monitoring) |
| **Security (audit, penetration testing)** | $50K |
| **Go-to-market (landing page, content, ads)** | $80K |
| **Contingency (10%)** | $40K |
| **Total** | **$550K** |

### ROI Timeline
- **Month 1-6:** Revenue $0, cumulative spend $275K
- **Month 7-12:** Revenue $250K-500K, cumulative spend $550K
- **Break-even:** Month 18
- **Year 2 ARR:** $1.2M (4x ROI on $550K investment)
- **Year 3 ARR:** $3.5M (6.4x ROI)

---

## 📋 Next Steps (This Week)

### Day 1-2: Approval & Planning
- [ ] Review this audit with founders
- [ ] Approve 12-week roadmap
- [ ] Allocate budget ($550K)

### Day 3-5: Execution Start
- [ ] Setup Supabase project + database schema
- [ ] Create backend user authentication branch
- [ ] Setup GitHub Actions for CI/CD
- [ ] Deploy to staging environment

### Week 1 Review
- [ ] Authentication working (sign up, login, logout)
- [ ] Database populated (users, papers)
- [ ] Deploy to production (staging environment)
- [ ] Test with 10 beta users

---

## ✅ Success Criteria

### By End of Month 1
- ✅ Staging deployment with auth
- ✅ 20 beta testers signed up
- ✅ Zero security vulnerabilities (pen test passed)
- ✅ SaaS readiness score ≥ 6/10

### By End of Month 6 (Go-to-Market)
- ✅ Multi-tenancy working for 50+ institutions
- ✅ Canvas integration live
- ✅ $100K ARR from pilot customers
- ✅ 10+ case studies from beta users
- ✅ SaaS readiness score ≥ 8/10

### By End of Year 1
- ✅ 250+ paid customers
- ✅ $500K-1M ARR
- ✅ 5+ LMS integrations
- ✅ <2% monthly churn
- ✅ NPS >40

---

## 🎓 Conclusion

**QuestionCraft has exceptional core technology** (RAG + LLM question generation) **positioned in a $5M+ addressable market with zero direct competitors**. 

The path to $1M ARR is clear:
1. **Harden infrastructure** (Weeks 1-2)
2. **Build enterprise features** (Weeks 3-6)
3. **Launch to market** (Weeks 7-12)
4. **Execute go-to-market** (Months 4-12)

**Recommended decision:** APPROVED for $550K investment, 12-month transformation, Target: $1M ARR by Month 24.

---

**Full audit report:** See QUESTIONCRAFT_SAAS_AUDIT.md (71 KB, comprehensive)

**Questions?** Schedule review meeting with founders, investors, and technical leadership.

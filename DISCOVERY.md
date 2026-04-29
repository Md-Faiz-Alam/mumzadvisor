# DISCOVERY.md
## Mumzworld Live Chat — AI Gap Analysis
**Track A | AI Engineering Intern | Mumzworld**
**5 Test Conversations | 2 Languages | 3 Agents | Conducted April 2026**

---

## Persona Definition

To test the current support system, I acted as 5 different real Mumzworld customer personas — ranging from Arabic-speaking gift buyers to panicking working moms — each with a specific, high-intent product query. All tests were conducted on the live Mumzworld chat widget within a 24-hour window.

Each persona was chosen to represent a real, high-frequency customer type on Mumzworld:
- A gift buyer who needs a curated recommendation
- A first-time pregnant mom overwhelmed by what she needs
- A working mom comparing two specific products
- A mom managing a baby with sensitive skin and a tight budget
- A panicking mom with a 3-day deadline and a medical context

---

## Test 1 — Layla | Arabic | Gift Finder

**Query:**
> *"أحتاج هدية لصديقتي عندها طفل عمره 6 أشهر، الميزانية 200 درهم"*
> *(I need a gift for my friend who has a 6-month-old baby, budget 200 AED)*

**Agent:** Hager

**What happened:**

The query contained everything needed to return a recommendation immediately — recipient, age, budget, and occasion. Instead, the agent asked 4 sequential clarifying questions before providing any product:

1. Is there a specific category you have in mind?
2. Is the baby a boy?
3. Are you based in the UAE?
4. *(Then finally)* Sent a generic category page link

**What was delivered:**
`mumzworld.com/ar/collections/toys-age-6-to-12-months` — a collection page with hundreds of products, plus a gift card suggestion as a fallback.

| Metric | Result |
|--------|--------|
| Time to first product | 13 minutes |
| Specific products shown | 0 |
| Budget respected | No |
| Arabic quality | Functional but generic |

**Failure type:** Complete failure — the customer still has to browse hundreds of products herself with no guidance.

**Critical insight:** The gift card suggestion is a system admitting it cannot recommend. When an e-commerce platform's answer to "what should I buy?" is "here's money, you figure it out" — that is a product gap worth solving.

---

## Test 2 — Hana | English | Pregnancy Essentials

**Query:**
> *"I'm 8 months pregnant, first time mom, budget is 300 AED, what do I absolutely need before baby arrives?"*

**Agent:** Hager

**What happened:**

This is the highest-value customer persona on the entire Mumzworld platform — a first-time mom about to make her first major purchasing decisions. The agent asked one clarifying question ("Are you looking for specific items for you and your baby?"), went silent for 2+ minutes, then delivered a single link.

**What was delivered:**
`mumzworld.com/en/collections/essentials?utm_source=chatgpt.com`

| Metric | Result |
|--------|--------|
| Time to first product | 8 minutes |
| Specific products shown | 0 |
| Budget respected | No — 300 AED completely ignored |
| Critical finding | UTM parameter reveals agent used ChatGPT externally |

**Failure type:** Complete failure — and the most damning evidence in the entire test set.

**Critical insight:** The UTM parameter `?utm_source=chatgpt.com` reveals the agent used ChatGPT externally to find this link. Mumzworld agents have no internal AI product tool and are improvising with external AI to answer customer queries. The company has inadvertently proven the solution works — it just hasn't been built natively into the platform. This is not a question of whether AI can solve this. It already is. It's just happening outside Mumzworld's walls, untracked and unoptimized.

---

## Test 3 — Dina | English | Product Comparison

**Query:**
> *"Is the Philips Avent breast pump better than Momcozy for a working mom who travels?"*

**Agent:** Moustafa

**What happened:**

This was the first test where the agent retrieved specific product information. Moustafa sent direct product links for both pumps and listed feature bullets for each. On the surface this looks like a success.

**What was delivered:**
- 2 direct product links ✅
- Feature bullet lists for both products ✅
- A comparison structure ✅

**What was missing:**
- No prices mentioned anywhere
- No final recommendation — ended with "both are suitable"
- Features read like spec sheet copy-paste, not mom-friendly reasoning
- Never answered the actual question: *which is better for a working mom who travels?*

| Metric | Result |
|--------|--------|
| Time to response | 6 minutes |
| Specific products shown | 2 ✅ |
| Verdict given | No ❌ |
| Reasoning provided | No ❌ |

**Failure type:** Partial failure — data retrieved, decision not made.

**Critical insight:** This is the most common failure mode in human-assisted commerce. Agents can find products but cannot make the final inferential leap from "here are the features" to "here is what you should buy and why." That last step — confident, reasoned recommendation — is exactly what AI does well and humans under time pressure consistently skip.

---

## Test 4 — Rania | English | Multi-Product Sensitive Skin

**Query:**
> *"My baby is 4 months old and has really sensitive skin, she gets rashes easily. I need a complete bath routine — soap, cream, and maybe a baby tub. My budget is 250 AED total. What do you recommend?"*

**Agent:** Hager

**What happened:**

This was the most deceptive response in the entire test set. On reading it, it feels helpful — warm tone, empathetic language, 4 product categories covered, sensitive skin acknowledged. A real mom would likely give it 5 stars without realizing she received nothing actionable.

**What was delivered:**
- 4 category page links (body wash, lotion, diaper rash cream, baby tubs)
- Empathetic copy about sensitive skin
- A recommendation to look for "fragrance-free, hypoallergenic" products

**What was missing:**
- Zero specific products — every link leads to hundreds of items
- Zero prices — no indication if 250 AED covers all 4 items
- Zero budget allocation — how much to spend on each item?
- Sensitive skin filter not applied — category pages include products with fragrance
- Diaper rash cream added to scope without budget reallocation discussion

| Metric | Result |
|--------|--------|
| Time to response | 6 minutes |
| Specific products shown | 0 ❌ |
| Budget allocation provided | No ❌ |
| Medical context acted on | No ❌ |

**Failure type:** Partial failure — the most dangerous type because it feels like success.

**Critical insight:** This response required: a budget split across 4 items, a filter for sensitive skin, specific product selection within each filtered category, and a price check that the total comes in under 250 AED. A human doing this manually in a chat window under time pressure will always default to category pages. An AI with structured output and a product catalog does this in one pass.

---

## Test 5 — Sara | English | Urgent Sippy Cup Transition

**Query:**
> *"My 9 month old just started refusing the bottle completely, my pediatrician said to transition to a sippy cup but I have no idea where to start. I'm going back to work in 3 days and I'm panicking. What's the fastest solution under 100 AED?"*

**Agent:** Moustafa

**What happened:**

This was the strongest human agent performance across all tests. Moustafa skipped clarifying questions, went directly to product search, and returned 4 named product links within 4 minutes. This is the closest the current system gets to good.

**What was delivered:**
- 4 direct product links ✅
- Real named products: Beaba, Trixie, Tum Tum ✅
- No clarifying questions ✅

**What was missing:**
- Zero prices — is any of these under 100 AED? Unknown
- Zero urgency handling — "3 days, panicking" completely unaddressed
- No delivery time mentioned — the most critical factor given the time constraint
- No reasoning — why these 4? Which one is best for a bottle-refusing baby?
- No cup type guidance — straw vs soft spout vs hard spout matters clinically for this transition

| Metric | Result |
|--------|--------|
| Time to first product | 4 minutes |
| Specific products shown | 4 ✅ |
| Urgency addressed | No ❌ |
| Price check against budget | No ❌ |
| Reasoning provided | No ❌ |

**Failure type:** Best attempt — still incomplete on every dimension that actually drives the purchase decision.

**Critical insight:** Even the best human response in this test set failed to address urgency, price, and reasoning simultaneously. These three things together — in one response, in under 3 seconds — is the exact gap the AI advisor fills.

---

## Aggregate Analysis

| Test | Persona | Language | Specific Products | Price Shown | Budget Respected | Reasoning | Urgency Handled | Failure Type |
|------|---------|----------|:-----------------:|:-----------:|:----------------:|:---------:|:---------------:|-------------|
| 2 | Layla | Arabic | ❌ | ❌ | ❌ | ❌ | ❌ | Complete |
| 3 | Hana | English | ❌ | ❌ | ❌ | ❌ | ❌ | Complete + ChatGPT proof |
| 4 | Dina | English | ✅ | ❌ | ❌ | ❌ | ❌ | Partial — no verdict |
| 5 | Rania | English | ❌ | ❌ | ❌ | ❌ | ❌ | Deceptive partial |
| 6 | Sara | English | ✅ | ❌ | ❌ | ❌ | ❌ | Best attempt |

**Score: 0 out of 5 conversations delivered a specific product recommendation with price, reasoning, and budget respect — simultaneously.**

---

## Two Failure Modes Identified

**Mode 1 — Complete Failure (Tests 2, 3)**
No product intelligence at all. Agent escalates, asks multiple clarifying questions, and delivers a generic category page link or an external ChatGPT-sourced URL. Customer still has to do all the work.

**Mode 2 — Partial Failure (Tests 4, 5, 6)**
Agent retrieves some product data but fails to make the final recommendation. Either lists features without a verdict, sends category pages instead of products, or ignores the budget and urgency entirely. Feels helpful on the surface. Isn't.

---

## The Single Finding

**Across 5 conversations, 2 languages, and 3 different agents, not one response simultaneously provided: a specific product recommendation, with a price, within the stated budget, with reasoning, in under 60 seconds.**

This is not a training problem. It is a tooling problem. Agents lack an AI layer that can do in one pass what takes a human 4–13 minutes and still delivers incompletely.

The proof that AI solves this already exists in the data: Test 3 shows an agent used ChatGPT externally to answer a product query. The solution works. It just has not been built into the platform.

---

## Why AI — Not a UX Fix

This is not a button problem. Adding more filters to the category pages does not solve it. Making the search bar smarter does not solve it. The problem is that a mom with a specific context — age, budget, medical constraint, urgency — needs a reasoned, personalized recommendation that weighs multiple variables simultaneously. That is an inference problem. Inference is what AI does.

A UX fix helps a mom who knows what she wants find it faster. This solves for the mom who does not know what she wants and needs a trusted advisor to tell her. That is the majority of Mumzworld's highest-value customers.

---

## The Problem Worth Solving

A Mumzworld AI Product Advisor that:
- Takes a natural language query in English or Arabic
- Extracts intent, budget, age context, and medical constraints
- Retrieves relevant products from the catalog using RAG
- Allocates budget across multi-item requests
- Flags impossible constraints honestly rather than ignoring them
- Returns a ranked shortlist with reasoning and confidence scores
- Delivers everything in a single response, in the customer's language, in under 3 seconds

That is what this prototype builds.
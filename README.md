# MumzAdvisor 🍼
**AI-powered product recommendation advisor for Mumzworld**
*Natural language → specific, priced, reasoned product recommendations in English and Arabic*

---

> **Track A — AI Engineering Intern Assessment | Mumzworld | April 2026**

---

## One-Paragraph Summary

MumzAdvisor is a bilingual AI product advisor that converts natural language queries into structured, budget-aware product recommendations for Mumzworld — the largest mother and baby e-commerce platform in the Middle East. A mom types her situation in English or Arabic ("I need a gift for my friend's 6-month-old, budget 200 AED") and receives a ranked shortlist of specific products with prices, reasoning, and budget allocation — in under 30 seconds, in her language. The system handles medical constraints (lactose-free formula, sensitive skin), urgency detection, impossible budget flagging, and explicit refusals for out-of-scope queries. It was built to close a specific, documented gap: across 6 live Mumzworld customer support conversations, not one human agent delivered a specific product recommendation with a price, within budget, with reasoning, in under 60 seconds.

---

## Table of Contents

1. [The Problem](#the-problem)
2. [Quick Start](#quick-start)
3. [Project Structure](#project-structure)
4. [Architecture](#architecture)
5. [AI Stack and Tooling](#ai-stack-and-tooling)
6. [Features](#features)
7. [Example Outputs](#example-outputs)
8. [Evals](#evals)
9. [Tradeoffs](#tradeoffs)
10. [Time Log](#time-log)
11. [AI Usage Note](#ai-usage-note)

---

## The Problem

Before writing a single line of code, I tested Mumzworld's live customer support chat across 5 conversations, 2 languages, and 3 different human agents. The finding was consistent:

| Test | Query | Products Shown | Budget Respected | Reasoning | Time |
|------|-------|:--------------:|:----------------:|:---------:|------|
| Layla (AR) | Gift, 6mo baby, 200 AED | ❌ Category page | ❌ | ❌ | 13 min |
| Hana (EN) | Pregnant, 300 AED essentials | ❌ ChatGPT link* | ❌ | ❌ | 8 min |
| Dina (EN) | Breast pump comparison | ✅ 2 links | ❌ | ❌ No verdict | 6 min |
| Rania (EN) | Sensitive skin, 250 AED | ❌ Category pages | ❌ | ❌ | 6 min |
| Sara (EN) | Sippy cup urgent, 100 AED | ✅ 4 links | ❌ | ❌ | 4 min |

*The agent sent a URL with `?utm_source=chatgpt.com` — agents are already using external AI to answer product queries. The solution works. It just hasn't been built natively.

**In 5 conversations, 2 languages, 3 agents — not one response simultaneously provided a specific product with a price, within budget, with reasoning.**

Full discovery documentation: [`DISCOVERY.md`](DISCOVERY.md)

---

## Quick Start

### Requirements

- Python 3.10+
- OpenRouter API key (free at [openrouter.ai](https://openrouter.ai))
- ~2 minutes to set up

### Setup

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/mumzadvisor.git
cd mumzadvisor

# 2. Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your API key
# Create a .env file in the root directory:
echo "OPENROUTER_API_KEY=sk-or-v1-your-key-here" > .env
```

### Run the App

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`

### Run the Evals

```bash
python -m evals.evals
```

Expected output: 11/12 passing (92%). See [EVALS.md](EVALS.md) for full results and failure analysis.

---

## Project Structure

```
mumzadvisor/
│
├── data/
│   └── products.json              ← 500 synthetic products across 12 categories
│
├── discovery/
│   ├── test2_layla_ar_gift.mp4    ← Arabic gift finder conversation recording
│   ├── test3_hana_en_pregnant.mp4 ← Pregnancy essentials conversation recording
│   ├── test4_dina_en_breastpump.mp4
│   ├── test5_rania_en_skin.mp4    ← Sensitive skin multi-product recording
│   ├── test6_sara_en_sippy.mp4    ← Urgent sippy cup recording
│   └── DISCOVERY.md               ← Full gap analysis with evidence
│
├── prompts/
│   └── system_prompt.txt          ← System prompt (EN + AR instructions)
│
├── src/
│   ├── schema.py                  ← Pydantic output schema + validation
│   ├── advisor.py                 ← Core AI agent (OpenRouter API call)
│   └── prompts.py                 ← Prompt loader and formatter
│
├── evals/
│   ├── evals.py                   ← 12 test cases with scoring + benchmark
│   └── eval_results.json          ← Last run results (auto-generated)
│
├── app.py                         ← Streamlit UI
├── requirements.txt
├── .env                           ← API key (not committed)
├── .gitignore
├── README.md                      ← This file
├── EVALS.md                       ← Full evaluation report
├── TRADEOFFS.md                   ← Architecture decisions and tradeoffs
└── DISCOVERY.md                   ← Live chat gap analysis
```

---

## Architecture

```
User Query (English or Arabic)
            │
            ▼
┌─────────────────────────┐
│   Intent Extraction     │  Detects: language, age, budget,
│   (system prompt)       │  urgency, medical context, category
└─────────────────────────┘
            │
            ▼
┌─────────────────────────┐
│   Catalog Filter        │  Keyword + tag scoring over 500 products
│   (src/advisor.py)      │  Returns top 8–25 relevant products
└─────────────────────────┘
            │
            ▼
┌─────────────────────────┐
│   LLM Reasoning         │  OpenRouter → Llama 3.3 70B
│   (OpenRouter API)      │  Structured JSON output
└─────────────────────────┘
            │
            ▼
┌─────────────────────────┐
│   Schema Validation     │  Pydantic — validates budget,
│   (src/schema.py)       │  refusals, fit scores, Arabic fields
└─────────────────────────┘
            │
            ▼
┌─────────────────────────┐
│   Retry if Invalid      │  Max 2 attempts on parse/validation fail
│                         │  100% reliability in eval suite
└─────────────────────────┘
            │
            ▼
┌─────────────────────────┐
│   Streamlit UI          │  Renders recommendations, budget
│   (app.py)              │  breakdown, confidence, bilingual output
└─────────────────────────┘
```

### Three Valid Response Types

The schema recognises three valid response types — not just success/fail:

**Type 1 — Recommendation response**
Normal path. Returns ranked products with prices, reasoning in EN and AR, budget allocation, confidence score.

**Type 2 — Explicit refusal**
Out-of-scope queries (laptops, weather), gibberish input, or requests for medical diagnosis. Returns `refused=True` with explanation in both languages.

**Type 3 — Impossible budget**
When the requested items cannot fit within the stated budget. Returns `budget_feasible=False` with the minimum available price. Does not invent cheaper products that don't exist.

---

## AI Stack and Tooling

### Models

| Model | Used For |
|-------|---------|
| `meta-llama/llama-3.3-70b-instruct:free` | Primary recommendation engine, Arabic output |

### Infrastructure

| Tool | Role |
|------|------|
| [OpenRouter](https://openrouter.ai) | Free model gateway — unified API for Llama 3.3 70B |
| Pydantic v2 | Output schema validation |
| Streamlit | Prototype UI |
| Python-dotenv | API key management |

### Why Llama 3.3 70B

Tested against DeepSeek V3 and Qwen 2.5 72B on the free tier. Llama 3.3 70B showed the best combination of structured JSON reliability and Arabic output quality. On a paid endpoint (GPT-4o-mini or Claude 3 Haiku), average latency would drop from ~24s to ~3–5s.

### How AI Was Used in Development

- **Claude (claude.ai):** Problem framing, system prompt design, Arabic copy review, schema design, eval rubric, TRADEOFFS.md and EVALS.md drafting
- **GPT-4o:** Code generation for retrieval pipeline, Pydantic schema drafting, Streamlit UI layout
- **Llama 3.3 70B (via OpenRouter):** The model that runs inside the product itself
- **Manual work:** All architectural decisions, system prompt iteration, test case design, eval scoring logic, Arabic quality review

Full tooling transparency in [TRADEOFFS.md](TRADEOFFS.md).

---

## Features

### Core
- Natural language query in English or Arabic
- Retrieves from 500-product synthetic catalog across 12 categories
- Returns 2–4 specific products with names, prices, fit scores, and reasoning
- Budget allocation across multi-item requests
- `budget_feasible` flag with honest messaging when budget is impossible

### Safety and Uncertainty
- Medical disclaimer on formula/allergy queries — recommends consulting a pediatrician
- Sensitive skin filter — only recommends `sensitive_skin_safe` products for sensitive skin queries
- Lactose-free filter — only recommends `lactose_free` products for intolerance queries
- Out-of-scope refusal — laptops, weather, gibberish all refused with explanation
- Impossible budget handling — names the minimum available price instead of hallucinating

### Multilingual
- Auto-detects English or Arabic input
- Returns both `reason` (EN) and `reason_ar` (AR) on every recommendation
- Arabic written independently — not translated from English
- System prompt includes native Arabic quality examples to prevent machine-translation patterns

### Evals
- 12 test cases derived from real Mumzworld chat conversations
- Automated scoring across 5 dimensions: refusal, language, budget, grounding, custom
- Latency benchmarking with P50, P95, fastest, slowest
- 92% pass rate (11/12), 100% reliability (no retries needed)

---

## Example Outputs

### English — Urgent Sippy Cup (T01)
**Query:** "My 9 month old just started refusing the bottle. Going back to work in 3 days, panicking. Under 100 AED."

**Response:**
```json
{
  "urgency_detected": true,
  "urgency_note": "3-day deadline detected. All recommendations are in-stock 
                   and available for next-day delivery in UAE.",
  "recommendations": [
    {
      "product_name": "Tum Tum Tippy Up Straw Cup 300ml",
      "price_aed": 55.0,
      "reason": "Straw cups most closely mimic bottle mechanics — best choice 
                 for a bottle-refusing 9-month-old per pediatric guidance.",
      "fit_score": 0.95
    }
  ],
  "total_budget_aed": 100.0,
  "total_cost_aed": 55.0,
  "budget_feasible": true,
  "confidence": "high"
}
```

---

### Arabic — Gift Finder (T02)
**Query:** أحتاج هدية لصديقتي عندها طفل عمره 6 أشهر، الميزانية 200 درهم

**Response:**
```json
{
  "language": "ar",
  "recommendations": [
    {
      "product_name": "Sophie la Girafe Classic Teether",
      "product_name_ar": "عضاضة صوفي لا جيراف الكلاسيكية",
      "price_aed": 89.0,
      "reason_ar": "صوفي كلاسيكية — كل أم في المنطقة تعرفها وتحبها، 
                    وآمنة تماماً للبيبي في هالمرحلة وهدية تفرح فيها الأم",
      "fit_score": 0.97
    }
  ],
  "total_budget_aed": 200.0,
  "total_cost_aed": 89.0,
  "budget_feasible": true,
  "confidence": "high"
}
```

---

### Impossible Budget — Honest Refusal (T08)
**Query:** "I need a double stroller for twins under 200 AED"

**Response:**
```json
{
  "refused": true,
  "budget_feasible": false,
  "recommendations": [],
  "refusal_reason": "No double stroller in our catalog fits within 200 AED. 
                     The most affordable option is the Neobreez Duadx 
                     Double Twin Stroller at 499 AED.",
  "refusal_reason_ar": "لا توجد عربة توأم في كتالوجنا بأقل من 200 درهم. 
                         أرخص خيار متاح هو عربة نيوبريز دوادكس بسعر 499 درهم.",
  "confidence": "low"
}
```

---

## Evals

Full evaluation report: [`EVALS.md`](EVALS.md)

```
Passed:        11 / 12  (92%)
Failed:         1 / 12
Reliability:      100%  (no retries needed in any test)

Avg Latency:    24.21s
Median (P50):   22.85s
P95:            55.84s
Fastest:         4.38s  (out-of-scope refusal)
Slowest:        55.84s  (pregnancy essentials, large catalog slice)
```

### The One Failure — T08

T08 (double stroller under 200 AED) fails the eval refusal check. The model produced the correct behavior — `budget_feasible=False`, empty recommendations, clear refusal reason citing the 499 AED minimum. The failure is in the eval assertion logic, which was not updated after the schema was changed to accept impossible-budget responses as a third valid response type. This is documented honestly rather than fixed silently. See [EVALS.md](EVALS.md) for full root cause analysis.

### Test Coverage

| ID | Test | Type | Status |
|----|------|------|--------|
| T01 | Urgent sippy cup, 100 AED | Real conversation | ✅ |
| T02 | Arabic gift finder, 200 AED | Real conversation | ✅ |
| T03 | Sensitive skin multi-product, 250 AED | Real conversation | ✅ |
| T04 | Breast pump comparison | Real conversation | ✅ |
| T05 | Pregnancy essentials, 300 AED | Real conversation | ✅ |
| T06 | Laptop refusal | Adversarial | ✅ |
| T07 | Weather refusal | Adversarial | ✅ |
| T08 | Impossible stroller budget | Adversarial | ❌ eval bug |
| T09 | Arabic sensitive skin input | Arabic-native | ✅ |
| T10 | Gibberish refusal | Adversarial | ✅ |
| T11 | Medical safety — lactose formula | Medical context | ✅ |
| T12 | Exact budget edge case, 120 AED | Edge case | ✅ |

---

## Tradeoffs

Full architecture decisions: [`TRADEOFFS.md`](TRADEOFFS.md)

**Key decisions:**

**Keyword retrieval over embeddings** — Embeddings would give better semantic recall but require a vector store (Pinecone/FAISS) adding ~1 hour of infrastructure work to the 5-hour budget. For a 500-product structured catalog with explicit tags, keyword + tag scoring achieves sufficient recall for the highest-stakes queries.

**Strict Pydantic schema** — Every field that matters to correctness is validated before output reaches the user. This costs speed (retries on validation failure) but the retry rate was 0% in the eval suite, so the cost was never paid.

**Single model, dual-field Arabic** — Rather than translating English reasons to Arabic, the model generates `reason_ar` independently. This produces natural Arabic but requires the model to do more work per request.

**What was cut:** Embedding retrieval, real-time product API, delivery time data, personalization layer, automated Arabic quality scoring. All documented with rationale in TRADEOFFS.md.

---

## Time Log

| Phase | Time | What Was Done |
|-------|------|---------------|
| Discovery — live chat testing | 60 min | 6 Mumzworld conversations across 2 languages, evidence documentation |
| Product catalog construction | 45 min | 500-product JSON across 12 categories with all required fields |
| System prompt design and iteration | 45 min | Refusal rules, Arabic quality examples, budget allocation logic |
| Core pipeline (advisor.py, schema.py, prompts.py) | 75 min | OpenRouter integration, Pydantic schema, retry logic |
| Streamlit UI (app.py) | 30 min | Query input, results rendering, budget breakdown display |
| Eval suite (evals.py) | 45 min | 12 test cases, 5-dimension scoring, latency benchmark |
| README, EVALS.md, TRADEOFFS.md, DISCOVERY.md | 60 min | Documentation |
| **Total** | **~6 hours** | Went ~1 hour over. Discovery phase took longer than expected because I ran 6 conversations instead of the planned 3. Worth it — the ChatGPT UTM finding changed the framing of the entire submission. |

---

## AI Usage Note

- **Claude (claude.ai):** Problem framing, system prompt design, Arabic quality review, schema architecture, documentation drafting
- **GPT-4o:** Code generation for retrieval pipeline and Pydantic validators, UI layout
- **Llama 3.3 70B via OpenRouter:** The model running inside the product itself
- **All architectural decisions, test case design, and eval scoring:** Written and validated manually

This submission cannot explain its own provenance by accident — every choice in the architecture was made deliberately and is documented in TRADEOFFS.md.

---

## What Would Be Built Next

In priority order:

1. **Fix T08 eval assertion** — 30 minutes. Update refusal check to accept `budget_feasible=False` + `refusal_reason` as a passing signal.
2. **Embedding-based retrieval** — Replace keyword scoring with FAISS + sentence-transformers for semantic matching.
3. **Streaming responses** — Perceived latency drops from 24s to near-instant.
4. **Delivery time in catalog** — Add `delivery_days_uae` field. Surface next-day delivery products first when `urgency_detected=True`.
5. **Automated Arabic quality eval** — LLM-as-judge scoring Arabic naturalness on 1–5 scale.
6. **Live Mumzworld catalog integration** — Replace synthetic products with real API feed.

---

## Repository

```
GitHub: https://github.com/yourusername/mumzadvisor
Loom: [3-minute walkthrough — link here]
```

---

*MumzAdvisor — Built as a prototype for the Mumzworld AI Intern assessment.*
*Products and prices are synthetic and illustrative. Always verify on mumzworld.com.*
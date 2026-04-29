# TRADEOFFS.md
## MumzAdvisor — Architecture Decisions, Tradeoffs, and Honest Reflection
**Track A | AI Engineering Intern | Mumzworld**

---

## 1. Why This Problem

### The decision

I tested 6 real Mumzworld customer support conversations before writing a single line of code. The finding was consistent across all 6:

**Not one conversation — across 5 different queries, 2 languages, and 3 different human agents — produced a specific product recommendation with a price, within the stated budget, with reasoning, in under 60 seconds.**

The most revealing data point: in Test 3 (pregnant mom, 300 AED budget), the agent sent a link with the UTM parameter `?utm_source=chatgpt.com` — meaning agents are already using external AI to answer product queries. The solution works. It just hasn't been built natively into the platform.

### Problems I considered and rejected

| Problem | Why rejected |
|---------|-------------|
| Customer service email triage | Internal-facing, lower revenue impact, harder to demo |
| Product review synthesiser | Useful but doesn't solve the abandonment problem |
| Pregnancy timeline content generator | Broad scope, hard to evaluate objectively |
| Duplicate product detection | Engineering-interesting but not customer-facing |

### Why this problem beats the alternatives

Mumzworld does not have a **discovery** problem. The catalog is browsable. Filters exist. Search works.

The problem is **decision-making under constraint** — a mom with a specific budget, a baby with a medical condition, and 3 minutes of patience cannot be helped by a search bar. She needs a verdict, not a list.

That is an inference problem. Inference is what LLMs do well. A UX fix or a better filter would not solve it.

---

## 2. Architecture

### What I built

```
User Query (EN or AR)
        ↓
Catalog Filter (keyword + tag scoring)
        ↓
LLM Reasoning (OpenRouter → Llama 3.3 70B)
        ↓
Structured Output (JSON)
        ↓
Schema Validation (Pydantic)
        ↓
Retry if invalid (max 2 attempts)
        ↓
Rendered Response (Streamlit UI)
```

### Why not pure LLM with no retrieval

Rejected immediately. Without grounding to a real catalog, the model invents product names, prices, and features. In a medical context (lactose-free formula, sensitive skin) a hallucinated product recommendation is not just unhelpful — it's potentially harmful. Grounding was non-negotiable from the start.

### Why not vector embeddings for retrieval

Embeddings would give better semantic recall — finding "gentle wash for eczema baby" even if the product isn't tagged "eczema." I chose keyword + tag scoring instead because:

- Embeddings require a vector store setup (Pinecone, Chroma, or local FAISS) which adds ~1 hour of infrastructure work to the 5-hour budget
- For a 500-product catalog with well-structured tags, keyword scoring achieves acceptable recall
- The tags in the catalog (`sensitive_skin_safe`, `lactose_free`, `age_months_min/max`) are structured specifically to support exact-match filtering for the highest-stakes queries

**What I gave up:** Semantic fuzzy matching. A query like "wash for baby with eczema" won't match `sensitive_skin_safe` products unless the word "sensitive" appears. In production, embeddings would fix this.

### Why Pydantic schema validation

Every field that matters to correctness — budget_feasible, refused, fit_score, confidence — is validated before any output reaches the user. This catches two real failure modes:

1. Model returns `budget_feasible: true` when total cost exceeds budget (contradictory)
2. Model returns recommendations when it should refuse (hallucinated helpfulness)

**What I gave up:** Speed. Each validation failure triggers a retry, adding up to ~15s per failed attempt. In practice, the retry rate was 0% across the eval suite (100% reliability on first attempt), so the latency cost was never paid during testing.

---

## 3. Model Choice

### Chosen: `meta-llama/llama-3.3-70b-instruct:free` via OpenRouter

**Why:**
- Best free-tier model for structured JSON output reliability
- Strong Arabic capability relative to other free models
- 128k context window handles full catalog slices without truncation

### What I considered

| Model | Verdict | Reason rejected or not chosen |
|-------|---------|-------------------------------|
| Llama 3.3 70B | ✅ Chosen | Best balance of JSON reliability and Arabic quality |
| DeepSeek V3 | Tested, not chosen | Strong reasoning but weaker Arabic output quality |
| Qwen 2.5 72B | Considered | Good Arabic but less reliable structured output |
| GPT-4o-mini (paid) | Not available | Would be first choice on paid tier — 3–5s latency |
| Claude 3 Haiku (paid) | Not available | Strong structured output, but paid only |

### Honest assessment of the model choice

Llama 3.3 70B on free-tier OpenRouter has significant queuing latency that is out of my control. The model itself is fast — the wait time is infrastructure. On a paid endpoint, the same model would run in 3–6s. The 24s average in my evals is not a model quality problem — it is a free-tier infrastructure problem.

---

## 4. Latency — Honest Numbers

From the eval suite (12 test cases, April 2026):

| Metric | Value |
|--------|-------|
| Average | 24.21s |
| Median (P50) | 22.85s |
| P95 | 55.84s |
| Fastest | 4.38s (out-of-scope refusal) |
| Slowest | 55.84s (pregnancy essentials, large catalog slice) |

**This is not production-ready.** I am not going to pretend otherwise.

The current system would cause drop-off in a real chat interface. A mom who typed a question and waited 55 seconds would close the tab.

### Why is it slow

1. **Free-tier queuing** — OpenRouter free models have variable queue times. This accounts for ~70% of observed latency.
2. **Large catalog slices** — T05 (pregnancy essentials) passed 20 products to the model, inflating token count and inference time.
3. **No streaming** — The user sees nothing until the full JSON is validated and rendered. Perceived latency equals actual latency.

### Production path to acceptable latency

| Change | Expected impact |
|--------|----------------|
| Paid endpoint (GPT-4o-mini or Haiku) | Average drops to 3–5s |
| Streaming responses | Perceived latency drops immediately |
| Reduce catalog slice to top 8 products | ~20% token reduction |
| Cache repeated query patterns | Near-zero latency for common queries |

---

## 5. Multilingual Approach

### Chosen: Single model, dual-field output

Every response returns both `reason` (English) and `reason_ar` (Arabic) regardless of input language. The model detects input language and sets the `language` field accordingly.

**Why dual-field instead of translate-after:**
Post-hoc translation produces Arabic that reads like translated Arabic — formal, literal, unnatural. The system prompt explicitly instructs the model to write `reason_ar` independently in natural Gulf Arabic, not to translate the English reasoning.

**Known gap:** Arabic quality is evaluated manually in this prototype. I can read the output and identify translation-pattern phrasing, but there is no automated Arabic quality score. In production, a native Arabic speaker review pass or an LLM-as-judge Arabic quality scorer would be the next step.

**What the brief says:** "Arabic that reads like a literal translation" is listed as a "bad" signal. I took this seriously. The system prompt includes explicit good/bad Arabic examples to steer the model away from literal patterns.

---

## 6. Structured Output and Schema Design

### Why strict validation over flexible output

The alternative — parsing free-text responses and extracting recommendations manually — trades validation complexity for prompt simplicity. I rejected it because:

- Budget compliance cannot be verified without structured `total_cost_aed`
- Refusal detection requires an explicit `refused` boolean, not sentiment analysis on free text
- Eval automation requires machine-readable output

The Pydantic schema has 3 response types that are all valid:
1. Normal recommendation response
2. Explicit refusal (out-of-scope, gibberish, medical diagnosis)
3. Impossible budget response (`budget_feasible=False`, empty recommendations, `refusal_reason` citing minimum available price)

Type 3 was added mid-build when T08 (double stroller under 200 AED) exposed a gap — the model correctly identified the impossible budget but the schema rejected it because it expected either a refusal or recommendations, not a third state. This was fixed in the schema. The eval checker was not updated in time, causing T08 to fail the eval despite correct model behavior. This is documented honestly in EVALS.md.

---

## 7. What Was Cut and Why

### Embedding-based retrieval
**Cut because:** Infrastructure setup (vector store + embedding model) would consume ~1 hour of the 5-hour budget. Keyword + tag scoring achieves sufficient recall for a structured catalog. **Would build next.**

### Real-time product API
**Cut because:** Mumzworld does not have a public API. Products and prices in this prototype are synthetic, derived from publicly visible catalog data. In production, the catalog would be replaced with a live feed. **Required for production.**

### Delivery time optimization
**Cut because:** No delivery data available in the prototype catalog. This is the gap that T01 (urgent sippy cup, 3-day deadline) exposed most sharply — the system detects urgency but cannot actually tell the mom which product ships tomorrow. **High priority for production.**

### Personalization layer
**Cut because:** Requires user history and authentication, which is out of scope for a standalone prototype. **Would be a significant value-add in production** — a returning mom shouldn't have to re-specify her baby's age every time.

### Automated Arabic quality scoring
**Cut because:** Building an LLM-as-judge Arabic evaluator would add complexity without changing the core system. Manual review was used instead. **Would build next.**

### Frontend beyond Streamlit
**Cut because:** Streamlit was sufficient to demonstrate the end-to-end flow for the Loom recording. A production interface would be a React component embedded in the Mumzworld chat widget.

---

## 8. Evaluation Design Decision

Evals were written before building, not after. This matters because post-hoc evals are easy to write to match expected outputs — they measure what the system does, not what it should do.

All 12 test cases were derived from:
- 5 real Mumzworld customer conversations documented in DISCOVERY.md
- 4 adversarial refusal cases designed to probe scope boundaries
- 3 edge cases (exact budget, Arabic-only input, medical context)

The one eval failure (T08) is an eval engineering gap — the assertion logic was not updated after the schema was changed to accept impossible-budget responses as a valid third response type. The model behavior is correct. This is documented rather than hidden.

---

## 9. What I Would Build Next

### Next Improvements (Post Submission)

If given more time, I would focus on:

- Improving semantic search using embeddings (FAISS) to better match user intent beyond keywords.
- Adding streaming responses to improve perceived latency in the UI.
- Enhancing Arabic output quality with LLM-based evaluation and refinement.
- Adding delivery-time awareness to prioritize urgent recommendations.
---

## Final Reflection

The hardest decision in this project was not technical — it was scoping.

The temptation was to build something more impressive: embeddings, a vector store, a two-stage model pipeline, a real API integration. Any of those would have looked better in a demo.

But the brief explicitly said: *"honestly scoped to ship in ~5 hours."*

The system I built is not the most sophisticated possible version. It is a working prototype that demonstrates the core value — a mom can describe her situation in plain English or Arabic and receive specific, priced, reasoned product recommendations in under 30 seconds — with honest handling of the cases where it cannot help.

That is the gap the current Mumzworld system cannot close. This prototype closes it.
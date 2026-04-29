import os
import json
import time
import re
import requests
from dotenv import load_dotenv
from src.schema import AdvisorResponse

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "meta-llama/llama-3.3-70b-instruct"
MAX_CATALOG_ITEMS = 25
REQUEST_TIMEOUT = 25


# ─────────────────────────────────────────────
# LOADERS
# ─────────────────────────────────────────────
def load_system_prompt():
    prompt_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "prompts",
        "system_prompt.txt"
    )
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


def load_catalog():
    catalog_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "data",
        "products.json"
    )
    with open(catalog_path, "r", encoding="utf-8") as f:
        return json.load(f)


# ─────────────────────────────────────────────
# QUERY NORMALIZATION
# ─────────────────────────────────────────────
def normalize_text(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9\u0600-\u06FF\s]", " ", text.lower())


def extract_keywords(user_query: str) -> list[str]:
    stopwords = {
        "the", "and", "for", "with", "baby", "need", "want", "under",
        "best", "good", "from", "that", "this", "have", "my", "your",
        "aed", "old", "months", "month", "years", "year"
    }

    words = normalize_text(user_query).split()

    return [
        word for word in words
        if len(word) > 2 and word not in stopwords
    ]


# ─────────────────────────────────────────────
# SMART CATALOG FILTERING
# ─────────────────────────────────────────────
def filter_catalog(user_query: str, catalog: list) -> list:
    """
    Lightweight retrieval layer:
    Reduces token size while preserving relevant products.
    """
    query = user_query.lower()
    keywords = extract_keywords(user_query)

    scored_products = []

    for product in catalog:
        searchable_fields = [
            product.get("name", ""),
            product.get("product_name", ""),
            product.get("brand", ""),
            product.get("category", ""),
            product.get("subcategory", ""),
            product.get("description", ""),
            " ".join(product.get("tags", [])) if isinstance(product.get("tags"), list) else str(product.get("tags", "")),
        ]

        searchable_text = normalize_text(" ".join(map(str, searchable_fields)))

        score = 0

        # Keyword relevance
        for keyword in keywords:
            if keyword in searchable_text:
                score += 2

        # Special boosts
        if "sensitive" in query or "rash" in query:
            if product.get("sensitive_skin_safe"):
                score += 8
            if "fragrance" in searchable_text:
                score -= 3

        if "lactose" in query or "formula" in query:
            if product.get("lactose_free"):
                score += 8

        if "gift" in query or "هدية" in query:
            if "toy" in searchable_text or "gift" in searchable_text:
                score += 5

        if "pregnant" in query or "pregnancy" in query:
            if "maternity" in searchable_text:
                score += 6

        if score > 0:
            scored_products.append((score, product))

    # Sort highest relevance
    scored_products.sort(key=lambda x: x[0], reverse=True)

    filtered = [product for _, product in scored_products[:MAX_CATALOG_ITEMS]]

    # Fallback if no matches
    if not filtered:
        filtered = catalog[:MAX_CATALOG_ITEMS]

    return filtered


# ─────────────────────────────────────────────
# OPENROUTER API CALL
# ─────────────────────────────────────────────
def call_openrouter(system_prompt: str, user_message: str) -> str:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://mumzadvisor.app",
        "X-Title": "MumzAdvisor"
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.2,
        "max_tokens": 1200,
    }

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=REQUEST_TIMEOUT
    )

    if response.status_code != 200:
        raise Exception(
            f"OpenRouter API error {response.status_code}: {response.text}"
        )

    return response.json()["choices"][0]["message"]["content"]


# ─────────────────────────────────────────────
# RESPONSE PARSING
# ─────────────────────────────────────────────
def parse_and_validate(raw_response: str) -> tuple[AdvisorResponse | None, str | None]:
    cleaned = raw_response.strip()

    # Remove markdown fences
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        lines = [
            line for line in lines
            if not line.strip().startswith("```")
        ]
        cleaned = "\n".join(lines).strip()

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        return (
            None,
            f"JSON parse error: {str(e)}\nRaw response:\n{raw_response[:500]}"
        )

    try:
        validated = AdvisorResponse(**data)
        return validated, None
    except Exception as e:
        return None, f"Schema validation error: {str(e)}"


# ─────────────────────────────────────────────
# PRODUCT GROUNDING VALIDATION
# ─────────────────────────────────────────────
def validate_product_grounding(
    response: AdvisorResponse,
    catalog: list
) -> tuple[bool, str | None]:
    valid_ids = {
        str(product.get("id"))
        for product in catalog
    }

    for rec in response.recommendations:
        if rec.product_id not in valid_ids:
            return (
                False,
                f"Hallucinated product detected: {rec.product_id}"
            )

    return True, None


# ─────────────────────────────────────────────
# MAIN RECOMMENDATION PIPELINE
# ─────────────────────────────────────────────
def get_recommendation(
    user_query: str
) -> tuple[AdvisorResponse | None, str | None]:

    system_prompt = load_system_prompt()
    full_catalog = load_catalog()

    filtered_catalog = filter_catalog(user_query, full_catalog)

    user_message = f"""User query: {user_query}

Product catalog (recommend ONLY from this list):
{json.dumps(filtered_catalog, ensure_ascii=False, indent=2)}
"""

    last_error = None
    start_time = time.time()

    for attempt in range(2):
        try:
            raw_response = call_openrouter(
                system_prompt,
                user_message
            )

            result, error = parse_and_validate(raw_response)

            if result:
                grounded, grounding_error = validate_product_grounding(
                    result,
                    full_catalog
                )

                if not grounded:
                    return None, grounding_error

                elapsed = round(time.time() - start_time, 2)
                print(
                    f"[MumzAdvisor] Response generated in {elapsed}s "
                    f"(catalog size: {len(filtered_catalog)})"
                )

                return result, None

            last_error = error

            # Retry reinforcement
            user_message += "\n\nIMPORTANT: Return ONLY valid raw JSON."

        except Exception as e:
            last_error = f"API call failed: {str(e)}"

    return None, last_error
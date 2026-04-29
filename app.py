import streamlit as st
import time
import json
import os
from src.advisor import get_recommendation

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="MumzAdvisor | مستشار ممز",
    page_icon="🍼",
    layout="centered"
)

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []

if "last_query" not in st.session_state:
    st.session_state.last_query = ""

if "query_input" not in st.session_state:
    st.session_state.query_input = ""

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
    <h1 style='text-align: center;'>🍼 MumzAdvisor</h1>
    <p style='text-align: center; color: gray;'>
        AI-powered product advisor for Mumzworld — English & Arabic<br>
        <span dir='rtl'>مستشار منتجات بالذكاء الاصطناعي — عربي وإنجليزي</span>
    </p>
    <hr/>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# API KEY CHECK
# ─────────────────────────────────────────────
if not os.getenv("OPENROUTER_API_KEY"):
    st.error(
        "⚠️ OPENROUTER_API_KEY is missing. Please configure your environment variables."
    )
    st.stop()

# ─────────────────────────────────────────────
# EXAMPLE QUERIES
# ─────────────────────────────────────────────
st.markdown("### 💬 Try an example or type your own")

examples = [
    "My 9 month old is refusing the bottle, going back to work in 3 days. Under 100 AED?",
    "أحتاج هدية لصديقتي عندها طفل عمره 6 أشهر، الميزانية 200 درهم",
    "Baby 4 months, sensitive skin, rashes. Need soap, cream, baby tub. Budget 250 AED total.",
    "Is Philips Avent better than Momcozy for a working mom who travels?",
    "I'm 8 months pregnant, first time mom, budget 300 AED — what do I need?",
    "My newborn has colic and feeding issues. Need anti-colic bottles under 150 AED.",
    "Toddler 2 years old, traveling internationally. Need lightweight stroller under 500 AED.",
    "Best breast pump for a full-time working mom with frequent travel?",
    "Need hospital bag essentials for delivery next month, budget 400 AED.",
    "My baby has eczema and dry skin. Need safe lotion, wash, and diaper cream under 200 AED.",
    "Looking for teething toys for a 6-month-old baby under 120 AED.",
    "I need a double stroller for twins under 200 AED.",
    "أبحث عن كرسي سيارة آمن لطفل عمره سنة بميزانية 600 درهم",
    "Need weaning essentials for my 7-month-old starting solids, budget 180 AED.",
    "Best diaper bag for a working mom who commutes daily?"
]

selected = st.selectbox(
    "Pick an example (or ignore and type below)",
    ["— type your own —"] + examples
)

# Update text area automatically when example selected
if selected != "— type your own —":
    st.session_state.query_input = selected
elif st.session_state.last_query:
    st.session_state.query_input = st.session_state.last_query

query = st.text_area(
    "Your question (English or Arabic / سؤالك بالعربي أو الإنجليزي)",
    key="query_input",
    height=100,
    placeholder="e.g. My baby is 6 months and I need teething toys under 150 AED..."
)

# ─────────────────────────────────────────────
# ACTION BUTTONS
# ─────────────────────────────────────────────
col_submit, col_retry = st.columns([3, 1])

with col_submit:
    submit = st.button(
        "🔍 Get Recommendations",
        type="primary",
        use_container_width=True
    )


with col_retry:
    retry = st.button(
        "🔄 Retry",
        use_container_width=True
    )

if retry and st.session_state.history:
    st.session_state.query_input = st.session_state.history[-1]["query"]
    st.session_state.trigger_submit = True
    st.rerun()

# Read trigger flag
if "trigger_submit" not in st.session_state:
    st.session_state.trigger_submit = False

if st.session_state.trigger_submit:
    st.session_state.trigger_submit = False
    submit = True
    query = st.session_state.query_input

# ─────────────────────────────────────────────
# HELPER FUNCTION
# ─────────────────────────────────────────────
def run_advisor_with_retry(user_query: str, max_attempts: int = 2):
    """
    Runs recommendation with retry support.
    Returns: response, error, attempts_used
    """
    last_error = None

    for attempt in range(1, max_attempts + 1):
        response, error = get_recommendation(user_query)

        if response:
            return response, None, attempt

        last_error = error

    return None, last_error, max_attempts


# ─────────────────────────────────────────────
# RESULT DISPLAY
# ─────────────────────────────────────────────
if submit:
    query = st.session_state.query_input

    if not query.strip():
        st.warning("Please enter a question first.")
    else:
        st.session_state.last_query = query

        progress = st.progress(0)
        status = st.empty()

        start_time = time.time()
        status.info("🔎 Analyzing your request and matching products...")

        progress.progress(20)

        response, error, attempts = run_advisor_with_retry(query)

        progress.progress(90)

        latency = round(time.time() - start_time, 2)

        progress.progress(100)
        time.sleep(0.2)
        progress.empty()
        status.empty()

        # ─────────────────────────────────────
        # ERROR HANDLING
        # ─────────────────────────────────────
        if error:
            st.error(
                f"⚠️ Something went wrong after {attempts} attempt(s): {error}"
            )

        elif response is None:
            st.error("No response received. Please try again.")

        else:
            # Save history
            st.session_state.history.append({
                "query": query,
                "response": response.model_dump(mode="json")
            })

            # ─────────────────────────────────
            # LATENCY DISPLAY
            # ─────────────────────────────────
            speed_label = (
                "⚡ Excellent" if latency < 15 else
                "🟢 Good" if latency < 30 else
                "🟡 Moderate" if latency < 50 else
                "🔴 Slow"
            )

            st.success(
                f"⏱️ Response generated in {latency} seconds | {speed_label} | Attempts: {attempts}"
            )

            # JSON Download
            st.download_button(
                label="📥 Download JSON Response",
                data=json.dumps(
                    response.model_dump(mode="json"),
                    ensure_ascii=False,
                    indent=2
                ),
                file_name="mumzadvisor_response.json",
                mime="application/json"
            )

            # ─────────────────────────────────
            # REFUSAL DISPLAY
            # ─────────────────────────────────
            if response.refused:
                st.warning("🚫 Out of scope / خارج النطاق")

                if response.refusal_reason:
                    st.write(f"**English:** {response.refusal_reason}")

                if response.refusal_reason_ar:
                    st.markdown(
                        f"<div dir='rtl' style='text-align:right'>{response.refusal_reason_ar}</div>",
                        unsafe_allow_html=True
                    )

            else:
                # Urgency
                if response.urgency_detected and response.urgency_note:
                    st.error(f"⚡ Urgent: {response.urgency_note}")

                # Clarification
                if (
                    response.needs_clarification and
                    response.clarification_question
                ):
                    st.info(f"❓ {response.clarification_question}")

                # Budget Summary
                if response.total_budget_aed:
                    col1, col2, col3 = st.columns(3)

                    col1.metric(
                        "Budget",
                        f"{response.total_budget_aed} AED"
                    )

                    if response.total_cost_aed:
                        col2.metric(
                            "Total Cost",
                            f"{response.total_cost_aed} AED"
                        )

                    if response.budget_feasible is not None:
                        col3.metric(
                            "Budget OK?",
                            "✅ Yes" if response.budget_feasible else "❌ No"
                        )

                if response.budget_feasible is False:
                    st.warning(
                        f"⚠️ Budget notice: {response.confidence_note or 'The requested items exceed your budget.'}"
                    )

                # Confidence
                conf_color = {
                    "high": "🟢",
                    "medium": "🟡",
                    "low": "🔴"
                }

                conf = response.confidence.value

                st.markdown(
                    f"### Confidence: {conf_color.get(conf, '⚪')} {conf.upper()}"
                )

                if response.confidence_note:
                    st.caption(response.confidence_note)

                st.markdown("---")

                # ─────────────────────────────
                # PRODUCT CARDS
                # ─────────────────────────────
                st.markdown("### 🛍️ Recommended Products")

                for i, product in enumerate(response.recommendations, 1):
                    stars = "⭐" * max(1, round(product.fit_score * 5))

                    with st.expander(
                        f"#{i} {product.product_name} — {product.price_aed} AED {stars}",
                        expanded=True
                    ):
                        col_a, col_b = st.columns([3, 1])

                        with col_a:
                            st.markdown(f"**🇬🇧 {product.product_name}**")
                            st.write(product.reason)

                            st.markdown("---")

                            st.markdown(f"**🇸🇦 {product.product_name_ar}**")
                            st.markdown(
                                f"""
                                <div dir='rtl' style='text-align:right; font-size:16px; line-height:1.8'>
                                    {product.reason_ar}
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                        with col_b:
                            st.metric(
                                "Price",
                                f"{product.price_aed} AED"
                            )
                            st.metric(
                                "Fit Score",
                                f"{round(product.fit_score * 100)}%"
                            )
                            st.link_button(
                                "View on Mumzworld 🔗",
                                str(product.url)
                            )

                # Budget Breakdown
                if response.budget_allocations:
                    st.markdown("### 💰 Budget Breakdown")

                    for alloc in response.budget_allocations:
                        st.markdown(
                            f"- **{alloc.item}** ({alloc.item_ar}): **{alloc.allocated_aed} AED**"
                        )

                # Language
                lang_label = (
                    "🇬🇧 English"
                    if response.language.value == "en"
                    else "🇸🇦 Arabic"
                )

                st.caption(
                    f"Response language detected: {lang_label}"
                )

# ─────────────────────────────────────────────
# HISTORY
# ─────────────────────────────────────────────
if st.session_state.history:
    st.markdown("---")
    st.markdown("### 🕘 Recent Queries")

    for item in reversed(st.session_state.history[-5:]):
        st.markdown(f"- {item['query']}")

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.caption(
    "MumzAdvisor — Built as a prototype for Mumzworld AI Intern assessment. "
    "Products and prices are illustrative. Always verify on mumzworld.com."
)
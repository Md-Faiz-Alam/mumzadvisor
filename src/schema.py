# from pydantic import (
#     BaseModel,
#     field_validator,
#     model_validator,
#     HttpUrl
# )
# from typing import Optional
# from enum import Enum


# # ─────────────────────────────────────────────
# # ENUMS
# # ─────────────────────────────────────────────
# class ConfidenceLevel(str, Enum):
#     HIGH = "high"
#     MEDIUM = "medium"
#     LOW = "low"


# class Language(str, Enum):
#     EN = "en"
#     AR = "ar"


# # ─────────────────────────────────────────────
# # PRODUCT RECOMMENDATION
# # ─────────────────────────────────────────────
# class ProductRecommendation(BaseModel):
#     product_id: str
#     product_name: str
#     product_name_ar: str
#     price_aed: float
#     reason: str
#     reason_ar: str
#     fit_score: float
#     url: HttpUrl

#     @field_validator("fit_score")
#     @classmethod
#     def fit_score_range(cls, v):
#         if not 0.0 <= v <= 1.0:
#             raise ValueError(
#                 "fit_score must be between 0.0 and 1.0"
#             )
#         return round(v, 2)

#     @field_validator("price_aed")
#     @classmethod
#     def price_positive(cls, v):
#         if v <= 0:
#             raise ValueError(
#                 "price_aed must be positive"
#             )
#         return round(v, 2)

#     @field_validator("reason")
#     @classmethod
#     def english_reason_required(cls, v):
#         if not v or len(v.strip()) < 10:
#             raise ValueError(
#                 "English reason must be meaningful"
#             )
#         return v.strip()

#     @field_validator("reason_ar")
#     @classmethod
#     def arabic_reason_required(cls, v):
#         if not v or len(v.strip()) < 10:
#             raise ValueError(
#                 "Arabic reason must be meaningful"
#             )
#         return v.strip()


# # ─────────────────────────────────────────────
# # BUDGET ALLOCATION
# # ─────────────────────────────────────────────
# class BudgetAllocation(BaseModel):
#     item: str
#     item_ar: str
#     allocated_aed: float
#     product_id: Optional[str] = None

#     @field_validator("allocated_aed")
#     @classmethod
#     def allocation_positive(cls, v):
#         if v <= 0:
#             raise ValueError(
#                 "allocated_aed must be positive"
#             )
#         return round(v, 2)


# # ─────────────────────────────────────────────
# # MAIN RESPONSE SCHEMA
# # ─────────────────────────────────────────────
# class AdvisorResponse(BaseModel):
#     # Core output
#     recommendations: list[ProductRecommendation]
#     language: Language

#     # Budget
#     total_budget_aed: Optional[float] = None
#     total_cost_aed: Optional[float] = None
#     budget_feasible: Optional[bool] = None
#     budget_allocations: Optional[list[BudgetAllocation]] = None

#     # Confidence
#     confidence: ConfidenceLevel
#     confidence_note: Optional[str] = None
#     confidence_note_ar: Optional[str] = None

#     # Refusal
#     refused: bool = False
#     refusal_reason: Optional[str] = None
#     refusal_reason_ar: Optional[str] = None

#     # Urgency
#     urgency_detected: bool = False
#     urgency_note: Optional[str] = None
#     urgency_note_ar: Optional[str] = None

#     # Clarification
#     needs_clarification: bool = False
#     clarification_question: Optional[str] = None
#     clarification_question_ar: Optional[str] = None

#     # ─────────────────────────────────────────
#     # FIELD VALIDATORS
#     # ─────────────────────────────────────────
#     @field_validator("recommendations")
#     @classmethod
#     def max_recommendations(cls, v):
#         if len(v) > 5:
#             raise ValueError(
#                 "Maximum 5 recommendations allowed"
#             )
#         return v

#     @field_validator("total_budget_aed", "total_cost_aed")
#     @classmethod
#     def budget_values_positive(cls, v):
#         if v is not None and v < 0:
#             raise ValueError(
#                 "Budget values cannot be negative"
#             )
#         return round(v, 2) if v is not None else v

#     # ─────────────────────────────────────────
#     # MODEL-LEVEL VALIDATORS
#     # ─────────────────────────────────────────
#     @model_validator(mode="after")
#     def validate_response_logic(self):
#         # Refusal consistency
#         if self.refused:
#             if len(self.recommendations) > 0:
#                 raise ValueError(
#                     "Refused responses must not include recommendations"
#                 )
#             if not self.refusal_reason:
#                 raise ValueError(
#                     "Refused responses must include refusal_reason"
#                 )

#         # Non-refusal consistency
#         if not self.refused and len(self.recommendations) == 0:
#             raise ValueError(
#                 "Non-refused responses must include recommendations"
#             )

#         # Clarification consistency
#         if self.needs_clarification:
#             if not self.clarification_question:
#                 raise ValueError(
#                     "Clarification question required when needs_clarification is true"
#                 )

#         # Budget feasibility consistency
#         if (
#             self.total_budget_aed is not None and
#             self.total_cost_aed is not None
#         ):
#             if (
#                 self.total_cost_aed > self.total_budget_aed and
#                 self.budget_feasible is True
#             ):
#                 raise ValueError(
#                     "budget_feasible cannot be true if total cost exceeds budget"
#                 )

#             if (
#                 self.total_cost_aed <= self.total_budget_aed and
#                 self.budget_feasible is False
#             ):
#                 raise ValueError(
#                     "budget_feasible should not be false if within budget"
#                 )

#         # Budget allocation sum check
#         if (
#             self.budget_allocations and
#             self.total_budget_aed is not None
#         ):
#             allocation_sum = sum(
#                 alloc.allocated_aed
#                 for alloc in self.budget_allocations
#             )

#             if allocation_sum > self.total_budget_aed:
#                 raise ValueError(
#                     "Budget allocations exceed total budget"
#                 )

#         # Arabic language consistency
#         if self.language == Language.AR:
#             if not self.confidence_note_ar and not self.refused:
#                 raise ValueError(
#                     "Arabic responses should include Arabic confidence note"
#                 )

#         return self

#     # ─────────────────────────────────────────
#     # HELPER METHODS
#     # ─────────────────────────────────────────
#     def is_valid_response(self) -> bool:
#         """
#         Valid non-refused response requires
#         at least one recommendation.
#         """
#         if self.refused:
#             return (
#                 self.refusal_reason is not None
#                 and len(self.refusal_reason.strip()) > 0
#             )

#         return len(self.recommendations) > 0

#     def total_within_budget(self) -> Optional[bool]:
#         """
#         Returns:
#         - True if within budget
#         - False if exceeds
#         - None if budget unknown
#         """
#         if (
#             self.total_budget_aed is not None and
#             self.total_cost_aed is not None
#         ):
#             return (
#                 self.total_cost_aed <= self.total_budget_aed
#             )

#         return None

from pydantic import (
    BaseModel,
    field_validator,
    model_validator,
    HttpUrl
)
from typing import Optional
from enum import Enum


# ─────────────────────────────────────────────
# ENUMS
# ─────────────────────────────────────────────
class ConfidenceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Language(str, Enum):
    EN = "en"
    AR = "ar"


# ─────────────────────────────────────────────
# PRODUCT RECOMMENDATION
# ─────────────────────────────────────────────
class ProductRecommendation(BaseModel):
    product_id: str
    product_name: str
    product_name_ar: str
    price_aed: float
    reason: str
    reason_ar: str
    fit_score: float
    url: HttpUrl

    @field_validator("fit_score")
    @classmethod
    def fit_score_range(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError(
                "fit_score must be between 0.0 and 1.0"
            )
        return round(v, 2)

    @field_validator("price_aed")
    @classmethod
    def price_positive(cls, v):
        if v <= 0:
            raise ValueError(
                "price_aed must be positive"
            )
        return round(v, 2)

    @field_validator("reason")
    @classmethod
    def english_reason_required(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError(
                "English reason must be meaningful"
            )
        return v.strip()

    @field_validator("reason_ar")
    @classmethod
    def arabic_reason_required(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError(
                "Arabic reason must be meaningful"
            )
        return v.strip()


# ─────────────────────────────────────────────
# BUDGET ALLOCATION
# ─────────────────────────────────────────────
class BudgetAllocation(BaseModel):
    item: str
    item_ar: str
    allocated_aed: float
    product_id: Optional[str] = None

    @field_validator("allocated_aed")
    @classmethod
    def allocation_positive(cls, v):
        if v <= 0:
            raise ValueError(
                "allocated_aed must be positive"
            )
        return round(v, 2)


# ─────────────────────────────────────────────
# MAIN RESPONSE SCHEMA
# ─────────────────────────────────────────────
class AdvisorResponse(BaseModel):
    # Core output
    recommendations: list[ProductRecommendation]
    language: Language

    # Budget
    total_budget_aed: Optional[float] = None
    total_cost_aed: Optional[float] = None
    budget_feasible: Optional[bool] = None
    budget_allocations: Optional[list[BudgetAllocation]] = None

    # Confidence
    confidence: ConfidenceLevel
    confidence_note: Optional[str] = None
    confidence_note_ar: Optional[str] = None

    # Refusal
    refused: bool = False
    refusal_reason: Optional[str] = None
    refusal_reason_ar: Optional[str] = None

    # Urgency
    urgency_detected: bool = False
    urgency_note: Optional[str] = None
    urgency_note_ar: Optional[str] = None

    # Clarification
    needs_clarification: bool = False
    clarification_question: Optional[str] = None
    clarification_question_ar: Optional[str] = None

    # ─────────────────────────────────────────
    # FIELD VALIDATORS
    # ─────────────────────────────────────────
    @field_validator("recommendations")
    @classmethod
    def max_recommendations(cls, v):
        if len(v) > 5:
            raise ValueError(
                "Maximum 5 recommendations allowed"
            )
        return v

    @field_validator("total_budget_aed", "total_cost_aed")
    @classmethod
    def budget_values_positive(cls, v):
        if v is not None and v < 0:
            raise ValueError(
                "Budget values cannot be negative"
            )
        return round(v, 2) if v is not None else v

    # ─────────────────────────────────────────
    # MODEL-LEVEL VALIDATORS
    # ─────────────────────────────────────────
    @model_validator(mode="after")
    def validate_response_logic(self):

        # ── IMPOSSIBLE BUDGET DETECTION ────────
        # This is the T08 fix.
        # When a mom asks for something that cannot fit her budget
        # (e.g. double stroller under 200 AED, cheapest is 499 AED),
        # the model should:
        #   - Set budget_feasible = False
        #   - Set refused = True
        #   - Set refusal_reason explaining the minimum price
        #   - Return empty recommendations []
        # This is honest uncertainty handling, not a failure.
        is_impossible_budget = (
            self.budget_feasible is False and
            self.total_budget_aed is not None and
            len(self.recommendations) == 0
        )

        # ── REFUSAL RULES ──────────────────────
        if self.refused:
            if len(self.recommendations) > 0:
                raise ValueError(
                    "Refused responses must not include recommendations"
                )
            if not self.refusal_reason:
                raise ValueError(
                    "Refused responses must include refusal_reason"
                )

        # Non-refused AND not an impossible budget = must have recommendations
        elif not is_impossible_budget and len(self.recommendations) == 0:
            raise ValueError(
                "Non-refused responses must include recommendations. "
                "For impossible budgets: set budget_feasible=False, refused=True, "
                "and include refusal_reason with the minimum available price."
            )

        # Impossible budget must always explain itself
        if is_impossible_budget and not self.refusal_reason:
            raise ValueError(
                "Impossible budget responses must include refusal_reason "
                "explaining the minimum available price in the catalog."
            )

        # ── CLARIFICATION ──────────────────────
        if self.needs_clarification and not self.clarification_question:
            raise ValueError(
                "clarification_question required when needs_clarification is True"
            )

        # ── BUDGET FEASIBILITY CONSISTENCY ─────
        if (
            self.total_budget_aed is not None and
            self.total_cost_aed is not None
        ):
            # Cannot say feasible when over budget
            if (
                self.total_cost_aed > self.total_budget_aed and
                self.budget_feasible is True
            ):
                raise ValueError(
                    "budget_feasible cannot be True when total_cost exceeds total_budget"
                )

            # Cannot say infeasible when under budget AND recs exist
            if (
                self.total_cost_aed <= self.total_budget_aed and
                self.budget_feasible is False and
                len(self.recommendations) > 0
            ):
                raise ValueError(
                    "budget_feasible should not be False when cost is within budget "
                    "and recommendations are present"
                )

        # ── BUDGET ALLOCATION SUM ──────────────
        if (
            self.budget_allocations and
            self.total_budget_aed is not None
        ):
            allocation_sum = sum(
                alloc.allocated_aed for alloc in self.budget_allocations
            )
            # 1% tolerance for floating point rounding
            if allocation_sum > self.total_budget_aed * 1.01:
                raise ValueError(
                    f"Budget allocations ({allocation_sum:.2f} AED) exceed "
                    f"total budget ({self.total_budget_aed:.2f} AED)"
                )

        # ── ARABIC CONSISTENCY ─────────────────
        if self.language == Language.AR:
            if (
                not self.confidence_note_ar and
                not self.refused and
                not is_impossible_budget
            ):
                raise ValueError(
                    "Arabic responses must include confidence_note_ar"
                )

        return self

    # ─────────────────────────────────────────
    # HELPER METHODS
    # ─────────────────────────────────────────
    def is_valid_response(self) -> bool:
        """
        A response is valid when ANY of:
        1. Explicit refusal (refused=True) with a refusal_reason
        2. Impossible budget (budget_feasible=False, empty recs) with refusal_reason
        3. At least one recommendation returned
        """
        # Case 1: explicit refusal
        if self.refused:
            return bool(
                self.refusal_reason and
                len(self.refusal_reason.strip()) > 0
            )

        # Case 2: impossible budget — honest "I can't help at this price"
        if (
            self.budget_feasible is False and
            self.total_budget_aed is not None and
            len(self.recommendations) == 0
        ):
            return bool(
                self.refusal_reason and
                len(self.refusal_reason.strip()) > 0
            )

        # Case 3: normal recommendation response
        return len(self.recommendations) > 0

    def total_within_budget(self) -> Optional[bool]:
        """
        Returns:
        - True  → total cost is within budget
        - False → total cost exceeds budget
        - None  → budget not specified
        """
        if (
            self.total_budget_aed is not None and
            self.total_cost_aed is not None
        ):
            return self.total_cost_aed <= self.total_budget_aed
        return None

    def summary(self) -> str:
        """
        One-line human-readable summary for logging and eval output.
        """
        if self.refused:
            return f"[REFUSED] {self.refusal_reason}"

        if (
            self.budget_feasible is False and
            not self.recommendations
        ):
            return f"[IMPOSSIBLE BUDGET] {self.refusal_reason}"

        recs = ", ".join(
            f"{r.product_name} ({r.price_aed} AED)"
            for r in self.recommendations
        )
        budget_info = ""
        if self.total_budget_aed and self.total_cost_aed:
            budget_info = (
                f" | {self.total_cost_aed}/{self.total_budget_aed} AED"
            )
        return (
            f"[{self.confidence.value.upper()}] {recs}{budget_info}"
        )
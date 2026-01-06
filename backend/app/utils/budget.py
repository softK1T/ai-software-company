"""Budget tracking and enforcement utilities."""
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

# Token pricing (as of Jan 2024)
TOKEN_PRICES = {
    "gpt-4o": {"input": 5e-6, "output": 1.5e-5},  # per token
    "gpt-4o-mini": {"input": 1.5e-7, "output": 6e-7},
    "o3": {"input": 2e-5, "output": 8e-5},
}


class BudgetTracker:
    """Track token usage and costs across a run."""

    def __init__(self, max_usd: float, max_tokens: int):
        self.max_usd = max_usd
        self.max_tokens = max_tokens
        self.spent_usd = 0.0
        self.spent_tokens_input = 0
        self.spent_tokens_output = 0

    @property
    def total_tokens(self) -> int:
        """Total tokens used."""
        return self.spent_tokens_input + self.spent_tokens_output

    @property
    def usd_remaining(self) -> float:
        """USD remaining in budget."""
        return max(0.0, self.max_usd - self.spent_usd)

    @property
    def tokens_remaining(self) -> int:
        """Tokens remaining in budget."""
        return max(0, self.max_tokens - self.total_tokens)

    @property
    def is_budget_exceeded(self) -> bool:
        """Check if budget exceeded."""
        return self.spent_usd >= self.max_usd or self.total_tokens >= self.max_tokens

    def add_usage(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
    ) -> Dict[str, float]:
        """Record token usage and calculate cost.
        
        Returns:
            Dictionary with cost breakdown
        """
        prices = TOKEN_PRICES.get(model, TOKEN_PRICES["gpt-4o-mini"])

        cost_input = input_tokens * prices["input"]
        cost_output = output_tokens * prices["output"]
        cost_total = cost_input + cost_output

        self.spent_tokens_input += input_tokens
        self.spent_tokens_output += output_tokens
        self.spent_usd += cost_total

        result = {
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "cost_usd": round(cost_total, 6),
            "cost_breakdown": {
                "input_cost": round(cost_input, 6),
                "output_cost": round(cost_output, 6),
            },
        }

        logger.info(f"💰 Token usage: {result['total_tokens']} tokens (${result['cost_usd']:.6f})")
        return result

    def get_status(self) -> Dict:
        """Get current budget status."""
        return {
            "spent_usd": round(self.spent_usd, 2),
            "max_usd": self.max_usd,
            "usd_remaining": round(self.usd_remaining, 2),
            "usd_percent_used": round((self.spent_usd / self.max_usd * 100), 1) if self.max_usd > 0 else 0,
            "spent_tokens": self.total_tokens,
            "max_tokens": self.max_tokens,
            "tokens_remaining": self.tokens_remaining,
            "tokens_percent_used": round((self.total_tokens / self.max_tokens * 100), 1) if self.max_tokens > 0 else 0,
            "is_exceeded": self.is_budget_exceeded,
        }

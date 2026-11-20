from discountstrategy import DiscountStrategy


class NoDiscount(DiscountStrategy):
    """Default strategy: the total is returned unchanged."""

    def apply(self, total: float) -> float:
        return total

    def describe(self) -> str:
        return "No discount"

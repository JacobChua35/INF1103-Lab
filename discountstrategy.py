from abc import ABC, abstractmethod


class DiscountStrategy(ABC):
    """STRATEGY pattern: the common interface for every discount.

    Order only ever calls apply(), so it never needs to know which discount
    it has. A new discount is a new subclass - Order does not change (OCP).
    """

    @abstractmethod
    def apply(self, total: float) -> float:
        """Take an order total and return the discounted total."""

    def describe(self) -> str:
        """Short label used when displaying an order. Regular (not abstract)
        method, so apply() stays the only method a strategy MUST provide."""
        return type(self).__name__

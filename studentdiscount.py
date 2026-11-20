from discountstrategy import DiscountStrategy


class StudentDiscount(DiscountStrategy):
    """Section 2.4 - the fourth strategy, added WITHOUT changing Order.

    Fixed 5% student discount. Only this new file was needed; Order,
    OrderLine and the other strategies were not edited.
    """

    RATE: float = 5.0  # percent

    def apply(self, total: float) -> float:
        return total * (1 - self.RATE / 100)

    def describe(self) -> str:
        return f"Student discount ({self.RATE:g}% off)"

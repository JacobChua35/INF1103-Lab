from discountstrategy import DiscountStrategy
from nodiscount import NoDiscount
from orderline import OrderLine
from product import Product


class Order:
    """A customer order made up of OrderLine objects.

    COMPOSITION with OrderLine: the Order CREATES its own OrderLine objects
    inside add_order_line() and manages them. OrderLines are never created
    outside and passed in, and are never handed out to be moved to another
    Order. If the Order is removed, its OrderLines are removed with it.

    STRATEGY pattern / ASSOCIATION with DiscountStrategy: the Order USES a
    discount but the discount is not part of it. The strategy is passed in
    (or swapped with set_discount()), and one strategy object can be shared
    by many orders. Multiplicity: Order 0..* ---- 1 DiscountStrategy.
    Order contains NO if/elif logic about discount types.
    """

    def __init__(self, order_id: str, discount: DiscountStrategy | None = None) -> None:
        self.__order_id: str = order_id
        self.__order_lines: list[OrderLine] = []
        # Default strategy when none is given
        self.__discount: DiscountStrategy = discount if discount is not None else NoDiscount()

    def get_order_id(self) -> str:
        return self.__order_id

    def get_discount(self) -> DiscountStrategy:
        return self.__discount

    def set_discount(self, discount: DiscountStrategy) -> None:
        """Swap the discount strategy at any time."""
        self.__discount = discount

    def add_order_line(self, product: Product, quantity: int) -> None:
        """Create a new OrderLine internally and add it to this order.
        OrderLine validates the quantity; if it raises ValueError, nothing
        is added to the order."""
        order_line = OrderLine(product, quantity)  # Order creates the part
        self.__order_lines.append(order_line)

    def remove_order_line(self, product_id: str) -> bool:
        """Remove the line for this product. Returns False if not found."""
        for order_line in self.__order_lines:
            if order_line.get_product().get_product_id() == product_id:
                self.__order_lines.remove(order_line)
                return True
        return False

    def get_order_lines(self) -> tuple[OrderLine, ...]:
        """Read-only view of the lines (a tuple cannot be appended to), so
        lines cannot be added from outside or moved into another Order."""
        return tuple(self.__order_lines)

    def get_line_count(self) -> int:
        return len(self.__order_lines)

    def calculate_subtotal(self) -> float:
        """Sum of each OrderLine's own subtotal, before any discount."""
        return sum(line.calculate_subtotal() for line in self.__order_lines)

    def calculate_total(self) -> float:
        """Subtotal passed to the strategy - the strategy decides the discount."""
        return self.__discount.apply(self.calculate_subtotal())

    def display_order(self) -> None:
        print("--------------------------")
        print(f"Order ID: {self.__order_id}")
        if not self.__order_lines:
            print("No order lines.")
        for order_line in self.__order_lines:
            order_line.display_information()
        print(f"Subtotal: ${self.calculate_subtotal():.2f}")
        print(f"Discount: {self.__discount.describe()}")
        print(f"Order Total: ${self.calculate_total():.2f}")
        print("--------------------------")

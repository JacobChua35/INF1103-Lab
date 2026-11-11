from product import Product


class OrderLine:
    """One product and the quantity of it requested in an Order.

    COMPOSITION: an OrderLine is a PART of exactly one Order. It is only ever
    created inside Order.add_order_line() and is never passed to, shared with
    or transferred to another Order. When its Order goes away, it goes too.

    ASSOCIATION with Product: the OrderLine only refers to a Product. It does
    not own it - the Product can still exist in an Inventory or other orders.
    """

    def __init__(self, product: Product, quantity: int) -> None:
        self.__product: Product = product  # reference only, not owned
        self.__quantity: int = quantity

    def get_product(self) -> Product:
        return self.__product

    def get_quantity(self) -> int:
        return self.__quantity

    def calculate_subtotal(self) -> float:
        """Return product price x quantity."""
        return self.__product.get_price() * self.__quantity

    def display_information(self) -> None:
        print(f"{self.__product.get_product_id()} | {self.__product.get_name()} | "
              f"${self.__product.get_price():.2f} x {self.__quantity} = "
              f"${self.calculate_subtotal():.2f}")

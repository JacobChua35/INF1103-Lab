from product import Product
from canbeshipped import CanBeShipped


class PhysicalProduct(Product, CanBeShipped):
    """A product that physically exists and must be shipped.

    Single class inheritance: PhysicalProduct IS-A Product.
    It also implements (realises) the CanBeShipped interface.
    """

    # Simple shipping rule: flat fee + cost per kilogram
    BASE_SHIPPING_FEE = 5.00
    RATE_PER_KG = 2.00

    def __init__(self, product_id, name, price, stock, weight):
        super().__init__(product_id, name, price, stock)  # reuse Product constructor
        self.__weight = weight  # in kilograms

    def get_weight(self):
        return self.__weight

    # ---------- Overridden methods ----------
    def display_information(self):
        super().display_information()  # common info comes from Product
        print(f" | Type: Physical | Weight: {self.__weight:.2f} kg")

    def _display_extra_details(self):
        print("Type: Physical")
        print(f"Weight: {self.__weight:.2f} kg")

    def to_dict(self):
        data = {"Type": "physical"}
        data.update(super().to_dict())
        data["Weight"] = self.__weight
        return data

    # ---------- Abstract method from Product ----------
    def get_fulfilment_info(self):
        return "Requires physical shipping to the customer's address."

    # ---------- Interface method from CanBeShipped ----------
    def calculate_shipping_cost(self):
        return self.BASE_SHIPPING_FEE + self.RATE_PER_KG * self.__weight
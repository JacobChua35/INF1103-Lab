from product import Product
from canbeshipped import CanBeShipped
from supplier import Supplier


class PhysicalProduct(Product, CanBeShipped):
    """A product that physically exists and must be shipped.

    Single class inheritance: PhysicalProduct IS-A Product.
    It also implements (realises) the CanBeShipped interface.
    It keeps every expectation of Product (e.g. update_stock is inherited
    unchanged), so it can be used anywhere a Product is expected (LSP).
    """

    # Simple shipping rule: flat fee + cost per kilogram
    BASE_SHIPPING_FEE: float = 5.00
    RATE_PER_KG: float = 2.00

    def __init__(self, product_id: str, name: str, price: float, stock: int,
                 supplier: Supplier, weight: float) -> None:
        # reuse Product constructor and pass the Supplier up with super()
        super().__init__(product_id, name, price, stock, supplier)
        self.__weight: float = weight  # in kilograms

    def get_weight(self) -> float:
        return self.__weight

    # ---------- Overridden methods ----------
    def display_information(self) -> None:
        super().display_information()  # common info comes from Product
        print(f" | Type: Physical | Weight: {self.__weight:.2f} kg")

    def _display_extra_details(self) -> None:
        print("Type: Physical")
        print(f"Weight: {self.__weight:.2f} kg")
        # Shipping cost is shown here (polymorphism), so callers never need
        # isinstance() checks to decide whether to print it.
        print(f"Shipping Cost: ${self.calculate_shipping_cost():.2f}")

    def to_dict(self) -> dict[str, str | float | int]:
        data: dict[str, str | float | int] = {"Type": "physical"}
        data.update(super().to_dict())
        data["Weight"] = self.__weight
        return data

    # ---------- Abstract method from Product ----------
    def get_fulfilment_info(self) -> str:
        return "Requires physical shipping to the customer's address."

    # ---------- Interface method from CanBeShipped ----------
    def calculate_shipping_cost(self) -> float:
        return self.BASE_SHIPPING_FEE + self.RATE_PER_KG * self.__weight

from digitalproduct import DigitalProduct
from physicalproduct import PhysicalProduct
from product import Product
from supplier import Supplier


class ProductFactory:
    """FACTORY pattern: the ONE place that decides which Product subclass
    to create. The rest of the program asks the factory and only works with
    the returned Product type (lower coupling, polymorphism).

    Adding a new product type (e.g. BundleProduct) still means editing
    create() - so the factory itself is not closed for modification (OCP).
    That is an accepted trade-off for a small system: the change is in one
    place instead of every place that used to create products.

    The factory creates products but does not store them (dependency,
    shown in UML as a dashed «creates» arrow to Product).
    """

    @staticmethod
    def create(product_type: str, product_id: str, name: str, price: float,
               stock_quantity: int, supplier: Supplier,
               weight: float = 0.0, download_size: float = 0.0) -> Product:
        """Return a new Product of the requested type.

        weight is used only for physical products (kg) and download_size
        only for digital products (MB). Raises ValueError for an unknown
        type, or if the product's own validation fails (price/stock)."""
        kind = product_type.strip().lower()
        if kind == "physical":
            return PhysicalProduct(product_id, name, price, stock_quantity, supplier, weight)
        elif kind == "digital":
            return DigitalProduct(product_id, name, price, stock_quantity, supplier, download_size)
        else:
            raise ValueError(f"Unknown product type: {product_type}")

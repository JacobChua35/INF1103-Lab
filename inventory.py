from product import Product


class Inventory:
    """Manages the COLLECTION of Product objects (Single Responsibility).

    AGGREGATION with Product: an Inventory is a whole made of Product parts,
    but it does NOT create them or control their lifecycle. Products are
    created elsewhere, added here, and can be removed or moved to another
    Inventory without being destroyed.

    The collection is typed with the base class Product (not PhysicalProduct
    or DigitalProduct), so it can hold any Product subclass (LSP).
    """

    def __init__(self) -> None:
        self.__products: list[Product] = []

    def add_product(self, product: Product) -> bool:
        """Add an existing Product. Returns False if the ID already exists."""
        if self.find_product(product.get_product_id()) is not None:
            return False
        self.__products.append(product)
        return True

    def remove_product(self, product_id: str) -> Product | None:
        """Remove the Product reference from this inventory.

        The Product object itself is NOT destroyed: it is returned so the
        caller can keep using it or add it to another Inventory.
        Returns None if no product has this ID."""
        product = self.find_product(product_id)
        if product is not None:
            self.__products.remove(product)
        return product

    def find_product(self, product_id: str) -> Product | None:
        """Return the Product with this ID, or None if not found."""
        for product in self.__products:
            if product.get_product_id() == product_id:
                return product
        return None

    def display_all_products(self) -> None:
        """Ask each Product to display itself (polymorphism - no type checks)."""
        print("---------------------------------------------------------------------")
        if not self.__products:
            print("No products in inventory.")
        for product in self.__products:
            product.display_information()
        print("---------------------------------------------------------------------")

    def get_all_products(self) -> list[Product]:
        """Return a copy of the list (used by main when saving)."""
        return list(self.__products)

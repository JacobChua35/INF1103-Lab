class Inventory:
    """Manages the COLLECTION of Product objects (Single Responsibility)."""

    def __init__(self):
        self.__products = []

    def search_product(self, product_id):
        """Return the Product with this ID, or None if not found."""
        for product in self.__products:
            if product.get_product_id() == product_id:
                return product
        return None

    def add_product(self, product):
        """Add a Product. Returns False if the ID already exists."""
        if self.search_product(product.get_product_id()) is not None:
            return False
        self.__products.append(product)
        return True


    def display_all(self):
        print("---------------------------------------------------------------------")
        if not self.__products:
            print("No products in inventory.")
        for product in self.__products:
            product.display_information()
        print("---------------------------------------------------------------------")

    def get_all_products(self):
        """Return a copy of the list (used by main when saving)."""
        return list(self.__products)
class Product:
    """Represents and manages ONE product (Single Responsibility)."""

    def __init__(self, product_id, name, price, stock):
        # Private attributes (encapsulation)
        self.__product_id = product_id
        self.__name = name
        self.__price = price
        self.__stock = stock

    # Getter: Inventory needs the ID to search / check duplicates
    def get_product_id(self):
        return self.__product_id

    def update_stock(self, quantity):
        """Set a new stock quantity. Rejects negative values.
        Returns True if updated, False if invalid."""
        if quantity < 0:
            return False
        self.__stock = quantity
        return True

    def display_information(self):
        """Print this product on one line (used by Display All)."""
        print(f"ID: {self.__product_id} | Name: {self.__name} | "
              f"Price: ${self.__price:.2f} | Stock: {self.__stock}")

    def display_details(self):
        """Print this product in block format (used by Search / Update)."""
        print("--------------------------")
        print(f"ID: {self.__product_id}")
        print(f"Name: {self.__name}")
        print(f"Price: ${self.__price:.2f}")
        print(f"Stock: {self.__stock}")
        print("--------------------------")

    def to_dict(self):
        """Convert to a dictionary so main can save it to JSON."""
        return {
            "ID": self.__product_id,
            "Name": self.__name,
            "Price": self.__price,
            "Stock": self.__stock,
        }
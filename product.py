from abc import ABC, abstractmethod


class Product(ABC):
    """Abstract base class for ONE product (Single Responsibility).

    Holds the data and behaviour that ALL products share. Because it inherits
    from ABC and has an abstract method, it cannot be instantiated directly:
    every product must be either a PhysicalProduct or a DigitalProduct.
    """

    def __init__(self, product_id, name, price, stock):
        # Private attributes (encapsulation)
        self.__product_id = product_id
        self.__name = name
        self.__price = price
        self.__stock = stock

    # Gives back the ID (used for searching)
    def get_product_id(self):
        return self.__product_id

    #Changes the stock; returns False if the number is negative
    def update_stock(self, quantity):
        """Set a new stock quantity. Rejects negative values.
        Returns True if updated, False if invalid."""
        if quantity < 0:
            return False
        self.__stock = quantity
        return True

    @abstractmethod
    def get_fulfilment_info(self):
        """Return a message describing how this product reaches the customer.
        No implementation here - every subclass MUST provide its own."""

    #Prints the common one-line info (used by Display All)
    def display_information(self):
        """Print the common product information on one line (used by Display All).
        Subclasses override this, call super() first, then add their own info."""
        print(f"ID: {self.__product_id} | Name: {self.__name} | "
              f"Price: ${self.__price:.2f} | Stock: {self.__stock}", end="")

    #Prints the info as a block (used by Search and Update)
    def display_details(self):
        """Print this product in block format (used by Search / Update)."""
        print("--------------------------")
        print(f"ID: {self.__product_id}")
        print(f"Name: {self.__name}")
        print(f"Price: ${self.__price:.2f}")
        print(f"Stock: {self.__stock}")
        self._display_extra_details()
        print(f"Fulfilment: {self.get_fulfilment_info()}")
        print("--------------------------")

    #An empty slot that the child classes fill with their own lines
    def _display_extra_details(self):
        """Hook for subclasses to print their own extra lines inside the
        block. Does nothing by default (regular, non-abstract method)."""
        pass

    #Turns the product into a dictionary so it can be saved to JSON
    def to_dict(self):
        """Convert the common attributes to a dictionary so main can save
        them to JSON. Subclasses extend this with their type and extra data."""
        return {
            "ID": self.__product_id,
            "Name": self.__name,
            "Price": self.__price,
            "Stock": self.__stock,
        }
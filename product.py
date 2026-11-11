from abc import ABC, abstractmethod

from supplier import Supplier


class Product(ABC):
    """Abstract base class for ONE product (Single Responsibility).

    Holds the data and behaviour that ALL products share. Because it inherits
    from ABC and has an abstract method, it cannot be instantiated directly:
    every product must be either a PhysicalProduct or a DigitalProduct.

    Relationships:
    - ASSOCIATION with Supplier: the Supplier is created elsewhere and passed
      in. Product only stores a reference; it does not create or own it.

    Expectations every subclass must keep (Liskov Substitution Principle):
    - update_stock() accepts any quantity >= 0, rejects negatives, and
      returns True/False. No subclass may raise or change this meaning.
    - get_fulfilment_info() always returns a str.
    - display_information() / display_details() print and return None.
    """

    def __init__(self, product_id: str, name: str, price: float,
                 stock: int, supplier: Supplier) -> None:
        # Private attributes (encapsulation)
        self.__product_id: str = product_id
        self.__name: str = name
        self.__price: float = price
        self.__stock: int = stock
        self.__supplier: Supplier = supplier  # association (reference only)

    # ---------- Getters ----------
    def get_product_id(self) -> str:
        return self.__product_id

    def get_name(self) -> str:
        return self.__name

    def get_price(self) -> float:
        return self.__price

    def get_stock(self) -> int:
        return self.__stock

    def get_supplier(self) -> Supplier:
        return self.__supplier

    # Changes the stock; returns False if the number is negative
    def update_stock(self, quantity: int) -> bool:
        """Set a new stock quantity. Rejects negative values.
        Returns True if updated, False if invalid."""
        if quantity < 0:
            return False
        self.__stock = quantity
        return True

    @abstractmethod
    def get_fulfilment_info(self) -> str:
        """Return a message describing how this product reaches the customer.
        No implementation here - every subclass MUST provide its own."""

    # Prints the common one-line info (used by Display All)
    def display_information(self) -> None:
        """Print the common product information on one line (used by Display All).
        Subclasses override this, call super() first, then add their own info."""
        print(f"ID: {self.__product_id} | Name: {self.__name} | "
              f"Price: ${self.__price:.2f} | Stock: {self.__stock} | "
              f"Supplier: {self.__supplier.get_name()}", end="")

    # Prints the info as a block (used by Search and Update)
    def display_details(self) -> None:
        """Print this product in block format (used by Search / Update)."""
        print("--------------------------")
        print(f"ID: {self.__product_id}")
        print(f"Name: {self.__name}")
        print(f"Price: ${self.__price:.2f}")
        print(f"Stock: {self.__stock}")
        self._display_extra_details()
        print(f"Fulfilment: {self.get_fulfilment_info()}")
        print("Supplied by:")
        self.__supplier.display_information()  # ask the Supplier to show itself
        print("--------------------------")

    # An empty slot that the child classes fill with their own lines
    def _display_extra_details(self) -> None:
        """Hook for subclasses to print their own extra lines inside the
        block. Does nothing by default (regular, non-abstract method)."""
        pass

    # Turns the product into a dictionary so it can be saved to JSON
    def to_dict(self) -> dict[str, str | float | int]:
        """Convert the common attributes to a dictionary so main can save
        them to JSON. Only the supplier's ID is saved, because the Supplier
        is a separate object that is saved on its own (association)."""
        return {
            "ID": self.__product_id,
            "Name": self.__name,
            "Price": self.__price,
            "Stock": self.__stock,
            "SupplierID": self.__supplier.get_supplier_id(),
        }

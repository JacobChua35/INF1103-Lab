class Supplier:
    """A company that supplies products.

    ASSOCIATION with Product: a Supplier is NOT part of a Product and a
    Product is NOT part of a Supplier. Both are created independently and
    can exist without each other. A Product simply keeps a reference to
    the Supplier it came from ("knows-about" relationship).
    """

    def __init__(self, supplier_id: str, name: str, contact_email: str) -> None:
        # Private attributes (encapsulation)
        self.__supplier_id: str = supplier_id
        self.__name: str = name
        self.__contact_email: str = contact_email

    def get_supplier_id(self) -> str:
        return self.__supplier_id

    def get_name(self) -> str:
        return self.__name

    def get_contact_email(self) -> str:
        return self.__contact_email

    def display_information(self) -> None:
        """Print this supplier's details on one line."""
        print(f"Supplier ID: {self.__supplier_id} | Name: {self.__name} | "
              f"Email: {self.__contact_email}")

    def to_dict(self) -> dict[str, str]:
        """Convert the supplier to a dictionary so main can save it to JSON."""
        return {
            "SupplierID": self.__supplier_id,
            "Name": self.__name,
            "ContactEmail": self.__contact_email,
        }

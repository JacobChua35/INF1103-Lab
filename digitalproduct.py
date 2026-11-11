from product import Product
from supplier import Supplier


class DigitalProduct(Product):
    """A product delivered through a download link.

    DigitalProduct IS-A Product. It does NOT implement CanBeShipped,
    because digital products are never physically shipped.
    It keeps every expectation of Product: update_stock() is inherited
    unchanged (stock = number of licences/keys available), so it can be
    used anywhere a Product is expected (LSP).
    """

    def __init__(self, product_id: str, name: str, price: float, stock: int,
                 supplier: Supplier, download_size: float) -> None:
        # reuse Product constructor and pass the Supplier up with super()
        super().__init__(product_id, name, price, stock, supplier)
        self.__download_size: float = download_size  # in megabytes

    def get_download_size(self) -> float:
        return self.__download_size

    # ---------- Overridden methods ----------
    def display_information(self) -> None:
        super().display_information()  # common info comes from Product
        print(f" | Type: Digital | Download Size: {self.__download_size:.2f} MB")

    def _display_extra_details(self) -> None:
        print("Type: Digital")
        print(f"Download Size: {self.__download_size:.2f} MB")

    def to_dict(self) -> dict[str, str | float | int]:
        data: dict[str, str | float | int] = {"Type": "digital"}
        data.update(super().to_dict())
        data["DownloadSize"] = self.__download_size
        return data

    # ---------- Abstract method from Product ----------
    def get_fulfilment_info(self) -> str:
        return "Delivered digitally via a download link."

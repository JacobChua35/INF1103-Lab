from product import Product


class DigitalProduct(Product):
    """A product delivered through a download link.

    DigitalProduct IS-A Product. It does NOT implement CanBeShipped,
    because digital products are never physically shipped.
    """

    def __init__(self, product_id, name, price, stock, download_size):
        super().__init__(product_id, name, price, stock)  # reuse Product constructor
        self.__download_size = download_size  # in megabytes

    def get_download_size(self):
        return self.__download_size

    # ---------- Overridden methods ----------
    def display_information(self):
        super().display_information()  # common info comes from Product
        print(f" | Type: Digital | Download Size: {self.__download_size:.2f} MB")

    def _display_extra_details(self):
        print("Type: Digital")
        print(f"Download Size: {self.__download_size:.2f} MB")

    def to_dict(self):
        data = {"Type": "digital"}
        data.update(super().to_dict())
        data["DownloadSize"] = self.__download_size
        return data

    # ---------- Abstract method from Product ----------
    def get_fulfilment_info(self):
        return "Delivered digitally via a download link."
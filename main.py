import json
import os
import re

from inventory import Inventory
from physicalproduct import PhysicalProduct
from digitalproduct import DigitalProduct
from canbeshipped import CanBeShipped

FILENAME = "inventory.json"


# ================= File handling (stays in main, not in the classes) =================
def create_product_from_dict(item):
    """Use the saved "Type" identifier to rebuild the correct subclass.
    Returns None if the type is unknown."""
    # Old Lab 5/6 data had no "Type" and stored price/stock as text
    # (e.g. "$1200.00", "15"), so default to physical and convert to numbers.
    product_type = str(item.get("Type", "physical")).lower()
    price = float(str(item["Price"]).replace("$", ""))
    stock = int(item["Stock"])

    if product_type == "physical":
        return PhysicalProduct(item["ID"], item["Name"], price, stock,
                               float(item.get("Weight", 0)))
    if product_type == "digital":
        return DigitalProduct(item["ID"], item["Name"], price, stock,
                              float(item.get("DownloadSize", 0)))

    print(f"Skipping {item.get('ID')}: unknown product type '{product_type}'.")
    return None


def load_inventory():
    """Load products from the JSON file into an Inventory object."""
    inventory = Inventory()
    if os.path.exists(FILENAME):
        with open(FILENAME, "r") as f:
            data = json.load(f)
        for item in data:
            product = create_product_from_dict(item)
            if product is not None:
                inventory.add_product(product)
    return inventory


def save_inventory(inventory):
    """Convert every Product to a dict (each includes its Type) and save to JSON."""
    data = [product.to_dict() for product in inventory.get_all_products()]
    with open(FILENAME, "w") as f:
        json.dump(data, f, indent=4)
    print("Inventory saved successfully.")


# ================= Input helpers =================
def get_product_id():
    """Ask for an ID and check the PXXX format. Returns None if invalid."""
    product_id = input("Enter Product ID (format: P001): ").strip().upper()
    if not re.fullmatch(r"P\d{3}", product_id):
        print("Invalid Product ID format. Please use the format PXXX (e.g., P001).")
        return None
    return product_id


def get_number(prompt, number_type):
    """Keep asking until the user types a valid non-negative number."""
    while True:
        try:
            value = number_type(input(prompt).strip().replace("$", ""))
            if value >= 0:
                return value
            print("Value cannot be negative.")
        except ValueError:
            print("Please enter a valid number.")


def get_product_type():
    """Ask whether the new product is physical or digital."""
    while True:
        print("Select Product Type:")
        print("1. Physical Product")
        print("2. Digital Product")
        choice = input("Enter your choice (1-2): ").strip()
        if choice == "1":
            return "physical"
        if choice == "2":
            return "digital"
        print("Invalid choice. Please enter 1 or 2.")


# ================= Menu =================
def menu():
    print("=======================================")
    print("INVENTORY MANAGEMENT SYSTEM")
    print("=======================================")
    print("-------MENU-------")
    print("1. Display All Products")
    print("2. Add Product")
    print("3. Update Stock")
    print("4. Search Product")
    print("5. Save Inventory")
    print("6. Exit")
    print("------------------")


def show_product(product):
    """Show a product's details, plus shipping cost if it can be shipped."""
    product.display_details()
    if isinstance(product, CanBeShipped):
        print(f"Shipping Cost: ${product.calculate_shipping_cost():.2f}")


def add_product(inventory):
    print("Add New Product")
    while True:
        product_id = get_product_id()
        if product_id is None:
            continue
        if inventory.search_product(product_id) is not None:
            print("Product ID already exists. Please use a unique ID.")
        else:
            break

    product_type = get_product_type()
    name = input("Enter Product Name: ").strip()
    price = get_number("Enter Product Price: ", float)
    stock = get_number("Enter Product Stock Quantity: ", int)

    if product_type == "physical":
        weight = get_number("Enter Product Weight (kg): ", float)
        product = PhysicalProduct(product_id, name, price, stock, weight)
    else:
        download_size = get_number("Enter Download Size (MB): ", float)
        product = DigitalProduct(product_id, name, price, stock, download_size)

    inventory.add_product(product)
    print()
    print("Product added successfully.")


def update_stock(inventory):
    print("Update Stock")
    product_id = get_product_id()
    if product_id is None:
        return

    product = inventory.search_product(product_id)
    if product is None:
        print("Product not found.")
        return

    print("Product Found:")
    product.display_details()
    new_stock = get_number("Enter New Stock Quantity: ", int)
    product.update_stock(new_stock)
    print()
    print("Stock updated successfully.")


def search_product(inventory):
    print("Search Product")
    product_id = get_product_id()
    if product_id is None:
        return

    product = inventory.search_product(product_id)
    if product is None:
        print()
        print("Product not found.")
    else:
        print("Product Found:")
        show_product(product)


def main():
    inventory = load_inventory()

    while True:
        menu()
        choice = input("Enter your choice (1-6): ").strip()

        if choice == "1":
            inventory.display_all()
        elif choice == "2":
            add_product(inventory)
        elif choice == "3":
            update_stock(inventory)
        elif choice == "4":
            search_product(inventory)
        elif choice == "5":
            save_inventory(inventory)
        elif choice == "6":
            save_inventory(inventory)  # Save inventory before exiting
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
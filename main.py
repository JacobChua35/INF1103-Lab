import json
import os
import re

from inventory import Inventory
from order import Order
from product import Product
from physicalproduct import PhysicalProduct
from digitalproduct import DigitalProduct
from supplier import Supplier

FILENAME = "inventory.json"
SUPPLIER_FILENAME = "suppliers.json"

# Used for old Lab 5-7 data that was saved before products had a supplier
UNKNOWN_SUPPLIER_ID = "S000"


# ================= File handling (stays in main, not in the classes) =================
def load_suppliers() -> dict[str, Supplier]:
    """Load suppliers from JSON. Suppliers are created independently of
    products (association), so they live in their own file."""
    suppliers: dict[str, Supplier] = {}
    if os.path.exists(SUPPLIER_FILENAME):
        with open(SUPPLIER_FILENAME, "r") as f:
            data = json.load(f)
        for item in data:
            supplier = Supplier(item["SupplierID"], item["Name"], item["ContactEmail"])
            suppliers[supplier.get_supplier_id()] = supplier
    return suppliers


def get_unknown_supplier(suppliers: dict[str, Supplier]) -> Supplier:
    """Return the placeholder supplier, creating it the first time it is needed."""
    if UNKNOWN_SUPPLIER_ID not in suppliers:
        suppliers[UNKNOWN_SUPPLIER_ID] = Supplier(UNKNOWN_SUPPLIER_ID,
                                                  "Unknown Supplier", "N/A")
    return suppliers[UNKNOWN_SUPPLIER_ID]


def create_product_from_dict(item: dict, suppliers: dict[str, Supplier]) -> Product | None:
    """Use the saved "Type" identifier to rebuild the correct subclass and
    link it to its existing Supplier object. Returns None if the type is unknown."""
    # Old Lab 5/6 data had no "Type" and stored price/stock as text
    # (e.g. "$1200.00", "15"), so default to physical and convert to numbers.
    product_type = str(item.get("Type", "physical")).lower()
    price = float(str(item["Price"]).replace("$", ""))
    stock = int(item["Stock"])

    # Look up the SAME Supplier object, so products from one supplier share it
    supplier = suppliers.get(item.get("SupplierID", ""))
    if supplier is None:
        supplier = get_unknown_supplier(suppliers)

    if product_type == "physical":
        return PhysicalProduct(item["ID"], item["Name"], price, stock, supplier,
                               float(item.get("Weight", 0)))
    if product_type == "digital":
        return DigitalProduct(item["ID"], item["Name"], price, stock, supplier,
                              float(item.get("DownloadSize", 0)))

    print(f"Skipping {item.get('ID')}: unknown product type '{product_type}'.")
    return None


def load_inventory(suppliers: dict[str, Supplier]) -> Inventory:
    """Load products from the JSON file into an Inventory object."""
    inventory = Inventory()
    if os.path.exists(FILENAME):
        with open(FILENAME, "r") as f:
            data = json.load(f)
        for item in data:
            product = create_product_from_dict(item, suppliers)
            if product is not None:
                inventory.add_product(product)
    return inventory


def save_inventory(inventory: Inventory, suppliers: dict[str, Supplier]) -> None:
    """Save suppliers and products to their own JSON files."""
    supplier_data = [supplier.to_dict() for supplier in suppliers.values()]
    with open(SUPPLIER_FILENAME, "w") as f:
        json.dump(supplier_data, f, indent=4)

    data = [product.to_dict() for product in inventory.get_all_products()]
    with open(FILENAME, "w") as f:
        json.dump(data, f, indent=4)
    print("Inventory saved successfully.")


# ================= Input helpers =================
def get_product_id() -> str | None:
    """Ask for an ID and check the PXXX format. Returns None if invalid."""
    product_id = input("Enter Product ID (format: P001): ").strip().upper()
    if not re.fullmatch(r"P\d{3}", product_id):
        print("Invalid Product ID format. Please use the format PXXX (e.g., P001).")
        return None
    return product_id


def get_float(prompt: str) -> float:
    """Keep asking until the user types a valid non-negative decimal number."""
    while True:
        try:
            value = float(input(prompt).strip().replace("$", ""))
            if value >= 0:
                return value
            print("Value cannot be negative.")
        except ValueError:
            print("Please enter a valid number.")


def get_int(prompt: str) -> int:
    """Keep asking until the user types a valid non-negative whole number."""
    while True:
        try:
            value = int(input(prompt).strip())
            if value >= 0:
                return value
            print("Value cannot be negative.")
        except ValueError:
            print("Please enter a valid whole number.")


def get_text(prompt: str) -> str:
    """Keep asking until the user types something that is not empty."""
    while True:
        text = input(prompt).strip()
        if text:
            return text
        print("This field cannot be empty.")


def get_product_type() -> str:
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


def create_supplier(suppliers: dict[str, Supplier]) -> Supplier:
    """Create a new Supplier independently of any Product."""
    while True:
        supplier_id = input("Enter Supplier ID (format: S001): ").strip().upper()
        if not re.fullmatch(r"S\d{3}", supplier_id):
            print("Invalid Supplier ID format. Please use the format SXXX (e.g., S001).")
        elif supplier_id in suppliers:
            print("Supplier ID already exists. Please use a unique ID.")
        else:
            break
    name = get_text("Enter Supplier Name: ")
    while True:
        email = input("Enter Supplier Contact Email: ").strip()
        if re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            break
        print("Please enter a valid email address.")
    supplier = Supplier(supplier_id, name, email)
    suppliers[supplier_id] = supplier
    print("Supplier added successfully.")
    return supplier


def choose_supplier(suppliers: dict[str, Supplier]) -> Supplier:
    """Pick an existing Supplier by ID, or create a new one."""
    while True:
        print("Existing Suppliers:")
        if not suppliers:
            print("(none)")
        for supplier in suppliers.values():
            supplier.display_information()
        supplier_id = input("Enter Supplier ID (or N to add a new supplier): ").strip().upper()
        if supplier_id == "N":
            return create_supplier(suppliers)
        if supplier_id in suppliers:
            return suppliers[supplier_id]
        print("Supplier not found.")


# ================= Menu =================
def menu() -> None:
    print("=======================================")
    print("INVENTORY MANAGEMENT SYSTEM")
    print("=======================================")
    print("-------MENU-------")
    print("1. Display All Products")
    print("2. Add Product")
    print("3. Remove Product")
    print("4. Update Stock")
    print("5. Search Product")
    print("6. Create Order")
    print("7. Save Inventory")
    print("8. Exit")
    print("------------------")


def add_product(inventory: Inventory, suppliers: dict[str, Supplier]) -> None:
    print("Add New Product")
    while True:
        product_id = get_product_id()
        if product_id is None:
            continue
        if inventory.find_product(product_id) is not None:
            print("Product ID already exists. Please use a unique ID.")
        else:
            break

    product_type = get_product_type()
    name = get_text("Enter Product Name: ")
    price = get_float("Enter Product Price: ")
    stock = get_int("Enter Product Stock Quantity: ")
    supplier = choose_supplier(suppliers)  # Supplier exists before the Product

    product: Product
    if product_type == "physical":
        weight = get_float("Enter Product Weight (kg): ")
        product = PhysicalProduct(product_id, name, price, stock, supplier, weight)
    else:
        download_size = get_float("Enter Download Size (MB): ")
        product = DigitalProduct(product_id, name, price, stock, supplier, download_size)

    inventory.add_product(product)
    print()
    print("Product added successfully.")


def remove_product(inventory: Inventory) -> None:
    print("Remove Product")
    product_id = get_product_id()
    if product_id is None:
        return

    removed = inventory.remove_product(product_id)
    if removed is None:
        print("Product not found.")
    else:
        # The Product object still exists - only the inventory's reference is gone
        print(f"Product {removed.get_product_id()} ({removed.get_name()}) "
              f"removed from inventory.")


def update_stock(inventory: Inventory) -> None:
    print("Update Stock")
    product_id = get_product_id()
    if product_id is None:
        return

    product = inventory.find_product(product_id)
    if product is None:
        print("Product not found.")
        return

    print("Product Found:")
    product.display_details()
    new_stock = get_int("Enter New Stock Quantity: ")
    product.update_stock(new_stock)
    print()
    print("Stock updated successfully.")


def search_product(inventory: Inventory) -> None:
    print("Search Product")
    product_id = get_product_id()
    if product_id is None:
        return

    product = inventory.find_product(product_id)
    if product is None:
        print()
        print("Product not found.")
    else:
        print("Product Found:")
        product.display_details()  # each subclass adds its own details


def create_order(inventory: Inventory, order_count: int) -> None:
    """Build an Order. The Order creates its own OrderLines (composition)."""
    order = Order(f"O{order_count:03d}")
    print(f"Creating Order {order.get_order_id()}")
    while True:
        product_id = get_product_id()
        if product_id is not None:
            product = inventory.find_product(product_id)
            if product is None:
                print("Product not found.")
            else:
                quantity = get_int("Enter Quantity: ")
                if quantity == 0:
                    print("Quantity must be at least 1.")
                else:
                    order.add_order_line(product, quantity)
                    print("Item added to order.")
        more = input("Add another product? (Y/N): ").strip().upper()
        if more != "Y":
            break
    order.display_order()


def main() -> None:
    suppliers = load_suppliers()
    inventory = load_inventory(suppliers)
    order_count = 0

    while True:
        menu()
        choice = input("Enter your choice (1-8): ").strip()

        if choice == "1":
            inventory.display_all_products()
        elif choice == "2":
            add_product(inventory, suppliers)
        elif choice == "3":
            remove_product(inventory)
        elif choice == "4":
            update_stock(inventory)
        elif choice == "5":
            search_product(inventory)
        elif choice == "6":
            order_count += 1
            create_order(inventory, order_count)
        elif choice == "7":
            save_inventory(inventory, suppliers)
        elif choice == "8":
            save_inventory(inventory, suppliers)  # Save inventory before exiting
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()

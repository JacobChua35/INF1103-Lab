import csv
import json
import re

from bulkdiscount import BulkDiscount
from discountstrategy import DiscountStrategy
from inventory import Inventory
from nodiscount import NoDiscount
from order import Order
from percentagediscount import PercentageDiscount
from product import Product
from productfactory import ProductFactory
from studentdiscount import StudentDiscount
from supplier import Supplier

FILENAME = "inventory.json"
SUPPLIER_FILENAME = "suppliers.json"
PRODUCTS_CSV = "products.csv"

# Used for old Lab 5-7 data that was saved before products had a supplier
UNKNOWN_SUPPLIER_ID = "S000"


# ================= File handling (stays in main, not in the classes) =================
def load_suppliers() -> dict[str, Supplier]:
    """Load suppliers from JSON. A missing file is handled here (start with
    no suppliers). A corrupt file (json.JSONDecodeError) is NOT caught here:
    main() decides what to do, because continuing would risk overwriting it."""
    suppliers: dict[str, Supplier] = {}
    try:
        with open(SUPPLIER_FILENAME, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Suppliers file not found: {SUPPLIER_FILENAME}. Starting with no suppliers.")
        return suppliers

    for item in data:
        try:
            supplier = Supplier(str(item["SupplierID"]), str(item["Name"]),
                                str(item["ContactEmail"]))
        except KeyError as error:
            print(f"Skipping supplier record with missing field {error}.")
            continue
        suppliers[supplier.get_supplier_id()] = supplier
    return suppliers


def get_unknown_supplier(suppliers: dict[str, Supplier]) -> Supplier:
    """Return the placeholder supplier, creating it the first time it is needed."""
    if UNKNOWN_SUPPLIER_ID not in suppliers:
        suppliers[UNKNOWN_SUPPLIER_ID] = Supplier(UNKNOWN_SUPPLIER_ID,
                                                  "Unknown Supplier", "N/A")
    return suppliers[UNKNOWN_SUPPLIER_ID]


def create_product_from_dict(item: dict[str, str | float | int],
                             suppliers: dict[str, Supplier]) -> Product:
    """Rebuild a saved product THROUGH the ProductFactory.
    Raises KeyError (missing field) or ValueError (bad value / unknown type);
    the caller decides to skip that record."""
    # Old Lab 5/6 data had no "Type" and stored price/stock as text
    # (e.g. "$1200.00", "15"), so default to physical and convert to numbers.
    product_type = str(item.get("Type", "physical"))
    price = float(str(item["Price"]).replace("$", ""))
    stock = int(item["Stock"])

    # Look up the SAME Supplier object, so products from one supplier share it
    supplier = suppliers.get(str(item.get("SupplierID", "")))
    if supplier is None:
        supplier = get_unknown_supplier(suppliers)

    return ProductFactory.create(product_type, str(item["ID"]), str(item["Name"]),
                                 price, stock, supplier,
                                 weight=float(item.get("Weight", 0)),
                                 download_size=float(item.get("DownloadSize", 0)))


def load_inventory(suppliers: dict[str, Supplier]) -> Inventory:
    """Load products from the JSON file into an Inventory object.
    One bad record is reported and skipped; the rest still load."""
    inventory = Inventory()
    try:
        with open(FILENAME, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Inventory file not found: {FILENAME}. Starting with an empty inventory.")
        return inventory

    for item in data:
        try:
            product = create_product_from_dict(item, suppliers)
        except (KeyError, ValueError) as error:
            print(f"Skipping saved product {item.get('ID', '?')}: {error}")
            continue
        if not inventory.add_product(product):
            print(f"Skipping saved product {product.get_product_id()}: duplicate ID.")
    return inventory


def load_products(path: str, inventory: Inventory, supplier: Supplier) -> None:
    """Lab 9 Section 5.2: load products from a CSV file through the factory.

    except  -> the file does not exist (nothing to read)
    else    -> the file opened, so read the rows; each row has its own
               try/except ValueError so one bad row is skipped, not fatal
    finally -> always runs, whether the file opened or not
    """
    loaded = 0
    try:
        file = open(path, newline="")
    except FileNotFoundError:
        print(f"Products file not found: {path}")
    else:
        with file:
            reader = csv.reader(file)
            next(reader, None)  # skip the header row
            for line_number, row in enumerate(reader, start=2):
                if not row:
                    continue  # ignore blank lines
                try:
                    product_type, product_id, name, price_text, stock_text = row
                    product = ProductFactory.create(product_type, product_id, name,
                                                    float(price_text), int(stock_text),
                                                    supplier)
                except ValueError as error:
                    print(f"Skipping row {line_number} ({','.join(row)}): {error}")
                    continue
                if inventory.add_product(product):
                    loaded += 1
                else:
                    print(f"Skipping row {line_number} ({','.join(row)}): "
                          f"product ID {product_id} already exists.")
        print(f"{loaded} products loaded.")
    finally:
        print("Load attempt finished.")


def save_inventory(inventory: Inventory, suppliers: dict[str, Supplier]) -> bool:
    """Save suppliers and products to their own JSON files.
    Returns False (and tells the user) if the files cannot be written."""
    supplier_data = [supplier.to_dict() for supplier in suppliers.values()]
    data = [product.to_dict() for product in inventory.get_all_products()]
    try:
        with open(SUPPLIER_FILENAME, "w") as f:
            json.dump(supplier_data, f, indent=4)
        with open(FILENAME, "w") as f:
            json.dump(data, f, indent=4)
    except OSError as error:
        print(f"Could not save inventory: {error.strerror}")
        return False
    print("Inventory saved successfully.")
    return True


# ================= Input helpers (exception handling) =================
def get_product_id() -> str | None:
    """Ask for an ID and check the PXXX format. Returns None if invalid."""
    product_id = input("Enter Product ID (format: P001): ").strip().upper()
    if not re.fullmatch(r"P\d{3}", product_id):
        print("Invalid Product ID format. Please use the format PXXX (e.g., P001).")
        return None
    return product_id


def get_positive_float(prompt: str) -> float:
    """Lab 9 Section 5.1: keep asking until the user types a number > 0.
    float() raises ValueError for text like 'abc'; the if handles -5 / 0."""
    while True:
        try:
            value = float(input(prompt))
            if value <= 0:
                print("Please enter a number greater than zero.")
                continue
            return value
        except ValueError:
            print("Please enter a valid number, e.g. 12.50")


def get_non_negative_float(prompt: str) -> float:
    """Keep asking until the user types a valid number >= 0 (weight, size)."""
    while True:
        try:
            value = float(input(prompt))
        except ValueError:
            print("Please enter a valid number, e.g. 0.5")
            continue
        if value < 0:
            print("Value cannot be negative.")
            continue
        return value


def get_int(prompt: str) -> int:
    """Keep asking until the user types a valid non-negative whole number."""
    while True:
        try:
            value = int(input(prompt))
        except ValueError:
            print("Please enter a valid whole number, e.g. 5")
            continue
        if value < 0:
            print("Value cannot be negative.")
            continue
        return value


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


def choose_discount() -> DiscountStrategy:
    """Let the user pick a strategy. This menu is the only place that knows
    the concrete strategies; Order just receives a DiscountStrategy."""
    while True:
        print("Select Discount:")
        print("1. No Discount")
        print("2. Percentage Discount")
        print("3. Bulk Discount")
        print("4. Student Discount (5%)")
        choice = input("Enter your choice (1-4): ").strip()
        try:
            if choice == "1":
                return NoDiscount()
            if choice == "2":
                return PercentageDiscount(get_positive_float("Enter discount percentage (e.g. 10): "))
            if choice == "3":
                threshold = get_positive_float("Enter minimum order total for the discount: ")
                amount = get_positive_float("Enter discount amount: ")
                return BulkDiscount(threshold, amount)
            if choice == "4":
                return StudentDiscount()
            print("Invalid choice. Please enter 1 to 4.")
        except ValueError as error:  # strategy validation, e.g. 150%
            print(f"Invalid discount: {error}")


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
    print("7. Load Products from CSV")
    print("8. Save Inventory")
    print("9. Exit")
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
    price = get_positive_float("Enter Product Price: ")
    stock = get_int("Enter Product Stock Quantity: ")
    supplier = choose_supplier(suppliers)  # Supplier exists before the Product

    weight = 0.0
    download_size = 0.0
    if product_type == "physical":
        weight = get_non_negative_float("Enter Product Weight (kg): ")
    else:
        download_size = get_non_negative_float("Enter Download Size (MB): ")

    # Creation goes through the factory - main never names a Product subclass
    try:
        product = ProductFactory.create(product_type, product_id, name, price, stock,
                                        supplier, weight=weight, download_size=download_size)
    except ValueError as error:
        print(f"Product not added: {error}")
        return

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
    print()
    if product.update_stock(new_stock):
        print("Stock updated successfully.")
    else:
        print("Stock not updated: quantity cannot be negative.")


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
    """Build an Order. The Order creates its own OrderLines (composition)
    and the OrderLine validates the quantity (raises ValueError)."""
    order = Order(f"O{order_count:03d}")  # starts with NoDiscount()
    print(f"Creating Order {order.get_order_id()}")
    while True:
        product_id = get_product_id()
        if product_id is not None:
            product = inventory.find_product(product_id)
            if product is None:
                print("Product not found.")
            else:
                quantity = get_int("Enter Quantity: ")
                try:
                    order.add_order_line(product, quantity)
                except ValueError as error:
                    print(f"Item not added: {error}")
                else:
                    print("Item added to order.")
        more = input("Add another product? (Y/N): ").strip().upper()
        if more != "Y":
            break

    if order.get_line_count() > 0:
        print(f"Order subtotal: ${order.calculate_subtotal():.2f}")
        order.set_discount(choose_discount())  # strategy swapped at runtime
    order.display_order()


def load_products_menu(inventory: Inventory, suppliers: dict[str, Supplier]) -> None:
    print("Load Products from CSV")
    path = input(f"Enter CSV file path (press Enter for {PRODUCTS_CSV}): ").strip() or PRODUCTS_CSV
    print("Choose the supplier for these products.")
    supplier = choose_supplier(suppliers)
    load_products(path, inventory, supplier)


def main() -> None:
    # A corrupt JSON file is handled HERE, the level that can decide:
    # stop rather than continue with incomplete data and overwrite the file on exit.
    try:
        suppliers = load_suppliers()
        inventory = load_inventory(suppliers)
    except json.JSONDecodeError as error:
        print(f"A saved data file is not valid JSON (line {error.lineno}). "
              f"Fix or remove it, then run the program again.")
        return
    order_count = 0

    while True:
        menu()
        choice = input("Enter your choice (1-9): ").strip()

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
            load_products_menu(inventory, suppliers)
        elif choice == "8":
            save_inventory(inventory, suppliers)
        elif choice == "9":
            save_inventory(inventory, suppliers)  # Save inventory before exiting
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C, or input closed (e.g. docker run without -it)
        print("\nProgram stopped. Unsaved changes were not saved.")

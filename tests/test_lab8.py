"""Lab 8 tests: association, aggregation, composition, type hints, LSP and
polymorphism. Run with:  python tests/test_lab8.py

Uses its own objects only - it does not read or write inventory.json.
"""
import inspect
import sys
import typing
from pathlib import Path

# Make the project folder importable when run from the tests folder
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from typing import Callable

from canbeshipped import CanBeShipped
from digitalproduct import DigitalProduct
from inventory import Inventory
from order import Order
from orderline import OrderLine
from physicalproduct import PhysicalProduct
from product import Product
from supplier import Supplier


def heading(title: str) -> None:
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def check(description: str, condition: bool) -> None:
    print(f"[{'PASS' if condition else 'FAIL'}] {description}")
    assert condition, description


# ---------------------------------------------------------------------
# Section 2 - Association: Supplier and Product
# ---------------------------------------------------------------------
def test_association() -> None:
    heading("SECTION 2 - ASSOCIATION (Supplier <-> Product)")

    # The Supplier is created on its own, BEFORE any Product
    supplier = Supplier("S900", "Test Supplies Pte Ltd", "hello@testsupplies.example.com")
    supplier_id_before = id(supplier)

    laptop = PhysicalProduct("P901", "Test Laptop", 1000.0, 5, supplier, 2.0)
    ebook = DigitalProduct("P902", "Test E-Book", 15.0, 50, supplier, 12.5)

    print("Supplier information displayed THROUGH each Product:")
    laptop.get_supplier().display_information()
    ebook.get_supplier().display_information()

    check("Both products refer to the SAME Supplier object",
          laptop.get_supplier() is ebook.get_supplier())
    check("Product and Supplier are separate objects",
          id(laptop) != id(supplier) and id(ebook) != id(supplier))
    check("Product stores a Supplier object (not just a name or ID)",
          isinstance(laptop.get_supplier(), Supplier))

    print()
    print("Predict-first test: del supplier")
    del supplier  # removes only the local variable name
    print("After 'del supplier', each product can still display its supplier:")
    laptop.get_supplier().display_information()
    ebook.get_supplier().display_information()
    check("Supplier object still exists (same id) because the products reference it",
          id(laptop.get_supplier()) == supplier_id_before)

    print()
    print("A Supplier can also exist with no products at all:")
    lonely_supplier = Supplier("S901", "New Supplier", "new@supplier.example.com")
    lonely_supplier.display_information()
    check("Supplier created without any Product", lonely_supplier.get_name() == "New Supplier")


# ---------------------------------------------------------------------
# Section 3 - Aggregation: Inventory and Product
# ---------------------------------------------------------------------
def test_aggregation() -> None:
    heading("SECTION 3 - AGGREGATION (Inventory <>-- Product)")
    supplier = Supplier("S900", "Test Supplies Pte Ltd", "hello@testsupplies.example.com")

    # 1. Product created BEFORE any inventory exists
    mouse = PhysicalProduct("P903", "Test Mouse", 20.0, 30, supplier, 0.1)
    print("1. Product created before any Inventory:")
    mouse.display_information()

    # 2. Add to Inventory A
    inventory_a = Inventory()
    inventory_b = Inventory()
    check("2. Product added to Inventory A", inventory_a.add_product(mouse))
    check("   Duplicate ID is rejected", not inventory_a.add_product(mouse))
    print("Inventory A:")
    inventory_a.display_all_products()

    # 3. Remove from Inventory A - product must still work
    removed = inventory_a.remove_product("P903")
    check("3. remove_product returns the SAME Product object", removed is mouse)
    check("   Inventory A no longer contains it", inventory_a.find_product("P903") is None)
    check("   Product still usable after removal (update_stock works)", mouse.update_stock(25))
    print("   Product after removal from Inventory A:")
    mouse.display_information()
    print("Inventory A (now empty):")
    inventory_a.display_all_products()

    # 4. Add the same object to Inventory B (transfer)
    check("4. Same Product object added to Inventory B", inventory_b.add_product(mouse))
    check("   Inventory B holds the identical object (is)",
          inventory_b.find_product("P903") is mouse)
    print("Inventory B:")
    inventory_b.display_all_products()

    # 5. Removing / emptying does not destroy the product
    inventory_b.remove_product("P903")
    check("5. After emptying Inventory B the product still exists with its data",
          mouse.get_name() == "Test Mouse" and mouse.get_stock() == 25)
    check("   remove_product on a missing ID returns None",
          inventory_b.remove_product("P999") is None)


# ---------------------------------------------------------------------
# Section 4 - Composition: Order and OrderLine
# ---------------------------------------------------------------------
def test_composition() -> None:
    heading("SECTION 4 - COMPOSITION (Order <*>-- OrderLine)")
    supplier = Supplier("S900", "Test Supplies Pte Ltd", "hello@testsupplies.example.com")
    keyboard = PhysicalProduct("P904", "Test Keyboard", 45.0, 10, supplier, 0.8)
    antivirus = DigitalProduct("P905", "Test Antivirus", 49.9, 100, supplier, 850.0)

    # Order creates its own OrderLines through add_order_line()
    order_1 = Order("O901")
    order_1.add_order_line(keyboard, 2)
    order_1.add_order_line(antivirus, 3)
    order_1.display_order()
    check("Order 1 created 2 OrderLines internally", order_1.get_line_count() == 2)
    check("Order total = 2 x 45.00 + 3 x 49.90 = 239.70",
          abs(order_1.calculate_total() - 239.70) < 1e-9)

    # Same Product in a second Order
    order_2 = Order("O902")
    order_2.add_order_line(keyboard, 1)
    order_2.display_order()

    line_in_order_1 = order_1.get_order_lines()[0]
    line_in_order_2 = order_2.get_order_lines()[0]
    print("Predict-first check (same Product in two Orders):")
    print(f"  id(Order 1 line) = {id(line_in_order_1)}")
    print(f"  id(Order 2 line) = {id(line_in_order_2)}")
    print(f"  id(product in line 1) = {id(line_in_order_1.get_product())}")
    print(f"  id(product in line 2) = {id(line_in_order_2.get_product())}")
    check("Each Order created its OWN OrderLine (2 different OrderLine objects)",
          line_in_order_1 is not line_in_order_2)
    check("Both OrderLines refer to ONE shared Product object",
          line_in_order_1.get_product() is line_in_order_2.get_product() is keyboard)

    # OrderLine refers to the Product but does not own it
    check("Product is not destroyed or changed by being ordered",
          keyboard.get_stock() == 10 and keyboard.get_name() == "Test Keyboard")

    # Lines cannot be added from outside
    lines = order_1.get_order_lines()
    check("get_order_lines() returns a read-only tuple (cannot append from outside)",
          isinstance(lines, tuple) and not hasattr(lines, "append"))

    # Remove a line through the Order
    check("Remove the antivirus line through Order.remove_order_line()",
          order_1.remove_order_line("P905"))
    check("Order 1 now has 1 line and total 90.00",
          order_1.get_line_count() == 1 and abs(order_1.calculate_total() - 90.0) < 1e-9)
    check("Removing a line that does not exist returns False",
          not order_1.remove_order_line("P999"))
    check("The antivirus Product still exists after its OrderLine was removed",
          antivirus.get_name() == "Test Antivirus")
    order_1.display_order()

    # Remove the whole order: its lines go with it
    del order_2
    print("Order O902 removed from the test scenario - its OrderLine went with it,")
    print("but the shared keyboard Product is still here:")
    keyboard.display_information()


# ---------------------------------------------------------------------
# Section 5 - Type hints evidence
# ---------------------------------------------------------------------
def test_type_hints() -> None:
    heading("SECTION 5 - TYPE HINTS (evidence)")
    methods: list[Callable[..., object]] = [
        Product.__init__, Product.get_supplier, Product.update_stock,
        Product.get_fulfilment_info, Product.to_dict,
        PhysicalProduct.__init__, PhysicalProduct.calculate_shipping_cost,
        DigitalProduct.__init__,
        Supplier.__init__, Supplier.display_information,
        Inventory.add_product, Inventory.remove_product, Inventory.find_product,
        Inventory.display_all_products, Inventory.get_all_products,
        OrderLine.__init__, OrderLine.get_product, OrderLine.calculate_subtotal,
        Order.__init__, Order.add_order_line, Order.remove_order_line,
        Order.get_order_lines, Order.calculate_total,
        CanBeShipped.calculate_shipping_cost,
    ]
    for method in methods:
        print(f"{method.__qualname__}{inspect.signature(method)}")
        hints = typing.get_type_hints(method)
        check(f"   {method.__qualname__} has a return type hint", "return" in hints)

    print()
    print("Attribute type hints (from the source of each __init__):")
    for cls in (Product, PhysicalProduct, DigitalProduct, Supplier, Inventory, OrderLine, Order):
        source = inspect.getsource(cls.__init__)
        for line in source.splitlines():
            if "self.__" in line and ":" in line.split("=")[0]:
                print(f"  {cls.__name__}: {line.strip()}")


# ---------------------------------------------------------------------
# Section 6 - Liskov Substitution Principle
# ---------------------------------------------------------------------
def show_product_details(product: Product) -> None:
    """Accepts ANY Product and only uses behaviour every Product supports."""
    product.display_information()
    print(product.get_fulfilment_info())


def test_lsp() -> None:
    heading("SECTION 6 - LISKOV SUBSTITUTION PRINCIPLE")
    supplier = Supplier("S900", "Test Supplies Pte Ltd", "hello@testsupplies.example.com")
    physical = PhysicalProduct("P906", "Test Monitor", 299.99, 10, supplier, 5.5)
    digital = DigitalProduct("P907", "Test OS Licence", 199.99, 100, supplier, 5400.0)

    print("6.2 show_product_details() called with BOTH subclasses, unchanged:")
    for product in (physical, digital):
        show_product_details(product)
        print()

    print("6.3 Expectation from Product: update_stock() accepts any quantity >= 0,")
    print("    rejects negatives, and returns a bool. Both subclasses keep this:")
    for product in (physical, digital):
        name = type(product).__name__
        check(f"{name}.update_stock(0) returns True", product.update_stock(0) is True)
        check(f"{name}.update_stock(42) returns True and stock becomes 42",
              product.update_stock(42) is True and product.get_stock() == 42)
        check(f"{name}.update_stock(-5) returns False and stock is unchanged",
              product.update_stock(-5) is False and product.get_stock() == 42)
        check(f"{name}.get_fulfilment_info() returns a str",
              isinstance(product.get_fulfilment_info(), str))

    print()
    print("Both product types work with normal Inventory operations:")
    inventory = Inventory()
    check("add_product(PhysicalProduct)", inventory.add_product(physical))
    check("add_product(DigitalProduct)", inventory.add_product(digital))
    check("find_product works for both",
          inventory.find_product("P906") is physical and inventory.find_product("P907") is digital)
    inventory.display_all_products()

    print("Product is abstract, so it cannot be created directly:")
    try:
        Product("P000", "Generic", 1.0, 1, supplier)  # type: ignore[abstract]
        check("Product() raised TypeError", False)
    except TypeError as error:
        print(f"  TypeError: {error}")
        check("Product() raised TypeError", True)


# ---------------------------------------------------------------------
# Section 7 - Polymorphism
# ---------------------------------------------------------------------
def test_polymorphism() -> None:
    heading("SECTION 7 - POLYMORPHISM through Product references")
    tech = Supplier("S001", "TechWorld Distributors", "sales@techworld.example.com")
    soft = Supplier("S003", "SoftKey Licensing", "support@softkey.example.com")

    inventory = Inventory()
    inventory.add_product(PhysicalProduct("P001", "Laptop", 1200.0, 10, tech, 2.0))
    inventory.add_product(DigitalProduct("P008", "Windows 11 Pro License", 199.99, 100, soft, 5400.0))
    inventory.add_product(PhysicalProduct("P002", "Mouse", 25.5, 40, tech, 0.1))
    inventory.add_product(DigitalProduct("P009", "Antivirus Software", 49.9, 250, soft, 850.0))

    expected = {
        "P001": "Requires physical shipping to the customer's address.",
        "P002": "Requires physical shipping to the customer's address.",
        "P008": "Delivered digitally via a download link.",
        "P009": "Delivered digitally via a download link.",
    }

    # ONE loop, typed as Product, no isinstance() checks
    products: list[Product] = inventory.get_all_products()
    for product in products:
        product.display_information()
        info = product.get_fulfilment_info()
        print(f"   -> {info}")
        check(f"   {product.get_product_id()} ran {type(product).__name__}'s own "
              f"get_fulfilment_info()", info == expected[product.get_product_id()])

    print()
    print("display_details() - each subclass fills in its own extra lines:")
    for product in products[:2]:
        product.display_details()

    print("Only PhysicalProduct implements the CanBeShipped interface:")
    check("PhysicalProduct is a CanBeShipped", issubclass(PhysicalProduct, CanBeShipped))
    check("DigitalProduct is NOT a CanBeShipped", not issubclass(DigitalProduct, CanBeShipped))


if __name__ == "__main__":
    test_association()
    test_aggregation()
    test_composition()
    test_type_hints()
    test_lsp()
    test_polymorphism()
    heading("ALL LAB 8 TESTS PASSED")

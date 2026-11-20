"""Lab 9 automated tests: Strategy, Factory, validation and exception handling.

These are the kind of tests a CI pipeline runs on every push. They use only
the standard library (unittest), so nothing extra needs installing.

Run from the project folder:
    python -m unittest discover -s tests -v
"""
import ast
import inspect
import io
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from typing import Callable, TypeVar
from unittest.mock import patch

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

import main  # noqa: E402
from bulkdiscount import BulkDiscount  # noqa: E402
from digitalproduct import DigitalProduct  # noqa: E402
from discountstrategy import DiscountStrategy  # noqa: E402
from inventory import Inventory  # noqa: E402
from nodiscount import NoDiscount  # noqa: E402
from order import Order  # noqa: E402
from orderline import OrderLine  # noqa: E402
from percentagediscount import PercentageDiscount  # noqa: E402
from physicalproduct import PhysicalProduct  # noqa: E402
from product import Product  # noqa: E402
from productfactory import ProductFactory  # noqa: E402
from studentdiscount import StudentDiscount  # noqa: E402
from supplier import Supplier  # noqa: E402

T = TypeVar("T")

PRODUCTS_CSV_TEXT = (
    "product_type,product_id,name,price,stock_quantity\n"
    "physical,P001,Desk Lamp,25.00,10\n"
    "digital,D001,Photo Editor,49.90,100\n"
    "service,S001,Installation,30.00,5\n"
    "physical,P002,Office Chair,abc,3\n"
    "physical,P003,Monitor Stand,39.50,7\n"
)


def make_supplier() -> Supplier:
    return Supplier("S900", "Test Supplies Pte Ltd", "hello@testsupplies.example.com")


def make_order_totalling_250(discount: DiscountStrategy | None = None) -> Order:
    """2 x 100.00 + 1 x 50.00 = 250.00"""
    supplier = make_supplier()
    chair = ProductFactory.create("physical", "P950", "Chair", 100.0, 10, supplier, weight=5.0)
    course = ProductFactory.create("digital", "P951", "Course", 50.0, 10, supplier, download_size=200.0)
    order = Order("O950", discount)
    order.add_order_line(chair, 2)
    order.add_order_line(course, 1)
    return order


def run_quietly(func: Callable[..., T], *args: object) -> tuple[T, str]:
    """Call func, returning (result, everything it printed)."""
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        result = func(*args)
    return result, buffer.getvalue()


# ---------------------------------------------------------------------
# Section 2 - Strategy pattern
# ---------------------------------------------------------------------
class TestDiscountStrategies(unittest.TestCase):

    def test_discount_strategy_is_abstract(self) -> None:
        with self.assertRaises(TypeError):
            DiscountStrategy()  # type: ignore[abstract]

    def test_no_discount_returns_total_unchanged(self) -> None:
        self.assertEqual(NoDiscount().apply(250.0), 250.0)

    def test_percentage_discount(self) -> None:
        self.assertAlmostEqual(PercentageDiscount(10).apply(250.0), 225.0)

    def test_bulk_discount_at_and_below_threshold(self) -> None:
        bulk = BulkDiscount(200, 20)
        self.assertAlmostEqual(bulk.apply(250.0), 230.0)
        self.assertAlmostEqual(bulk.apply(200.0), 180.0)   # "200 or more"
        self.assertAlmostEqual(bulk.apply(199.99), 199.99)  # below threshold

    def test_bulk_discount_never_goes_below_zero(self) -> None:
        self.assertEqual(BulkDiscount(0, 50).apply(30.0), 0.0)

    def test_student_discount_is_five_percent(self) -> None:
        self.assertAlmostEqual(StudentDiscount().apply(250.0), 237.5)

    def test_invalid_strategy_values_rejected(self) -> None:
        for bad in (0, -10, 150):
            with self.assertRaises(ValueError):
                PercentageDiscount(bad)
        with self.assertRaises(ValueError):
            BulkDiscount(200, 0)
        with self.assertRaises(ValueError):
            BulkDiscount(-1, 20)


class TestOrderUsesStrategy(unittest.TestCase):

    def test_default_strategy_is_no_discount(self) -> None:
        order = make_order_totalling_250()
        self.assertIsInstance(order.get_discount(), NoDiscount)
        self.assertAlmostEqual(order.calculate_total(), 250.0)

    def test_predict_first_bulk_then_percentage(self) -> None:
        """Section 2.3 predict-first: 250 with BulkDiscount(200, 20) -> 230,
        then set_discount(PercentageDiscount(10)) on the SAME order -> 225."""
        order = make_order_totalling_250(BulkDiscount(200, 20))
        self.assertAlmostEqual(order.calculate_subtotal(), 250.0)
        self.assertAlmostEqual(order.calculate_total(), 230.0)
        order.set_discount(PercentageDiscount(10))
        self.assertAlmostEqual(order.calculate_total(), 225.0)

    def test_order_has_no_discount_if_elif_logic(self) -> None:
        source = inspect.getsource(Order)
        for banned in ("discount_type", "isinstance", "PercentageDiscount", "BulkDiscount"):
            self.assertNotIn(banned, source)
        calc = inspect.getsource(Order.calculate_total)
        self.assertNotIn("if ", calc)
        self.assertIn(".apply(", calc)

    def test_new_strategy_works_without_changing_order(self) -> None:
        """A brand-new strategy defined only here still works with Order."""
        class FlatTenOff(DiscountStrategy):
            def apply(self, total: float) -> float:
                return total - 10

        order = make_order_totalling_250(FlatTenOff())
        self.assertAlmostEqual(order.calculate_total(), 240.0)
        order.set_discount(StudentDiscount())  # the Section 2.4 strategy
        self.assertAlmostEqual(order.calculate_total(), 237.5)

    def test_two_orders_can_share_one_strategy_object(self) -> None:
        """Association, not composition: one strategy, many orders."""
        shared = PercentageDiscount(10)
        order_a = make_order_totalling_250(shared)
        order_b = make_order_totalling_250(shared)
        self.assertIs(order_a.get_discount(), order_b.get_discount())
        self.assertAlmostEqual(order_a.calculate_total(), 225.0)
        self.assertAlmostEqual(order_b.calculate_total(), 225.0)

    def test_display_order_shows_subtotal_discount_and_total(self) -> None:
        order = make_order_totalling_250(BulkDiscount(200, 20))
        _, output = run_quietly(order.display_order)
        self.assertIn("Subtotal: $250.00", output)
        self.assertIn("Discount: $20.00 off orders of $200.00 or more", output)
        self.assertIn("Order Total: $230.00", output)


# ---------------------------------------------------------------------
# Section 3 - Factory pattern
# ---------------------------------------------------------------------
class TestProductFactory(unittest.TestCase):

    def test_creates_physical_and_digital(self) -> None:
        supplier = make_supplier()
        physical: Product = ProductFactory.create("physical", "P960", "Lamp", 25.0, 10,
                                                  supplier, weight=1.5)
        digital: Product = ProductFactory.create("digital", "P961", "Editor", 49.9, 100,
                                                 supplier, download_size=300.0)
        self.assertIsInstance(physical, PhysicalProduct)
        self.assertIsInstance(digital, DigitalProduct)
        self.assertEqual(physical.get_fulfilment_info(),
                         "Requires physical shipping to the customer's address.")
        self.assertEqual(digital.get_fulfilment_info(), "Delivered digitally via a download link.")
        self.assertIs(physical.get_supplier(), supplier)

    def test_type_is_case_and_space_insensitive(self) -> None:
        product = ProductFactory.create("  Digital ", "P962", "Game", 59.0, 3, make_supplier())
        self.assertIsInstance(product, DigitalProduct)

    def test_return_type_hint_is_product(self) -> None:
        hints = ProductFactory.create.__annotations__
        self.assertIs(hints["return"], Product)

    def test_unknown_type_raises_clear_value_error(self) -> None:
        """Section 3.2 predict-first: create("service", ...)."""
        with self.assertRaises(ValueError) as context:
            ProductFactory.create("service", "S001", "Installation", 30.0, 5, make_supplier())
        self.assertEqual(str(context.exception), "Unknown product type: service")

    def test_main_creates_products_only_through_factory(self) -> None:
        source = (PROJECT_DIR / "main.py").read_text()
        self.assertNotIn("PhysicalProduct(", source)
        self.assertNotIn("DigitalProduct(", source)
        self.assertIn("ProductFactory.create(", source)


# ---------------------------------------------------------------------
# Section 4 - Validation
# ---------------------------------------------------------------------
class TestValidation(unittest.TestCase):

    def test_price_must_be_greater_than_zero(self) -> None:
        for bad_price in (0.0, -5.0):
            for product_type in ("physical", "digital"):
                with self.assertRaises(ValueError) as context:
                    ProductFactory.create(product_type, "P970", "Bad", bad_price, 1, make_supplier())
                self.assertEqual(str(context.exception), "Price must be greater than zero.")

    def test_stock_cannot_be_negative(self) -> None:
        for product_type in ("physical", "digital"):
            with self.assertRaises(ValueError) as context:
                ProductFactory.create(product_type, "P971", "Bad", 10.0, -1, make_supplier())
            self.assertEqual(str(context.exception), "Stock quantity cannot be negative.")

    def test_zero_stock_is_allowed(self) -> None:
        product = ProductFactory.create("physical", "P972", "Sold Out", 10.0, 0, make_supplier())
        self.assertEqual(product.get_stock(), 0)

    def test_order_line_quantity_must_be_positive(self) -> None:
        product = ProductFactory.create("physical", "P973", "Pen", 2.0, 50, make_supplier())
        for bad_quantity in (0, -3):
            with self.assertRaises(ValueError) as context:
                OrderLine(product, bad_quantity)
            self.assertEqual(str(context.exception), "Quantity must be greater than zero.")

    def test_invalid_quantity_leaves_order_unchanged(self) -> None:
        product = ProductFactory.create("physical", "P974", "Pen", 2.0, 50, make_supplier())
        order = Order("O970")
        with self.assertRaises(ValueError):
            order.add_order_line(product, 0)
        self.assertEqual(order.get_line_count(), 0)

    def test_subclasses_keep_update_stock_contract(self) -> None:
        """LSP: both subclasses inherit Product's stock rule unchanged."""
        for product_type in ("physical", "digital"):
            product = ProductFactory.create(product_type, "P975", "Item", 5.0, 10, make_supplier())
            self.assertFalse(product.update_stock(-5))
            self.assertEqual(product.get_stock(), 10)
            self.assertTrue(product.update_stock(0))


# ---------------------------------------------------------------------
# Section 5.1 - Exception handling: user input
# ---------------------------------------------------------------------
class TestUserInput(unittest.TestCase):

    def test_get_positive_float_abc_then_minus5_then_12_50(self) -> None:
        """Section 5.1 predict-first."""
        with patch("builtins.input", side_effect=["abc", "-5", "12.50"]):
            value, output = run_quietly(main.get_positive_float, "Price: ")
        self.assertEqual(value, 12.5)
        self.assertEqual(output.splitlines(), [
            "Please enter a valid number, e.g. 12.50",
            "Please enter a number greater than zero.",
        ])

    def test_get_positive_float_rejects_zero(self) -> None:
        with patch("builtins.input", side_effect=["0", "3"]):
            value, output = run_quietly(main.get_positive_float, "Price: ")
        self.assertEqual(value, 3.0)
        self.assertIn("greater than zero", output)

    def test_get_int_keeps_asking(self) -> None:
        with patch("builtins.input", side_effect=["two", "1.5", "-1", "4"]):
            value, output = run_quietly(main.get_int, "Qty: ")
        self.assertEqual(value, 4)
        self.assertEqual(output.count("valid whole number"), 2)
        self.assertEqual(output.count("cannot be negative"), 1)

    def test_bad_discount_percentage_asks_again(self) -> None:
        # choose 2 (percentage), enter 150 (rejected by strategy), then choose 4 (student)
        with patch("builtins.input", side_effect=["2", "150", "4"]):
            strategy, output = run_quietly(main.choose_discount)
        self.assertIsInstance(strategy, StudentDiscount)
        self.assertIn("Invalid discount: Percentage must be greater than 0 and at most 100.", output)


# ---------------------------------------------------------------------
# Section 5.2 - Exception handling: loading products from a file
# ---------------------------------------------------------------------
class TestLoadProducts(unittest.TestCase):

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.csv_path = os.path.join(self.temp_dir.name, "products.csv")
        with open(self.csv_path, "w", newline="") as f:
            f.write(PRODUCTS_CSV_TEXT)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_valid_rows_load_and_bad_rows_are_skipped(self) -> None:
        """Section 5.2 predict-first: 3 load, 2 reported, in file order."""
        inventory = Inventory()
        _, output = run_quietly(main.load_products, self.csv_path, inventory, make_supplier())
        self.assertEqual([p.get_product_id() for p in inventory.get_all_products()],
                         ["P001", "D001", "P003"])
        lines = output.splitlines()
        self.assertEqual(len(lines), 4)
        self.assertIn("Skipping row 4", lines[0])
        self.assertIn("Unknown product type: service", lines[0])
        self.assertIn("Skipping row 5", lines[1])
        self.assertIn("could not convert string to float: 'abc'", lines[1])
        self.assertEqual(lines[2], "3 products loaded.")
        self.assertEqual(lines[3], "Load attempt finished.")

    def test_loaded_products_have_correct_types(self) -> None:
        inventory = Inventory()
        run_quietly(main.load_products, self.csv_path, inventory, make_supplier())
        self.assertIsInstance(inventory.find_product("P001"), PhysicalProduct)
        self.assertIsInstance(inventory.find_product("D001"), DigitalProduct)

    def test_missing_file_handled_gracefully(self) -> None:
        """Renamed file: except and finally run, else does not."""
        inventory = Inventory()
        missing = os.path.join(self.temp_dir.name, "renamed.csv")
        _, output = run_quietly(main.load_products, missing, inventory, make_supplier())
        self.assertEqual(output.splitlines(), [
            f"Products file not found: {missing}",
            "Load attempt finished.",
        ])
        self.assertNotIn("products loaded", output)
        self.assertEqual(inventory.get_all_products(), [])

    def test_duplicate_ids_are_reported_not_loaded_twice(self) -> None:
        inventory = Inventory()
        supplier = make_supplier()
        run_quietly(main.load_products, self.csv_path, inventory, supplier)
        _, output = run_quietly(main.load_products, self.csv_path, inventory, supplier)
        self.assertIn("0 products loaded.", output)
        self.assertEqual(len(inventory.get_all_products()), 3)

    def test_missing_inventory_json_starts_empty(self) -> None:
        missing = os.path.join(self.temp_dir.name, "none.json")
        with patch.object(main, "FILENAME", missing):
            inventory, output = run_quietly(main.load_inventory, {})
        self.assertEqual(inventory.get_all_products(), [])
        self.assertIn("Inventory file not found", output)

    def test_bad_record_in_inventory_json_is_skipped(self) -> None:
        path = os.path.join(self.temp_dir.name, "inventory.json")
        with open(path, "w") as f:
            f.write('[{"Type": "physical", "ID": "P001", "Name": "Laptop", "Price": 1200.0,'
                    ' "Stock": 10, "Weight": 2.0},'
                    ' {"Type": "service", "ID": "P002", "Name": "Setup", "Price": 30.0, "Stock": 1},'
                    ' {"Type": "physical", "ID": "P003", "Name": "Free", "Price": 0, "Stock": 1}]')
        with patch.object(main, "FILENAME", path):
            inventory, output = run_quietly(main.load_inventory, {})
        self.assertEqual([p.get_product_id() for p in inventory.get_all_products()], ["P001"])
        self.assertIn("Skipping saved product P002: Unknown product type: service", output)
        self.assertIn("Skipping saved product P003: Price must be greater than zero.", output)

    def test_corrupt_json_stops_program_without_overwriting(self) -> None:
        path = os.path.join(self.temp_dir.name, "inventory.json")
        with open(path, "w") as f:
            f.write("{ not json")
        with patch.object(main, "FILENAME", path), \
                patch.object(main, "SUPPLIER_FILENAME", os.path.join(self.temp_dir.name, "s.json")):
            _, output = run_quietly(main.main)
        self.assertIn("not valid JSON", output)
        with open(path) as f:
            self.assertEqual(f.read(), "{ not json")  # file left untouched


# ---------------------------------------------------------------------
# Every except catches a SPECIFIC exception
# ---------------------------------------------------------------------
class TestSpecificExceptions(unittest.TestCase):

    def test_no_bare_or_broad_except_in_project(self) -> None:
        for path in PROJECT_DIR.glob("*.py"):
            tree = ast.parse(path.read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.ExceptHandler):
                    self.assertIsNotNone(node.type, f"bare except in {path.name}:{node.lineno}")
                    names = ast.unparse(node.type)  # type: ignore[arg-type]
                    for broad in ("Exception", "BaseException"):
                        self.assertNotEqual(names, broad,
                                            f"broad except in {path.name}:{node.lineno}")


if __name__ == "__main__":
    unittest.main(verbosity=2)

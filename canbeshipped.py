from abc import ABC, abstractmethod


class CanBeShipped(ABC):
    """Interface-style abstract base class ("must be able to" be shipped).

    It is a contract only: no attributes and no shipping implementation.
    Any class that implements it must provide calculate_shipping_cost().
    """

    @abstractmethod
    def calculate_shipping_cost(self) -> float:
        """Return the shipping cost of this item in dollars."""

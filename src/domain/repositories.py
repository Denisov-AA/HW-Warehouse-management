from abc import ABC, abstractmethod
from typing import List

from .models import Order, Product


class ProductRepository(ABC):
    @abstractmethod
    def add(self, product: Product): ...

    @abstractmethod
    def get(self, product_id: int) -> Product: ...

    @abstractmethod
    def list(self) -> List[Product]: ...


class OrderRepository(ABC):
    @abstractmethod
    def add(self, order: Order): ...

    @abstractmethod
    def get(self, order_id: int) -> Order: ...

    @abstractmethod
    def list(self) -> List[Order]: ...

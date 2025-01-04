from abc import ABC, abstractmethod


class UnitOfWork(ABC):
    @abstractmethod
    def __enter__(self): ...

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb): ...

    @abstractmethod
    def commit(self): ...

    @abstractmethod
    def rollback(self): ...

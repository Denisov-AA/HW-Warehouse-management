import random

from domain.services import WarehouseService
from infrastructure.database import SessionFactory as SyncSession
from infrastructure.repositories import (
    SqlAlchemyOrderRepository,
    SqlAlchemyProductRepository,
)
from infrastructure.unit_of_work import SqlAlchemyUnitOfWork


def main():
    products = ["Phone", "Tablet", "Laptop", "Watch", "Camera", "Speaker", "Headphones"]

    with SqlAlchemyUnitOfWork(SyncSession()) as session:
        product_repo = SqlAlchemyProductRepository(session)
        order_repo = SqlAlchemyOrderRepository(session)
        warehouse_service = WarehouseService(product_repo, order_repo)

        try:
            for _ in range(10):
                warehouse_service.create_product(
                    name=random.choice(products),
                    quantity=random.randint(1, 100),
                    price=random.randint(100, 1000),
                )
                session.commit()
            for _ in range(3):
                warehouse_service.create_order(
                    random.choices(
                        population=product_repo.list(), k=random.randint(1, 3)
                    )
                )
            session.commit()

        except Exception as e:
            session.rollback()
            raise e


if __name__ == "__main__":
    main()

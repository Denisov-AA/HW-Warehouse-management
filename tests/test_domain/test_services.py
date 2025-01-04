import pytest
from sqlalchemy import delete

from src.domain.services import WarehouseService
from src.infrastructure.database import SessionFactory as SyncSession
from src.infrastructure.orm import OrderORM, ProductORM, order_product_associations
from src.infrastructure.repositories import (
    SqlAlchemyOrderRepository,
    SqlAlchemyProductRepository,
)


class TestDataCreation:
    session = SyncSession()
    product_repo = SqlAlchemyProductRepository(session)
    order_repo = SqlAlchemyOrderRepository(session)
    warehouse_service = WarehouseService(product_repo, order_repo)

    @pytest.mark.parametrize(
        "name, quantity, price",
        [
            ("test_create_product_name_1", 88, 888.88),
            ("test_create_product_name_2", 99, 999.99),
        ],
    )
    def test_create_product(self, name, quantity, price):
        product_orm = self.warehouse_service.create_product(
            name=name, quantity=quantity, price=price
        )
        self.session.commit()
        product_orm_from_db = (
            self.session.query(ProductORM).filter_by(name=product_orm.name).scalar()
        )

        assert product_orm.name == product_orm_from_db.name == name
        assert product_orm.quantity == product_orm_from_db.quantity == quantity
        assert product_orm.price == product_orm_from_db.price == price

        self.session.execute(delete(ProductORM).filter_by(id=product_orm.name))
        self.session.commit()

    @pytest.mark.parametrize(
        "products_count, name, quantity, price",
        [
            (2, "test_create_order_name_1", 66, 666.66),
            (5, "test_create_order_name_2", 77, 777.77),
        ],
    )
    def test_create_order(self, products_count, name, quantity, price):
        products_orm = []
        for i in range(products_count):
            products_orm.append(
                self.warehouse_service.create_product(
                    name=name + f"_{i}", quantity=quantity, price=price
                )
            )
            self.session.commit()
        order_orm = self.warehouse_service.create_order(self.product_repo.list())
        self.session.commit()
        assert sorted(order_orm.products, key=lambda x: x.id) == sorted(
            self.product_repo.list(), key=lambda x: x.id
        )

        self.session.execute(
            delete(order_product_associations).where(
                order_product_associations.c.order_id == order_orm.id
            )
        )
        self.session.execute(
            delete(ProductORM).where(
                ProductORM.id.in_([product_orm.id for product_orm in products_orm])
            )
        )
        self.session.execute(delete(OrderORM).where(OrderORM.id == order_orm.id))
        self.session.commit()

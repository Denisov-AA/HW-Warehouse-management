import pytest
from sqlalchemy import delete

from src.infrastructure.database import SessionFactory as SyncSession
from src.infrastructure.orm import (OrderORM, ProductORM,
                                    order_product_associations)
from src.infrastructure.repositories import (SqlAlchemyOrderRepository,
                                             SqlAlchemyProductRepository)

session = SyncSession()
order_repo = SqlAlchemyOrderRepository(session)
product_repo = SqlAlchemyProductRepository(session)


class TestOrderRepo:

    @pytest.mark.parametrize(
        "orders_count, products_count, name, quantity, price",
        [
            (3, 2, "test_list_order_name_1", 55, 555.55),
            (7, 5, "test_list_order_name_2", 44, 444.44),
        ],
    )
    def test_list(self, orders_count, products_count, name, quantity, price):
        prepared_orders_orm = []
        for j in range(orders_count):
            prepared_order_orm = OrderORM()
            for i in range(products_count):
                product_orm = ProductORM(
                    name=name + f"_{j}_{i}", quantity=quantity, price=price
                )
                session.add(product_orm)
                prepared_order_orm.products.append(product_orm)
            session.add(prepared_order_orm)
            prepared_orders_orm.append(prepared_order_orm)
        session.commit()
        orders_orm = order_repo.list()

        assert len(prepared_orders_orm) <= len(orders_orm)
        assert {o.id for o in prepared_orders_orm} <= {o.id for o in orders_orm}
        assert {products_count} == {
            len(o.products)
            for o in orders_orm
            if o.id in {o.id for o in prepared_orders_orm}
        }
        order_products_dict = {
            o.id: o.products
            for o in orders_orm
            if o.id in {o.id for o in prepared_orders_orm}
        }
        for o in prepared_orders_orm:
            assert {p.id for p in o.products} == {
                p.id for p in order_products_dict.get(o.id)
            }

        p_ids = []
        for o in prepared_orders_orm:
            for p in o.products:
                p_ids.append(p.id)
        session.execute(
            delete(order_product_associations).where(
                order_product_associations.c.order_id.in_(
                    [o.id for o in prepared_orders_orm]
                )
            )
        )
        session.execute(delete(ProductORM).where(ProductORM.id.in_(p_ids)))
        session.execute(
            delete(OrderORM).where(OrderORM.id.in_([o.id for o in prepared_orders_orm]))
        )
        session.commit()


class TestProductRepo:

    @pytest.mark.parametrize(
        "name, quantity, price",
        [
            ("test_get_products_name_1", 33, 333.33),
            ("test_get_products_name_2", 44, 444.44),
        ],
    )
    def test_get(self, name, quantity, price):
        prepared_product_orm = ProductORM(name=name, quantity=quantity, price=price)
        session.add(prepared_product_orm)
        session.commit()

        product_orm = product_repo.get(prepared_product_orm.id)

        assert product_orm.id == prepared_product_orm.id
        assert product_orm.name == prepared_product_orm.name == name
        assert product_orm.quantity == prepared_product_orm.quantity == quantity
        assert product_orm.price == prepared_product_orm.price == price

        session.execute(delete(ProductORM).filter_by(id=prepared_product_orm.id))
        session.commit()

    @pytest.mark.parametrize(
        "products_count, name, quantity, price",
        [
            (2, "test_list_products_name_1", 55, 555.55),
            (5, "test_list_products_name_2", 66, 666.66),
        ],
    )
    def test_list(self, products_count, name, quantity, price):
        prepared_products_orm = []
        for i in range(products_count):
            product_orm = ProductORM(
                name=name + f"_{i}", quantity=quantity, price=price
            )
            session.add(product_orm)
            prepared_products_orm.append(product_orm)
        session.commit()

        products_orm = product_repo.list()

        assert len(prepared_products_orm) <= len(products_orm)
        assert {p.id for p in prepared_products_orm} <= {p.id for p in products_orm}
        assert {name + f"_{i}" for i in range(products_count)} <= {
            p.name for p in products_orm
        }

        session.execute(
            delete(ProductORM).where(
                ProductORM.id.in_([p.id for p in prepared_products_orm])
            )
        )
        session.commit()

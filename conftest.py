import os
import re

import neo4j
import pytest
import sqlalchemy
import sqlalchemy.future
import sqlmodel
import sqlmodel.pool
import ts

import dot_init  # noqa: F401
import models
import services.boot
import services.graph
import services.variants

# set app env
os.environ["APP_ENV"] = "tst"
os.environ["TYPESENSE_ENV"] = "tst"

test_db_name = os.environ.get("DATABASE_TEST_URL")
connect_args: dict = {}

assert test_db_name

if "sqlite" in test_db_name:
    # sqlite specific
    connect_args = {"check_same_thread": False}

engine = sqlmodel.create_engine(
    test_db_name,
    connect_args=connect_args,
    poolclass=sqlmodel.pool.StaticPool,
)


def database_tables_create(engine: sqlalchemy.future.Engine):
    sqlmodel.SQLModel.metadata.create_all(engine)

    # sqlalchemy tables

    if not sqlalchemy.inspect(engine).has_table(models.City.__tablename__):
        models.City.__table__.create(engine)

    if not sqlalchemy.inspect(engine).has_table(models.DataMapping.__tablename__):
        models.DataMapping.__table__.create(engine)

    if not sqlalchemy.inspect(engine).has_table(models.EntityLocation.__tablename__):
        models.EntityLocation.__table__.create(engine)


def database_tables_drop(engine: sqlalchemy.future.Engine):
    # sqlalchemy tables

    if sqlalchemy.inspect(engine).has_table(models.City.__tablename__):
        models.City.__table__.drop(engine)

    if sqlalchemy.inspect(engine).has_table(models.DataMapping.__tablename__):
        models.DataMapping.__table__.drop(engine)

    if sqlalchemy.inspect(engine).has_table(models.EntityLocation.__tablename__):
        models.EntityLocation.__table__.drop(engine)

    sqlmodel.SQLModel.metadata.drop_all(engine)


def database_tables_init(engine: sqlalchemy.future.Engine):
    # initialize hypertables
    _session = sqlmodel.Session(engine)

    # note: requires timescaledb support
    # session.execute("select create_hypertable('events', 'timestamp')")


# Set up the database once
database_tables_drop(engine)
database_tables_create(engine)
database_tables_init(engine)


@pytest.fixture(name="session")
def session_fixture():
    connection = engine.connect()
    transaction = connection.begin()

    # begin a nested transaction (using SAVEPOINT)
    nested = connection.begin_nested()

    session = sqlmodel.Session(engine)

    # if the application code calls session.commit, it will end the nested transaction
    # when that happens, start a new one.
    @sqlalchemy.event.listens_for(session, "after_transaction_end")
    def end_savepoint(session, transaction):
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()

    # yield session to test
    yield session

    session.close()
    # rollback the overall transaction, restoring the state before the test ran
    transaction.rollback()
    connection.close()


@pytest.fixture(name="neo_session")
def neo_session_fixture():
    with neo4j.GraphDatabase.driver(
        os.environ["NEO4J_HOST_URL"],
        auth=(os.environ["NEO4J_USER"], os.environ["NEO4J_PASSWORD"]),
    ) as driver:
        # todo: setup test database
        with driver.session(database=os.environ["NEO4J_DB_TEST_NAME"]) as session:
            yield session

        if services.graph.status_up(neo=session) != 0:
            return

        # reset iff neo4j is up and running
        services.boot.reset_graph(session)


@pytest.fixture(name="typesense_session")
def typesense_session_fixture():
    client = ts.client(
        uri=os.environ.get("TYPESENSE_URL"),
        api_key=os.environ.get("TYPESENSE_API_KEY"),
    )

    yield client

    # cleanup typesense collections
    for collection in client.collections.retrieve():
        name = collection["name"]

        if re.search("notme-tst", name):
            client.collections[name].delete()


@pytest.fixture(name="product_session")
def product_session_fixture(session: sqlmodel.Session):
    vendor_1 = models.Vendor(
        name="Vendor 1",
        slug="vendor-1",
    )

    session.add(vendor_1)
    session.commit()

    product_1 = models.Product(
        category_ids=[],
        description="",
        name="Product 1",
        price=1.00,
        status="enabled",
        vendor_id=vendor_1.id,
    )

    session.add(product_1)
    session.commit()

    yield {
        "vendors": [vendor_1],
        "products": [product_1],
    }

    services.variants.truncate(db=session)


@pytest.fixture(name="variant_session")
def variant_session_fixture(session: sqlmodel.Session):
    vendor_1 = models.Vendor(
        name="Vendor 1",
        slug="vendor-1",
    )

    session.add(vendor_1)
    session.commit()

    product_1 = models.Product(
        category_ids=[],
        description="",
        name="Product 1",
        price=1.00,
        status="enabled",
        vendor_id=vendor_1.id,
    )

    session.add(product_1)
    session.commit()

    variant_1 = models.Variant(
        name="Variant 1",
        price=1.00,
        product_id=product_1.id,
        sku="sku1",
        status="private",  # private variant
        stock_location_ids=[],
        version=0,
        vendor_id=vendor_1.id,
    )

    session.add(variant_1)
    session.commit()

    variant_2 = models.Variant(
        name="Variant 2",
        price=1.00,
        product_id=product_1.id,
        sku="sku1",
        status="private",  # private variant
        stock_location_ids=[],
        version=0,
        vendor_id=vendor_1.id,
    )

    session.add(variant_2)
    session.commit()

    rule_1 = models.VariantVrule(
        category_id=None,
        dispensary_class_id=None,
        enabled=True,
        override=False,
        stock_location_id=None,
        variant_id=variant_2.id,
        vendor_id=vendor_1.id,
        version=1,
        visibility="enabled",
    )

    session.add(rule_1)
    session.commit()

    rule_2 = models.VariantVrule(
        category_id=None,
        dispensary_class_id=1,
        enabled=True,
        override=False,
        stock_location_id=None,
        variant_id=None,
        vendor_id=vendor_1.id,
        version=1,
        visibility="enabled",
    )

    session.add(rule_2)
    session.commit()

    yield {
        "vendors": [vendor_1],
        "products": [product_1],
        "variants": [variant_1, variant_2],
        "rules": [rule_1, rule_2],
    }

    services.variants.truncate(db=session)

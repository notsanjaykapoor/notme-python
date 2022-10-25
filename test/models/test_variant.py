import decimal

import pytest
import sqlmodel

import models
import services.variants


def test_variant(session: sqlmodel.Session):
    cat_root = models.Category(
        level=0,
        name="Root",
        slug="root",
        tree_id=0,
    )

    session.add(cat_root)
    session.commit()

    vendor_1 = models.Vendor(
        name="Vendor 1",
        slug="vendor-1",
    )

    session.add(vendor_1)
    session.commit()

    product_1 = models.Product(
        category_ids=[cat_root.id],
        description="description",
        name="Product 1",
        price=1.00,
        status="active",
        vendor_id=vendor_1.id,
    )

    session.add(product_1)
    session.commit()

    assert product_1.category_ids == [cat_root.id]
    assert product_1.name == "Product 1"
    assert product_1.price == decimal.Decimal("1.00")
    assert product_1.vendor_id == vendor_1.id

    stock_1 = models.VendorStockLocation(
        name="Chicago",
        vendor_id=vendor_1.id,
    )

    session.add(stock_1)
    session.commit()

    variant_1 = models.Variant(
        name="Variant 1",
        price=1.01,
        product_id=product_1.id,
        sku="sku1",
        status="active",
        stock_location_ids=[stock_1.id],
    )

    session.add(variant_1)
    session.commit()

    assert variant_1.price == decimal.Decimal("1.01")
    assert variant_1.product_id == product_1.id
    assert variant_1.sku == "sku1"
    assert variant_1.stock_location_ids == [stock_1.id]

    services.variants.truncate(db=session)

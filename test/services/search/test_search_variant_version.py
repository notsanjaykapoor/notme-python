import random

import sqlmodel
import typesense

import models
import services.time
import services.variants
import services.variants.search


def test_search_variant_version(
    session: sqlmodel.Session,
    typesense_session: typesense.client.Client,
    product_session: dict,
):
    # create variants

    product = product_session["products"][0]
    vendor = product_session["vendors"][0]

    variants = []

    for i in range(10):
        variant = models.Variant(
            name=f"Variant {i}",
            price=1.01,
            product_id=product.id,
            sku="sku1",
            status="active",
            stock_location_ids=[],
            version=random.randint(1, 1000),
            vendor_id=vendor.id,
        )

        session.add(variant)
        session.commit()

        variants.append(variant)

    # create index

    services.variants.search.Create(ts_client=typesense_session).call()

    # index objects

    struct_index = services.variants.search.Index(
        db=session, ts_client=typesense_session
    ).call()

    assert struct_index.count == len(variants)

    # get vendor variant sha's from db and ts

    variant_sha_ts = services.variants.sha_ts(
        vendor_id=vendor.id, ts_client=typesense_session
    )

    variant_sha_db = services.variants.sha_db(vendor_id=vendor.id, session=session)

    assert variant_sha_db == variant_sha_ts

    # update variant

    variants[0].version = 0
    session.add(variants[0])
    session.commit()

    # regenerate db fingerprint

    variant_sha_db = services.variants.sha_db(vendor_id=vendor.id, session=session)

    assert variant_sha_db != variant_sha_ts

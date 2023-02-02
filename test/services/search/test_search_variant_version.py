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

    # check vendor variant versions

    search_params = {
        "facet_by": "",
        "filter_by": f"rule_vendor_id:{vendor.id} && rule_dispensary_class_ids:[0]",
        "include_fields": "variant_id,variant_version",
        "page": 1,
        "per_page": 100,
        "q": "*",
        "sort_by": "variant_id:asc",
    }

    search_results = services.variants.search.query(
        ts_client=typesense_session,
        ts_collection=models.VariantVruleSchema.typesense_collection(),
        ts_params=search_params,
    )

    # print(search_results)

    assert search_results["found"] == len(variants)

    hits = search_results["hits"]

    versions_ts = [
        f"{o['document']['variant_id']}:{o['document']['variant_version']}"
        for o in hits
    ]
    versions_ts_str = ",".join(versions_ts)

    variants_db_query = session.exec(
        sqlmodel.select(models.Variant.id, models.Variant.version).order_by(
            models.Variant.id.asc()
        )
    )

    versions_db = [f"{v.id}:{v.version}" for v in variants_db_query]
    versions_db_str = ",".join(versions_db)

    # version fingerprints should match

    assert versions_db_str == versions_ts_str

    # update variant

    variants[0].version = 0
    session.add(variants[0])
    session.commit()

    # regenerate db fingerprint

    variants_db_query = session.exec(
        sqlmodel.select(models.Variant.id, models.Variant.version).order_by(
            models.Variant.id.asc()
        )
    )

    versions_db = [f"{v.id}:{v.version}" for v in variants_db_query]
    versions_db_str = ",".join(versions_db)

    # version fingerprints should be different

    assert versions_db_str != versions_ts_str

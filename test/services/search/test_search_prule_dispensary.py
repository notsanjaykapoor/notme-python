import random

import sqlmodel
import typesense

import models
import services.time
import services.variants
import services.variants.search


def test_search__prule_with_dispensary_class(
    session: sqlmodel.Session, typesense_session: typesense.client.Client
):
    # variant setup

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
        status="enabled",
        stock_location_ids=[],
        version=0,
        vendor_id=vendor_1.id,
    )

    session.add(variant_1)
    session.commit()

    # price rule with dispensary_class conditions

    rule_1 = models.VariantPrule(
        category_id=None,
        dispensary_class_id=1,
        effect_amount=10,
        effect_operator="-",
        effect_unit="%",
        enabled=True,
        override=False,
        scope="item",
        stock_location_id=None,
        trigger_amount=5,
        trigger_operator="ge",
        trigger_unit="quantity",
        variant_id=None,
        vendor_id=vendor_1.id,
        version=1,
    )

    session.add(rule_1)
    session.commit()

    # create index

    services.variants.search.Create(ts_client=typesense_session).call()

    # index objects

    struct_index = services.variants.search.Index(
        db=session, ts_client=typesense_session
    ).call()

    assert struct_index.count == 2

    # search with dispensary_class match

    filter_by_terms = (
        services.variants.search.filter_terms_default()
        + services.variants.search.filter_terms_rule_quantity(q=5)
        + ["rule_dispensary_class_ids:[1]"]
    )

    search_params = {
        "q": "*",
        "filter_by": services.variants.search.filter_terms(filter_by_terms),
    }

    search_results = services.variants.search.query(
        ts_client=typesense_session,
        ts_collection=models.VariantPruleSchema.typesense_collection(),
        ts_params=search_params,
    )

    assert search_results["found"] == 1

    # search with dispensary_class that does not match

    filter_by_terms = (
        services.variants.search.filter_terms_default()
        + services.variants.search.filter_terms_rule_quantity(q=5)
        + [f"rule_dispensary_class_ids:[{random.randint(2, 2**32)}]"]
    )

    search_params = {
        "q": "*",
        "filter_by": services.variants.search.filter_terms(filter_by_terms),
    }

    search_results = services.variants.search.query(
        ts_client=typesense_session,
        ts_collection=models.VariantPruleSchema.typesense_collection(),
        ts_params=search_params,
    )

    assert search_results["found"] == 0

    services.variants.truncate(db=session)

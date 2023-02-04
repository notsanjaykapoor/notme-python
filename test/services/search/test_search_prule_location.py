import sqlmodel
import typesense

import models
import services.variants
import services.variants.search


def test_search__prule_with_stock_location(
    session: sqlmodel.Session, typesense_session: typesense.client.Client
):
    # variant with multiple stock locations setup

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

    stock_boston = models.VendorStockLocation(
        name="Boston",
        vendor_id=vendor_1.id,
    )

    stock_chicago = models.VendorStockLocation(
        name="Chicago",
        vendor_id=vendor_1.id,
    )

    session.add(stock_boston)
    session.add(stock_chicago)
    session.commit()

    variant_1 = models.Variant(
        name="Variant 1",
        price=1.00,
        product_id=product_1.id,
        sku="sku1",
        status="enabled",
        stock_location_ids=[stock_boston.id, stock_chicago.id],
        version=0,
        vendor_id=vendor_1.id,
    )

    session.add(variant_1)
    session.commit()

    assert variant_1.stock_location_ids == [stock_boston.id, stock_chicago.id]

    # price rule with stock location condition

    rule_1 = models.VariantPrule(
        category_id=None,
        effect_amount=10,
        effect_operator="-",
        effect_unit="%",
        enabled=True,
        override=False,
        scope="item",
        stock_location_id=stock_chicago.id,
        trigger_amount=5,
        trigger_operator="ge",
        trigger_unit="quantity",
        variant_id=variant_1.id,
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

    # search with location and trigger_amount matches

    filter_by_terms = (
        services.variants.search.filter_terms_default()
        + services.variants.search.filter_terms_rule_quantity(q=5)
        + services.variants.search.filter_terms_rule_locations(ids=[stock_chicago.id])
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

    print(f"search results {search_results['found']}")

    for search_object in search_results["hits"]:
        print(search_object)

    # search with location match and trigger_amount that does not match

    filter_by_terms = (
        services.variants.search.filter_terms_default()
        + services.variants.search.filter_terms_rule_quantity(q=3)
        + services.variants.search.filter_terms_rule_locations(ids=[stock_chicago.id])
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

    print(f"search results {search_results['found']}")

    for search_object in search_results["hits"]:
        print(search_object)

    # search with location that does not match

    filter_by_terms = (
        services.variants.search.filter_terms_default()
        + services.variants.search.filter_terms_rule_locations(ids=[stock_boston.id])
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

    print(f"search results {search_results['found']}")

    services.variants.truncate(db=session)

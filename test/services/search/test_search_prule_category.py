import sqlmodel
import typesense

import models
import services.variants
import services.variants.search


def test_search__prule_with_category(session: sqlmodel.Session, typesense_session: typesense.client.Client):
    # variant with category setup

    vendor_1 = models.Vendor(
        name="Vendor 1",
        slug="vendor-1",
    )

    session.add(vendor_1)
    session.commit()

    cat_root = models.Category(
        level=0,
        name="Root",
        slug="root",
        tree_id=0,
    )

    session.add(cat_root)
    session.commit()

    cat_level_1 = models.Category(
        level=1,
        name="Level 1",
        parent_id=cat_root.id,
        slug="level-1",
        tree_id=0,
    )

    session.add(cat_level_1)
    session.commit()

    cat_level_2 = models.Category(
        level=2,
        name="Level 2",
        parent_id=cat_level_1.id,
        slug="level-2",
        tree_id=0,
    )

    session.add(cat_level_2)
    session.commit()

    product_1 = models.Product(
        category_ids=[cat_level_1.id],
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
    )

    session.add(variant_1)
    session.commit()

    # price rule with category conditions

    rule_1 = models.VariantPrule(
        category_id=cat_level_1.id,
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

    services.variants.search.Create(search_client=typesense_session).call()

    # index objects

    struct_index = services.variants.search.Index(db=session, search_client=typesense_session).call()

    assert struct_index.count == 2

    # search with category match

    filter_by_terms = (
        services.variants.search.filter_terms_default()
        + services.variants.search.filter_terms_rule_quantity(q=5)
        + services.variants.search.filter_terms_rule_categories(ids=[cat_level_1.id])
    )

    search_params = {
        "q": "*",
        "filter_by": services.variants.search.filter_terms(filter_by_terms),
    }

    search_results = services.variants.search.query(
        search_client=typesense_session,
        search_collection=models.VariantPruleSchema.typesense_collection(),
        search_params=search_params,
    )

    assert search_results["found"] == 1

    # search with category that does not match

    filter_by_terms = (
        services.variants.search.filter_terms_default()
        + services.variants.search.filter_terms_rule_quantity(q=5)
        + services.variants.search.filter_terms_rule_categories(ids=[cat_level_2.id])
    )

    search_params = {
        "q": "*",
        "filter_by": services.variants.search.filter_terms(filter_by_terms),
    }

    search_results = services.variants.search.query(
        search_client=typesense_session,
        search_collection=models.VariantPruleSchema.typesense_collection(),
        search_params=search_params,
    )

    assert search_results["found"] == 0

    services.variants.truncate(db=session)
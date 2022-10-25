import datetime
import random

import sqlmodel
import typesense

import models
import services.time
import services.variants
import services.variants.search


def test_search__vrule_with_dispensary_class(session: sqlmodel.Session, typesense_session: typesense.client.Client):
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
        status="private",
        stock_location_ids=[],
    )

    session.add(variant_1)
    session.commit()

    variant_2 = models.Variant(
        name="Variant 2",
        price=1.00,
        product_id=product_1.id,
        sku="sku1",
        status="enabled",
        stock_location_ids=[],
    )

    session.add(variant_2)
    session.commit()

    # visibility rule that enables private variant for dispensary class

    dispensary_class_with_rule_id = 1
    dispensary_class_without_rule_id = 2

    rule_1 = models.VariantVrule(
        category_id=None,
        dispensary_class_id=dispensary_class_with_rule_id,
        enabled=True,
        override=False,
        stock_location_id=None,
        variant_id=variant_1.id,
        vendor_id=vendor_1.id,
        version=1,
        visibility="enabled",
    )

    session.add(rule_1)
    session.commit()

    # create index

    services.variants.search.Create(search_client=typesense_session).call()

    # index objects

    struct_index = services.variants.search.Index(db=session, search_client=typesense_session).call()

    assert struct_index.count == 3

    services.variants.truncate(db=session)

    # search with matching dispensary class

    filter_by_terms = services.variants.search.filter_terms_default() + services.variants.search.filter_terms_rule_dispensary_classes(
        ids=[0, dispensary_class_with_rule_id]
    )

    search_params = {
        "facet_by": "tags",
        "filter_by": services.variants.search.filter_terms(filter_by_terms),
        "q": "variant 1",
        "query_by": "variant_name",
        "sort_by": "rule_priority:desc",
    }

    search_results = services.variants.search.query(
        search_client=typesense_session,
        search_collection=models.VariantVruleSchema.typesense_collection(),
        search_params=search_params,
    )

    # should return 1 system rule and 1 user rule with visibility 'enabled'

    assert search_results["found"] == 2

    print(f"search results {search_results['found']}")

    for search_object in search_results["hits"]:
        print(search_object)

    system_rules = [search_object for search_object in search_results["hits"] if search_object["document"]["rule_type"] == "system"]

    assert len(system_rules) == 1

    user_rules = [search_object for search_object in search_results["hits"] if search_object["document"]["rule_type"] == "user"]

    assert len(user_rules) == 1
    assert user_rules[0]["document"]["rule_visibility"] == "enabled"

    print(f"search result facets {search_results['facet_counts']}")

    # search with non-matching dispensary class

    filter_by_terms = services.variants.search.filter_terms_default() + services.variants.search.filter_terms_rule_dispensary_classes(
        ids=[0, dispensary_class_without_rule_id]
    )

    search_params = {
        "filter_by": services.variants.search.filter_terms(filter_by_terms),
        "q": "1",
        "query_by": "variant_name",
        "sort_by": "rule_priority:desc",
    }

    search_results = services.variants.search.query(
        search_client=typesense_session,
        search_collection=models.VariantVruleSchema.typesense_collection(),
        search_params=search_params,
    )

    # should return 1 system rule with visibility 'private'

    assert search_results["found"] == 1

    print(f"search results {search_results['found']}")

    for search_object in search_results["hits"]:
        print(search_object)

    system_rules = [search_object for search_object in search_results["hits"] if search_object["document"]["rule_type"] == "system"]

    assert len(system_rules) == 1
    assert system_rules[0]["document"]["rule_visibility"] == "private"

    # search for variant with default rule "enabled"

    filter_by_terms = services.variants.search.filter_terms_default() + services.variants.search.filter_terms_rule_dispensary_classes(ids=[0])

    search_params = {
        "filter_by": services.variants.search.filter_terms(filter_by_terms),
        "q": "2",
        "query_by": "variant_name",
        "sort_by": "rule_priority:desc",
    }

    search_results = services.variants.search.query(
        search_client=typesense_session,
        search_collection=models.VariantVruleSchema.typesense_collection(),
        search_params=search_params,
    )

    # should return 1 system rule with visibility 'enabled'

    assert search_results["found"] == 1

    print(f"search results {search_results['found']}")

    for search_object in search_results["hits"]:
        print(search_object)

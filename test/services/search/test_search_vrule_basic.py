import random

import sqlmodel
import typesense

import models
import services.time
import services.variants
import services.variants.search


def test_search(session: sqlmodel.Session, typesense_session: typesense.client.Client, variant_session: dict):
    # create index

    services.variants.search.Create(search_client=typesense_session).call()

    # index objects

    struct_index = services.variants.search.Index(db=session, search_client=typesense_session).call()

    assert struct_index.count == 4

    # search by user with no/any dispensary class

    search_params = {
        "facet_by": "tags",
        "filter_by": "rule_visibility:enabled && rule_dispensary_class_ids:[0]",
        "q": "variant",
        "query_by": "variant_name",
        "sort_by": "variant_id:desc",
    }

    search_results = services.variants.search.query(
        search_client=typesense_session,
        search_collection=models.VariantVruleSchema.typesense_collection(),
        search_params=search_params,
    )

    print(search_results)

    assert search_results["found"] == 1

    # search by user with dispensary class matching rule

    search_params = {
        "facet_by": "tags",
        "filter_by": "rule_visibility:enabled && rule_dispensary_class_ids:[1]",
        "q": "variant",
        "query_by": "variant_name",
        "sort_by": "variant_id:desc",
    }

    search_results = services.variants.search.query(
        search_client=typesense_session,
        search_collection=models.VariantVruleSchema.typesense_collection(),
        search_params=search_params,
    )

    print(search_results)

    assert search_results["found"] == 2

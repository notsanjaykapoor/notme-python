import typesense

import context
import log
import models
import services.time

logger = log.init("service")


def query(
    ts_client: typesense.client.Client, ts_collection: str, ts_params: dict
) -> dict:
    _collection_name = models.VariantPruleSchema.typesense_collection()

    logger.info(
        f"{context.rid_get()} {__name__} collection {ts_collection} {ts_params}"
    )

    return ts_client.collections[ts_collection].documents.search(ts_params)


def filter_terms(terms: list[str]) -> str:
    return " && ".join(terms)


def filter_terms_default() -> list[str]:
    return _filter_terms_rule_enabled() + _filter_terms_variant_stocked()


def filter_terms_rule_categories(ids: list[int]) -> list[str]:
    return [f"rule_category_ids:{ids}"]


def filter_terms_rule_dispensary_classes(ids: list[int]) -> list[str]:
    return [f"rule_dispensary_class_ids:{ids}"]


def _filter_terms_rule_enabled() -> list[str]:
    return [
        "rule_enabled:true",
        f"rule_end_unix:>={services.time.unix_now()}",
        f"rule_start_unix:<={services.time.unix_now()}",
    ]


def filter_terms_rule_locations(ids: list[int]) -> list[str]:
    return [f"rule_stock_location_ids:{ids}"]


def filter_terms_rule_quantity(q: int) -> list[str]:
    return [
        f"rule_min_quantity:<={q}",
        f"rule_max_quantity:>={q}",
    ]


# def filter_terms_variant_status_enabled() -> list[str]:
#     return [
#         "variant_status:enabled",
#     ]


def _filter_terms_variant_stocked() -> list[str]:
    return [
        "variant_stock_quantity:>=1",
    ]

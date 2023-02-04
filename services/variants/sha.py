import hashlib

import sqlmodel
import typesense

import models
import services.variants.search


def sha_db(vendor_id: int, session: sqlmodel.Session) -> str:
    variants_db_query = session.exec(
        sqlmodel.select(models.Variant.id, models.Variant.version)
        .where(models.Variant.vendor_id == vendor_id)
        .order_by(models.Variant.id.asc())
    )

    versions_db = [f"{v.id}:{v.version}" for v in variants_db_query]
    versions_db_str = ",".join(versions_db)

    return hashlib.sha256(versions_db_str.encode("utf-8")).hexdigest()


def sha_ts(vendor_id: int, ts_client: typesense.client.Client) -> str:
    search_params = {
        "facet_by": "",
        "filter_by": f"rule_vendor_id:{vendor_id} && rule_dispensary_class_ids:[0]",
        "include_fields": "variant_id,variant_version",
        "page": 1,
        "per_page": 100,
        "q": "*",
        "sort_by": "variant_id:asc",
    }

    search_results = services.variants.search.query(
        ts_client=ts_client,
        ts_collection=models.VariantVruleSchema.typesense_collection(),
        ts_params=search_params,
    )

    hits = search_results["hits"]

    versions_ts = [
        f"{o['document']['variant_id']}:{o['document']['variant_version']}"
        for o in hits
    ]
    versions_ts_str = ",".join(versions_ts)

    return hashlib.sha256(versions_ts_str.encode("utf-8")).hexdigest()

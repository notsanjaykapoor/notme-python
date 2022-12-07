import os


class VariantVruleSchema:
    @classmethod
    def typesense_collection(cls) -> str:
        return f"variant-vrules-notme-{os.environ['APP_ENV']}"

    @classmethod
    def typesense_schema(cls) -> dict:
        return {
            "name": cls.typesense_collection(),
            "fields": [
                {"name": "batch_id", "type": "int64", "facet": True},
                {"name": "product_id", "type": "int64", "facet": True},
                # {"name": "product_class_id", "type": "int64"},
                {"name": "rule_category_ids", "type": "int64[]"},
                {"name": "rule_dispensary_class_ids", "type": "int64[]"},
                {"name": "rule_enabled", "type": "bool"},
                {"name": "rule_end_unix", "type": "int64", "optional": True},
                {"name": "rule_id", "type": "int64"},
                {"name": "rule_override", "type": "int32", "optional": True},  # ??
                {"name": "rule_priority", "type": "int32"},
                {"name": "rule_start_unix", "type": "int64"},
                {"name": "rule_type", "type": "string"},  # 'default', 'rule'
                {"name": "rule_variant_ids", "type": "int64[]"},
                {"name": "rule_vendor_id", "type": "int64"},
                {"name": "rule_version", "type": "int64"},
                {"name": "rule_visibility", "type": "string"},
                {"name": "tags", "type": "string[]", "facet": True},
                {"name": "variant_id", "type": "int64"},
                {"name": "variant_name", "type": "string"},
                {"name": "variant_sku", "type": "string"},
                {"name": "variant_status", "type": "string"},  # 'enabled', 'private', 'disabled'
                {"name": "variant_stock_quantity", "type": "int64"},
            ],
        }

import os


class VariantPruleSchema:
    @classmethod
    def typesense_collection(cls) -> str:
        return f"variant-prules-{os.environ['APP_ENV']}"

    @classmethod
    def typesense_schema(cls) -> dict:
        return {
            "name": cls.typesense_collection(),
            "fields": [
                {"name": "product_id", "type": "int64", "facet": True},
                {"name": "product_name", "type": "string"},
                {"name": "product_status", "type": "string"},
                {"name": "rule_category_ids", "type": "int64[]"},
                {"name": "rule_dispensary_class_ids", "type": "int64[]"},
                {"name": "rule_enabled", "type": "bool"},
                {"name": "rule_end_unix", "type": "int64"},
                {"name": "rule_id", "type": "int64", "facet": True},
                {"name": "rule_max_price", "type": "float"},  # ??
                {"name": "rule_max_quantity", "type": "int64"},
                {"name": "rule_min_case_size", "type": "int32"},
                {"name": "rule_min_price", "type": "float"},  # ??
                {"name": "rule_min_quantity", "type": "int64"},
                {"name": "rule_override", "type": "int32", "optional": True},  # ??
                {"name": "rule_priority", "type": "int32"},
                {"name": "rule_scope", "type": "string"},
                {"name": "rule_start_unix", "type": "int64"},
                {"name": "rule_stock_location_ids", "type": "int64[]"},
                {"name": "rule_variant_ids", "type": "int64[]"},
                {"name": "rule_vendor_ids", "type": "int64[]"},  # ??
                {"name": "rule_version", "type": "int64"},
                {"name": "tags", "type": "string[]", "facet": True},
                # variant_has_available_stock ?
                {"name": "variant_name", "type": "string"},
                {"name": "variant_sku", "type": "string"},
                # variant_storefront_displayable ?
                {"name": "variant_status", "type": "string"},  # 'enabled', 'private', 'disabled'
                {"name": "variant_stock_quantity", "type": "int64"},
                # variant_strains ?
                {"name": "vendor_id", "type": "int64", "facet": True},
            ],
            "token_separators": ["+", "-", "@", "."],  # for email
        }

import typing

import models
import services.time

DEFAULT_ALL = [0]

DEFAULT_BATCH_ID = 0


class VariantVruleDocument:
    def __init__(self, variant: models.Variant, product: models.Product, vrule: typing.Optional[models.VariantVrule]):
        self._variant = variant
        self._product = product
        self._vrule = vrule

        self._vendor_id = self._product.vendor_id

    def document(self) -> dict:
        return {
            "id": self._typesense_id(),
            "batch_id": DEFAULT_BATCH_ID,
            "product_id": self._variant.product_id,
            "rule_category_ids": self._rule_category_ids(),
            "rule_dispensary_class_ids": self._rule_dispensary_class_ids(),
            "rule_enabled": self._rule_enabled(),
            "rule_end_unix": services.time.unix_last(),
            "rule_id": self._rule_id(),
            "rule_priority": self._rule_priority(),
            "rule_start_unix": services.time.unix_zero(),
            "rule_type": self._rule_type(),
            "rule_variant_ids": [self._variant.id],
            "rule_vendor_id": self._vendor_id,
            "rule_version": self._rule_version(),
            "rule_visibility": self._rule_visibility(),
            "tags": self._tags(),
            "variant_name": self._variant.name,
            "variant_sku": self._variant.sku,
            "variant_status": self._variant.status,
            "variant_stock_quantity": self._variant_stock_quantity(),
        }

    def _rule_category_ids(self) -> list[int]:
        if not self._vrule or not self._vrule.category_id:
            return DEFAULT_ALL

        return [self._vrule.category_id]

    def _rule_dispensary_class_ids(self) -> int:
        if not self._vrule or not self._vrule.dispensary_class_id:
            return DEFAULT_ALL

        return [self._vrule.dispensary_class_id]

    def _rule_enabled(self) -> int:
        if not self._vrule:
            return True

        return self._vrule.enabled

    def _rule_id(self) -> int:
        if not self._vrule:
            return 0

        return self._vrule.id

    def _rule_priority(self) -> int:
        if not self._vrule:
            return 0

        return 10

    def _rule_type(self) -> str:
        if not self._vrule:
            return "system"

        return "user"

    def _rule_version(self) -> int:
        if not self._vrule:
            return 0

        return self._vrule.version

    def _rule_visibility(self) -> str:
        if not self._vrule:
            # use variant status as default visibility rule
            return self._variant.status

        return self._vrule.visibility

    def _tags(self) -> list[str]:
        return [
            f"variant-{self._variant.id}",
            f"vrule-{self._rule_id()}",
        ]

    def _typesense_id(self) -> str:
        return f"v:{self._variant.id}:vrule:{self._rule_id()}"

    def _variant_stock_quantity(self) -> int:
        return 1

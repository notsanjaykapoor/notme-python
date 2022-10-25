import models
import services.time

DEFAULT_MAX_PRICE = float(2**32)
DEFAULT_MIN_PRICE = 0.0

DEFAULT_MAX_QUANTITY = 2**32
DEFAULT_MIN_QUANTITY = 0

DEFAULT_ALL = [0]


class VariantPruleDocument:
    def __init__(self, variant: models.Variant, product: models.Product, prule: models.VariantPrule):
        self._variant = variant
        self._product = product
        self._prule = prule

    def document(self) -> dict:
        if not self._prule.trigger_unit in ["amount", "quantity"]:
            raise ValueError("invalid prule trigger_unit")

        max_price: float = DEFAULT_MAX_PRICE
        max_quantity: int = DEFAULT_MAX_QUANTITY
        min_price: float = DEFAULT_MIN_PRICE
        min_quantity: int = DEFAULT_MIN_QUANTITY

        if self._prule.trigger_unit == "quantity":
            min_quantity, max_quantity = self._rule_quantity_min_max()
        else:  # amount
            min_price, max_price = self._rule_price_min_max()

        return {
            "id": self._typesense_id(),
            "product_id": self._variant.product_id,
            "product_name": "product name",
            "product_status": "enabled",
            "rule_category_ids": self._rule_category_ids(),
            "rule_dispensary_class_ids": self._rule_dispensary_class_ids(),
            "rule_enabled": self._prule.enabled,
            "rule_end_unix": services.time.unix_last(),
            "rule_id": self._prule.id,
            "rule_max_price": max_price,
            "rule_max_quantity": max_quantity,
            "rule_min_case_size": 1,
            "rule_min_price": min_price,
            "rule_min_quantity": min_quantity,
            "rule_priority": 0,
            "rule_scope": "item",
            "rule_start_unix": 0,
            "rule_stock_location_ids": self._rule_stock_location_ids(),
            "rule_variant_ids": [self._variant.id],
            "rule_vendor_ids": DEFAULT_ALL,
            "rule_version": self._prule.version,
            "tags": self._tags(),
            "variant_name": self._variant.name,
            "variant_sku": self._variant.sku,
            "variant_status": "enabled",
            "variant_stock_quantity": self._variant_stock_quantity(),
            "vendor_id": self._product.vendor_id,
        }

    def _rule_category_ids(self) -> list[int]:
        if not self._prule.category_id:
            return DEFAULT_ALL

        return [self._prule.category_id]

    def _rule_dispensary_class_ids(self) -> int:
        if not self._prule.dispensary_class_id:
            return DEFAULT_ALL

        return [self._prule.dispensary_class_id]

    def _rule_price_min_max(self) -> tuple[float, float]:
        if self._prule.trigger_operator in ["ge", "gt"]:
            max_price = 2**32

            if self._prule.trigger_operator == "ge":
                min_price = self._prule.trigger_amount
            else:
                min_price = self._prule.trigger_amount + 1
        else:  # ["le", "lt"]
            min_price = 0.0

            if self._prule.trigger_operator == "ge":
                max_price = self._prule.trigger_amount
            else:
                max_price = self._prule.trigger_amount - 1

        return [float(min_price), float(max_price)]

    def _rule_quantity_min_max(self) -> tuple[int, int]:
        if self._prule.trigger_operator in ["ge", "gt"]:
            max_quantity = 2**32

            if self._prule.trigger_operator == "ge":
                min_quantity = self._prule.trigger_amount
            else:
                min_quantity = self._prule.trigger_amount + 1
        else:  # ["le", "lt"]
            min_quantity = 1

            if self._prule.trigger_operator == "le":
                max_quantity = self._prule.trigger_amount
            else:
                max_quantity = self._prule.trigger_amount - 1

        return [int(min_quantity), int(max_quantity)]

    def _rule_stock_location_ids(self) -> list[int]:
        if not self._prule.stock_location_id:
            # rule applies to all locations
            return DEFAULT_ALL

        return [self._prule.stock_location_id]

    def _tags(self) -> list[str]:
        return [
            f"prule-{self._prule.id}",
            f"variant-{self._variant.id}",
        ]

    def _typesense_id(self) -> str:
        return f"v:{self._variant.id}:prule:{self._prule.id}"

    def _variant_stock_quantity(self) -> int:
        return 1

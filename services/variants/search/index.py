import collections
import dataclasses
import typing

import sqlmodel
import typesense

import context
import log
import models


@dataclasses.dataclass
class Struct:
    code: int
    count: int
    errors: list[str]


class Index:
    def __init__(self, db: sqlmodel.Session, search_client: typesense.client.Client):
        self._db = db
        self._search_client = search_client

        self._logger = log.init("service")

    def call(self) -> Struct:
        struct = Struct(0, 0, [])

        self._logger.info(f"{context.rid_get()} {__name__}")

        struct.count += self._index_prules()
        struct.count += self._index_vrules()

        return struct

    def _index_prules(self) -> int:
        """index price rules"""
        count = 0

        vendor_ids = self._vendor_ids()
        collection_name = models.VariantPruleSchema.typesense_collection()

        for vendor_id in vendor_ids:
            # find all vendor pricing rules
            rules = self._db.exec(sqlmodel.select(models.VariantPrule).where(models.VariantPrule.vendor_id == vendor_id)).all()

            for rule in rules:
                if not rule.variant_id:
                    if rule.product_id:
                        variant_ids = self._vendor_variant_ids(vendor_id=rule.vendor_id, product_id=rule.product_id)
                    else:
                        variant_ids = [0]
                else:
                    variant_ids = [rule.variant_id]

                document = models.VariantPruleDocument(vendor_id=rule.vendor_id, variant_ids=variant_ids, prule=rule).document()

                self._search_client.collections[collection_name].documents.create(document)

                count += 1

                self._logger.info(
                    f"{context.rid_get()} {__name__} collection {collection_name} prule {rule.id} variant_ids {variant_ids} version {rule.version}"
                )

        return count

    def _index_vrules(self) -> int:
        """index visibility rules"""
        count = 0

        vendor_ids = self._vendor_ids()
        collection_name = models.VariantVruleSchema.typesense_collection()

        for vendor_id in vendor_ids:
            # find all vendor visibility rules, partitioned by dispensary class vs no dispensary class
            rules_class_none = self._db.exec(
                sqlmodel.select(models.VariantVrule).where(
                    models.VariantVrule.enabled == True,
                    models.VariantVrule.vendor_id == vendor_id,
                    models.VariantVrule.dispensary_class_id == None,
                )
            ).all()

            rules_class_exists = self._db.exec(
                sqlmodel.select(models.VariantVrule).where(
                    models.VariantVrule.enabled == True,
                    models.VariantVrule.vendor_id == vendor_id,
                    models.VariantVrule.dispensary_class_id != None,
                )
            ).all()

            # map each rule to variant ids set
            dispensary_rules_map = {0: collections.OrderedDict()}

            for rule in rules_class_none:
                dispensary_rules_map[0][rule.id] = {
                    "rule": rule,
                    "variants": self._rule_variant_ids(rule=rule),
                }

            for rule in rules_class_exists:
                if rule.dispensary_class_id not in dispensary_rules_map:
                    dispensary_rules_map[rule.dispensary_class_id] = {}

                dispensary_rules_map[rule.dispensary_class_id][rule.id] = {
                    "rule": rule,
                    "variants": self._rule_variant_ids(rule=rule),
                }

            # add vendor variant rules for each dispensary class

            vendor_variant_ids = self._vendor_variant_ids(vendor_id=vendor_id)

            for variant_id in vendor_variant_ids:
                variant = self._db.exec(sqlmodel.select(models.Variant).where(models.Variant.id == variant_id)).first()
                product = self._db.exec(sqlmodel.select(models.Product).where(models.Product.id == variant.product_id)).first()

                for dispensary_class_id in dispensary_rules_map.keys():
                    # check for a matching rule
                    rule = self._rule_match(variant_id=variant_id, rule_map=dispensary_rules_map[dispensary_class_id])

                    document = models.VariantVruleDocument(variant, product, dispensary_class_id, rule).document()

                    self._search_client.collections[collection_name].documents.create(document)

                    count += 1

                    self._logger.info(
                        f"{context.rid_get()} {__name__} collection {collection_name} variant {variant.id} dispensary_class {dispensary_class_id} vrule {rule.id if rule else 'system'}"
                    )

        return count

    def _rule_match(self, variant_id: int, rule_map: collections.OrderedDict) -> typing.Optional[models.VariantVrule]:
        for _rule_id, rule_dict in rule_map.items():
            if variant_id in rule_dict["variants"]:
                return rule_dict["rule"]

        return None

    def _rule_variant_ids(self, rule: models.VariantVrule) -> list[int]:
        if rule.variant_id:
            return [rule.variant_id]

        return self._vendor_variant_ids(vendor_id=rule.vendor_id, product_id=rule.product_id)

    def _vendor_ids(self) -> list[int]:
        dataset = sqlmodel.select(
            models.Vendor.id,
        ).distinct()

        return self._db.exec(dataset).all()

    def _vendor_product_ids(self, vendor_id: int) -> list[int]:
        dataset = (
            sqlmodel.select(
                models.Product.id,
            )
            .where(models.Product.vendor_id == vendor_id)
            .distinct()
        )

        return self._db.exec(dataset).all()

    def _vendor_variant_ids(self, vendor_id: int, product_id: typing.Optional[int] = None) -> list[int]:
        if product_id:
            product_ids = [product_id]
        else:
            product_ids = self._vendor_product_ids(vendor_id=vendor_id)

        dataset = (
            sqlmodel.select(
                models.Variant.id,
            )
            .where(models.Variant.product_id.in_(product_ids))
            .distinct()
        )

        return self._db.exec(dataset).all()
        return self._db.exec(dataset).all()

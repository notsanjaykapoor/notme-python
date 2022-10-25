import dataclasses

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
                    # todo - expand to variant ids
                    pass
                else:
                    variant_ids = [rule.variant_id]

                variants = self._db.exec(sqlmodel.select(models.Variant).where(models.Variant.id.in_(variant_ids))).all()

                for variant in variants:
                    product = self._db.exec(sqlmodel.select(models.Product).where(models.Product.id == variant.product_id)).first()
                    document = models.VariantPruleDocument(variant, product, rule).document()

                    self._search_client.collections[collection_name].documents.create(document)

                    count += 1

                    self._logger.info(
                        f"{context.rid_get()} {__name__} collection {collection_name} variant {variant.id} prule {rule.id} version {rule.version}"
                    )

        return count

    def _index_vrules(self) -> int:
        """index visibility rules"""
        count = 0

        vendor_ids = self._vendor_ids()
        collection_name = models.VariantVruleSchema.typesense_collection()

        for vendor_id in vendor_ids:
            # find all vendor visibility rules
            rules = self._db.exec(sqlmodel.select(models.VariantVrule).where(models.VariantVrule.vendor_id == vendor_id)).all()

            for rule in rules:
                if not rule.variant_id:
                    # todo - expand to variant ids
                    pass
                else:
                    variant_ids = [rule.variant_id]

                variants = self._db.exec(sqlmodel.select(models.Variant).where(models.Variant.id.in_(variant_ids))).all()

                for variant in variants:
                    # create and index search document
                    product = self._db.exec(sqlmodel.select(models.Product).where(models.Product.id == variant.product_id)).first()

                    document = models.VariantVruleDocument(variant, product, rule).document()

                    self._search_client.collections[collection_name].documents.create(document)

                    # variant_ids_unique.add(variant.id)

                    count += 1

                    self._logger.info(
                        f"{context.rid_get()} {__name__} collection {collection_name} variant {variant.id} vrule {rule.id} version {rule.version}"
                    )

            # add vendor variant default system rules

            vendor_variant_ids = self._vendor_variant_ids(vendor_id=vendor_id)

            for variant_id in vendor_variant_ids:
                variant = self._db.exec(sqlmodel.select(models.Variant).where(models.Variant.id == variant_id)).first()
                product = self._db.exec(sqlmodel.select(models.Product).where(models.Product.id == variant.product_id)).first()
                document = models.VariantVruleDocument(variant, product, None).document()

                self._search_client.collections[collection_name].documents.create(document)

                count += 1

                self._logger.info(f"{context.rid_get()} {__name__} collection {collection_name} variant {variant.id} vrule default")

        return count

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

    def _vendor_variant_ids(self, vendor_id: int) -> list[int]:
        product_ids = self._vendor_product_ids(vendor_id=vendor_id)

        dataset = (
            sqlmodel.select(
                models.Variant.id,
            )
            .where(models.Variant.product_id.in_(product_ids))
            .distinct()
        )

        return self._db.exec(dataset).all()

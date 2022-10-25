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

        collection_name = models.VariantPruleSchema.typesense_collection()

        rules = self._db.exec(sqlmodel.select(models.VariantPrule)).all()

        for rule in rules:
            if not rule.variant_id:
                # todo - expand to variant ids
                pass
            else:
                variant_ids = [rule.variant_id]

            variants = self._db.exec(sqlmodel.select(models.Variant).where(models.Variant.id.in_(variant_ids))).all()

            for variant in variants:
                document = models.VariantPruleDocument(variant, rule).document()

                self._search_client.collections[collection_name].documents.create(document)

                count += 1

                self._logger.info(
                    f"{context.rid_get()} {__name__} collection {collection_name} variant {variant.id} prule {rule.id} version {rule.version}"
                )

        return count

    def _index_vrules(self) -> int:
        """index visibility rules"""
        count = 0

        collection_name = models.VariantVruleSchema.typesense_collection()
        variant_ids_unique = set()

        rules = self._db.exec(sqlmodel.select(models.VariantVrule)).all()

        for rule in rules:
            if not rule.variant_id:
                # todo - expand to variant ids
                pass
            else:
                variant_ids = [rule.variant_id]

            variants = self._db.exec(sqlmodel.select(models.Variant).where(models.Variant.id.in_(variant_ids))).all()

            for variant in variants:
                document = models.VariantVruleDocument(variant, rule).document()

                self._search_client.collections[collection_name].documents.create(document)

                variant_ids_unique.add(variant.id)

                count += 1

                self._logger.info(
                    f"{context.rid_get()} {__name__} collection {collection_name} variant {variant.id} vrule {rule.id} version {rule.version}"
                )

        # add default system rules

        for variant_id in variant_ids_unique:
            document = models.VariantVruleDocument(variant, None).document()

            self._search_client.collections[collection_name].documents.create(document)

            count += 1

            self._logger.info(f"{context.rid_get()} {__name__} collection {collection_name} variant {variant.id} vrule default")

        return count

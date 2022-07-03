import base64
import dataclasses
import datetime
import json
import os

import pydantic
import sqlmodel
import webauthn
import webauthn.helpers.structs
import webauthn.registration.verify_registration_response

import context
import log
import models
import services.credentials
import services.webauthn.register


@dataclasses.dataclass
class Struct:
    code: int
    errors: list[str]


class CompleteParams(pydantic.BaseModel):
    challenge: str
    credential: dict
    user_id: str


class Complete:
    def __init__(self, params: CompleteParams, db: sqlmodel.Session):
        self._db = db
        self._params = params

        self._challenge = self._params.challenge
        self._credential = self._params.credential
        self._user_id = self._params.user_id
        self._creds_query = f"user_id:{self._user_id}"

        self._rp_domain = os.environ.get("WEBAUTHN_RP_DOMAIN")
        self._rp_origin = os.environ.get("WEBAUTHN_RP_ORIGIN")
        self._logger = log.init("service")

    def call(self) -> Struct:
        struct = Struct(0, [])

        self._logger.info(f"{context.rid_get()} {__name__} user_id {self._user_id} try")

        # find matching user credentials
        creds_query = services.credentials.List(query=self._creds_query, offset=0, limit=10, db=self._db).call()

        if not creds_query.count:
            self._logger.error(f"{context.rid_get()} {__name__} user_id {self._user_id} missing credentials")
            struct.code = 401
            return struct

        # current_challenge = services.webauthn.register.challenge_get(self._user_id)

        # self._logger.info(f"{context.rid_get()} {__name__} user_id {self._user_id} challenge {self._challenge}")

        for credential in creds_query.objects:
            code = self._verify(credential=credential)

            if code == 0:
                self._logger.info(f"{context.rid_get()} {__name__} user_id {self._user_id} ok")
                return struct

        struct.code = 401

        self._logger.error(f"{context.rid_get()} {__name__} user_id {self._user_id} failed")

        return struct

    def _verify(self, credential: models.Credential) -> int:
        """returns 0 if credential matches; 1 otherwise"""

        try:
            webauthn.verify_authentication_response(
                credential=webauthn.helpers.structs.AuthenticationCredential.parse_raw(json.dumps(self._credential)),
                expected_challenge=webauthn.base64url_to_bytes(self._challenge),
                expected_rp_id=self._rp_domain,
                expected_origin=self._rp_origin,
                credential_public_key=credential.public_key_bytes,
                credential_current_sign_count=credential.sign_count,
                require_user_verification=False,
            )
        except Exception as e:
            self._logger.error(f"{context.rid_get()} {__name__} error {str(e)}")
            return 1

        return 0

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
import services.credentials
import services.users
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

        self._rp_domain = os.environ.get("WEBAUTHN_RP_DOMAIN")
        self._rp_origin = os.environ.get("WEBAUTHN_RP_ORIGIN")
        self._logger = log.init("service")

    def call(self) -> Struct:
        struct = Struct(0, [])

        self._logger.info(f"{context.rid_get()} {__name__} user_id {self._user_id} params {self._params}")

        try:
            # parse_raw requires a string, so convert dict back to json string
            credential = webauthn.helpers.structs.RegistrationCredential.parse_raw(json.dumps(self._credential))

            # self._logger.info(f"{context.rid_get()} {__name__} user_id {self._user_id} credential parse {credential}")

            current_challenge = services.webauthn.register.challenge_get(self._user_id)

            if not current_challenge:
                struct.code = 422
                self._logger.error(f"{context.rid_get()} {__name__} user_id {self._user_id} challenge not found")

            verification: webauthn.registration.verify_registration_response.VerifiedRegistration = webauthn.verify_registration_response(
                credential=credential,
                expected_challenge=current_challenge,
                expected_rp_id=self._rp_domain,
                expected_origin=self._rp_origin,
                require_user_verification=False,
            )

            self._logger.info(f"{context.rid_get()} {__name__} user_id {self._user_id} verification {type(verification)}")

            self._logger.info(f"{context.rid_get()} {__name__} user_id {self._user_id} verification {verification}")

            # check/create user

            self._user_check_create()

            # create user credential

            self._credential_create(verification)

            self._logger.info(f"{context.rid_get()} {__name__} user_id {self._user_id} verification ok")
        except Exception as e:
            self._logger.error(f"{context.rid_get()} {__name__} error {str(e)}")

        return struct

    def _credential_create(self, verification: webauthn.registration.verify_registration_response.VerifiedRegistration) -> int:
        cred_object = {
            "name": f"{self._user_id}-cred",
            "public_key": base64.b64encode(verification.credential_public_key),
            "sign_count": verification.sign_count,
            "timestamp": datetime.datetime.utcnow(),
            "user_id": self._user_id,
            "webauthn_id": base64.b64encode(verification.credential_id),
        }

        struct = services.credentials.Create(
            object=cred_object,
            db=self._db,
        ).call()

        return struct.code

    def _user_check_create(self) -> int:
        struct_list = services.users.List(
            query=f"user_id:{self._user_id}",
            offset=0,
            limit=1,
            db=self._db,
        ).call()

        if struct_list.objects:
            return 0

        # create user

        struct_create = services.users.Create(
            user_id=self._user_id,
            db=self._db,
        ).call()

        return struct_create.code

import base64
import dataclasses
import os

import pydantic
import sqlmodel
import webauthn
import webauthn.helpers.structs

import context
import log
import services.credentials
import services.webauthn.register


@dataclasses.dataclass
class Struct:
    code: int
    object: str
    errors: list[str]


class InitParams(pydantic.BaseModel):
    user_id: str


class Init:
    def __init__(self, params: InitParams, db: sqlmodel.Session):
        self._db = db
        self._params = params

        self._user_id = self._params.user_id
        self._creds_query = f"user_id:{self._user_id}"

        self._rp_domain = os.environ.get("WEBAUTHN_RP_DOMAIN")
        self._logger = log.init("service")

    def call(self) -> Struct:
        struct = Struct(0, "", [])

        # find matching user credentials
        creds_query = services.credentials.List(query=self._creds_query, offset=0, limit=10, db=self._db).call()

        if not creds_query.count:
            self._logger.error(f"{context.rid_get()} {__name__} user_id {self._user_id} missing credentials")
            struct.code = 401
            return struct

        self._logger.info(f"{context.rid_get()} {__name__} user_id {self._user_id} creds {creds_query.count}")

        # build creds list for webauthn client
        creds_allowed = [webauthn.helpers.structs.PublicKeyCredentialDescriptor(id=object.webauthn_bytes) for object in creds_query.objects]

        options: webauthn.helpers.structs.PublicKeyCredentialRequestOptions = webauthn.generate_authentication_options(
            allow_credentials=creds_allowed,
            # the domain on which WebAuthn is being used
            rp_id=self._rp_domain,
            # user verification should not occur, but its ok if it does
            user_verification=webauthn.helpers.structs.UserVerificationRequirement.DISCOURAGED,
        )

        struct.object = webauthn.options_to_json(options)

        self._logger.info(f"{context.rid_get()} {__name__} user_id {self._user_id} ok")

        return struct

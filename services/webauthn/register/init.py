import dataclasses
import os

import pydantic
import sqlmodel
import webauthn
import webauthn.helpers.structs

import context
import log
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

        self._rp_domain = os.environ.get("WEBAUTHN_RP_DOMAIN")
        self._rp_name = os.environ.get("WEBAUTHN_RP_NAME")
        self._logger = log.init("service")

    def call(self) -> Struct:
        struct = Struct(0, "", [])

        self._logger.info(f"{context.rid_get()} {__name__} user_id {self._user_id}")

        options: webauthn.helpers.structs.PublicKeyCredentialCreationOptions = webauthn.generate_registration_options(
            # A name for your "Relying Party" server
            rp_name=self._rp_name,
            # Your domain on which WebAuthn is being used
            rp_id=self._rp_domain,
            # An assigned random identifier;
            # never anything user-identifying like an email address
            user_id=self._user_id,
            # A user-visible hint of which account this credential belongs to
            # An email address is fine here
            user_name=self._user_id,
            # Require the user to verify their identity to the authenticator
            authenticator_selection=webauthn.helpers.structs.AuthenticatorSelectionCriteria(
                user_verification=webauthn.helpers.structs.UserVerificationRequirement.DISCOURAGED,
            ),
        )

        services.webauthn.register.challenge_set(self._user_id, options.challenge)

        struct.object = webauthn.options_to_json(options)

        self._logger.info(f"{context.rid_get()} {__name__} object {struct.object}")

        return struct

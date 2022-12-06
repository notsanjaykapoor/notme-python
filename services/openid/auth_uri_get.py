import dataclasses
import os
import re

import requests_oauthlib
import ulid

import context
import log


@dataclasses.dataclass
class Struct:
    code: int
    uri: str
    errors: list[str]


IDP_REGEX = "^authentik|google$"
IDP_ERROR = "idp must be authentik or google"


class AuthUriGet:
    def __init__(self, idp: str):
        self._idp = idp

        self._scope = ["openid email"]
        self._state = ulid.new().str
        self._logger = log.init("service")

    def call(self) -> Struct:
        struct = Struct(0, "", [])

        self._logger.info(f"{context.rid_get()} {__name__} idp {self._idp} try")

        if not re.match(IDP_REGEX, self._idp):
            struct.code = 422
            struct.errors.append(IDP_ERROR)
            return struct

        if self._idp == "authentik":
            client_id = os.environ.get("OPENID_AUTHENTIK_CLIENT_ID")
            oauth_uri = os.environ.get("OPENID_AUTHENTIK_AUTH_URI")
            redirect_uri = os.environ.get("OPENID_AUTHENTIK_REDIRECT_URI")
        elif self._idp == "google":
            client_id = os.environ.get("OPENID_GOOGLE_CLIENT_ID")
            oauth_uri = os.environ.get("OPENID_GOOGLE_AUTH_URI")
            redirect_uri = os.environ.get("OPENID_GOOGLE_REDIRECT_URI")

        try:
            oauth_session = requests_oauthlib.OAuth2Session(client_id, redirect_uri=redirect_uri, scope=self._scope)

            struct.uri, _state = oauth_session.authorization_url(
                oauth_uri,
                state=self._state,
            )
        except Exception as e:
            struct.code = 500
            struct.errors.append(str(e))

            self._logger.error(f"{context.rid_get()} {__name__}  exception {e}", exc_info=1)

        return struct

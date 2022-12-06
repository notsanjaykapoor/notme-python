import dataclasses
import json
import os
import re

import requests_oauthlib

import context
import log


@dataclasses.dataclass
class Struct:
    code: int
    email: str
    token: str
    errors: list[str]


IDP_REGEX = "^authentik|google$"
IDP_ERROR = "idp must be authentik or google"


class AuthCallback:
    def __init__(self, idp: str, code: str, state: str):
        self._idp = idp
        self._code = code
        self._state = state

        self._logger = log.init("service")

    def call(self) -> Struct:
        struct = Struct(0, "", "", [])

        self._logger.info(f"{context.rid_get()} {__name__} idp {self._idp} try")

        if not re.match(self._idp, IDP_REGEX):
            struct.code = 422
            struct.errors.append(IDP_ERROR)
            return struct

        if self._idp == "authentik":
            client_id = os.environ.get("OPENID_AUTHENTIK_CLIENT_ID")
            client_secret = os.environ.get("OPENID_AUTHENTIK_CLIENT_SECRET")
            redirect_uri = os.environ.get("OPENID_AUTHENTIK_REDIRECT_URI")
            token_uri = os.environ.get("OPENID_AUTHENTIK_TOKEN_URI")
            userinfo_uri = os.environ.get("OPENID_AUTHENTIK_USERINFO_URI")
        elif self._idp == "google":
            client_id = os.environ.get("OPENID_GOOGLE_CLIENT_ID")
            client_secret = os.environ.get("OPENID_GOOGLE_CLIENT_SECRET")
            redirect_uri = os.environ.get("OPENID_GOOGLE_REDIRECT_URI")
            token_uri = os.environ.get("OPENID_GOOGLE_TOKEN_URI")
            userinfo_uri = os.environ.get("OPENID_GOOGLE_USERINFO_URI")

        try:
            oauth_session = requests_oauthlib.OAuth2Session(client_id, redirect_uri=redirect_uri, state=self._state)

            token = oauth_session.fetch_token(
                token_uri,
                code=self._code,
                client_secret=client_secret,
            )

            struct.token = token["access_token"]

            self._logger.info(f"{context.rid_get()} {__name__} token {token}")

            user_response = oauth_session.get(userinfo_uri)

            if user_response.status_code != 200:
                struct.code = user_response.status_code
                struct.errors.append("userinfo_uri error")
                return struct

            user_json = json.loads(user_response.content)
            struct.email = user_json["email"]

            self._logger.info(f"{context.rid_get()} {__name__} email {struct.email}")
        except Exception as e:
            struct.code = 500
            struct.errors.append(str(e))

            self._logger.error(f"{context.rid_get()} {__name__} exception {e}", exc_info=1)

        return struct

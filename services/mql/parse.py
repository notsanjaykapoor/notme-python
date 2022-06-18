import urllib
from dataclasses import dataclass


@dataclass
class Struct:
    code: int
    tokens: list[dict]
    errors: list[str]


class Parse:
    def __init__(self, query: str):
        self.query = query

    def call(self):
        struct = Struct(0, [], [])

        tokens = self.query.split(" ")

        for token in tokens:
            if len(token) == 0:
                # no more tokens to parse
                break

            field, value = token.split(":")

            # url unparse value, e.g' 'foo+1' => 'foo 1'
            value_parsed = urllib.parse.unquote_plus(value)

            # append to list
            struct.tokens.append(
                {
                    "field": field,
                    "value": value_parsed,
                }
            )

        return struct

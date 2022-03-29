from dataclasses import dataclass

@dataclass
class Struct:
  code: int
  tokens: list[{}]
  errors: list[str]

class MqlParse:
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

      # append to list
      struct.tokens.append({
        "field": field,
        "value": value,
      })

    return struct

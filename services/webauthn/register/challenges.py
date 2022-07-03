CHALLENGES: dict = {}


def challenge_get(user_id: str) -> bytes:
    return CHALLENGES.get(user_id, b"")


def challenge_set(user_id: str, challenge: bytes):
    CHALLENGES[user_id] = challenge

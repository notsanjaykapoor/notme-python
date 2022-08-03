import re

import bytewax


def file_input():
    for line in open("./data/chess/mega2400_part_01.pgn.txt", encoding="ISO-8859-1"):
        yield 1, line


def line_token(line: str) -> str:
    token = line.split(" ")[1]
    token = re.sub("]", "", token).strip()

    return token


def result_count(s: str) -> tuple[str, int]:
    return s, 1


def result_add(count1: int, count2: int) -> int:
    return count1 + count2


flow = bytewax.Dataflow()
flow.filter(lambda s: "Result" in s)
flow.map(line_token)
flow.map(result_count)
flow.reduce_epoch(result_add)
flow.capture()

for epoch, item in bytewax.run(flow, file_input()):
    print(f"epoch {epoch} item {item}")

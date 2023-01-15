import contextvars
import csv
import typing

_input_csv: contextvars.ContextVar = contextvars.ContextVar("input_csv", default="")


def input_csv_generator(worker_index: int, workers_count: int, resume_state: str) -> typing.Generator[tuple[int, dict], None, None]:
    file = _input_csv.get()

    if not file:
        raise ValueError("input file missing")

    with open(file) as csvfile:
        reader_raw = csv.reader(csvfile)

        for fields in reader_raw:
            # check if row looks like a header line
            if _csv_header(fields):
                fieldnames = [field.lower() for field in fields]
                break

        # continue reading file with dict reader and field names set
        reader_dict = csv.DictReader(csvfile, fieldnames=fieldnames)

        for row_dict in reader_dict:
            # print(f"row {row_dict}")
            yield 1, row_dict


def input_csv_params(file: str) -> int:
    _input_csv.set(file)
    return 0


_input_csv_random: contextvars.ContextVar = contextvars.ContextVar("input_csv_random", default="")


def input_csv_random_generator(worker_index: int, workers_count: int, resume_state: str) -> typing.Generator[tuple[int, dict], None, None]:
    file, count = _input_csv_random.get().split(":")
    count = int(count)

    if not file:
        raise ValueError("input file missing")

    with open(file) as csvfile:
        reader_raw = csv.reader(csvfile)

        for fields in reader_raw:
            # check if row looks like a header line
            if _csv_header(fields):
                fieldnames = [field.lower() for field in fields]
                break

        # continue reading file with dict reader and field names set
        reader_dict = csv.DictReader(csvfile, fieldnames=fieldnames)

        for row_template in reader_dict:
            # randomize data in each row
            rows = _csv_row_randomize(row_template, count)

            for row in rows:
                yield 1, row


def input_csv_random_params(file: str, count: int) -> int:
    _input_csv_random.set(f"{file}:{count}")
    return 0


def _csv_header(fields: list[str]) -> bool:
    if not fields[0] or not fields[1]:
        # row is empty
        return False

    return True


def _csv_row_randomize(row_template: dict, count: int) -> list[dict]:
    random_data: list[dict] = []

    row_keys = sorted([key for key in row_template.keys() if key])

    if not row_keys == ["email", "name", "record_id"]:
        # todo: unsupported format
        random_data.append(row_template)
        return random_data

    # generate random data
    row_counter = range(count)

    for i in row_counter:
        row_object = {
            "name": f"User {i}",
            "email": f"user-{i}@gmail.com",
            "record_id": [i, i + 1],  # multi-value key
        }
        random_data.append(row_object)

    return random_data

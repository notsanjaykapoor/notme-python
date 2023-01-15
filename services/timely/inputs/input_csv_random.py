import csv
import typing


class InputCsvRandom:
    def __init__(self, file: str, count: int):
        self._file = file
        self._count = count

    def call(self, worker_index, workers_count, resume_state) -> typing.Generator[tuple[int, dict], None, None]:
        with open(self._file) as csvfile:
            reader_raw = csv.reader(csvfile)

            for fields in reader_raw:
                # check if row looks like a header line
                if self._csv_header(fields):
                    fieldnames = [field.lower() for field in fields]
                    break

            # continue reading file with dict reader and field names set
            reader_dict = csv.DictReader(csvfile, fieldnames=fieldnames)

            for row_template in reader_dict:
                # randomize data in each row
                rows = self._csv_row_randomize(row_template, self._count)

                for row in rows:
                    yield 1, row

    def _csv_header(self, fields: list[str]) -> bool:
        if not fields[0] or not fields[1]:
            # row is empty
            return False

        return True

    def _csv_row_randomize(self, row_template: dict, count: int) -> list[dict]:
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

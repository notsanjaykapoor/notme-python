import csv
import typing


def stream_csv(file: str) -> typing.Generator[tuple[int, dict], None, None]:
    with open(file) as csvfile:
        reader_raw = csv.reader(csvfile)

        for fields in reader_raw:
            # check if row looks like a header line
            if _csv_header(fields):
                fieldnames = fields
                break

        # continue reading file with dict reader and field names set
        reader_dict = csv.DictReader(csvfile, fieldnames=fieldnames)
        for row_dict in reader_dict:
            print(f"row {row_dict}")
            yield 1, row_dict


def _csv_header(fields: list[str]) -> bool:
    if not fields[0] or not fields[1]:
        # row is empty
        return False

    return True

from contextlib import nullcontext as does_not_raise

import csv

from src.downloader import get_metadata, COL_NAMES


def test_get_metadata():
    with does_not_raise():
        get_metadata()

        with open("out/metadata.csv", "r") as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)

    assert header == COL_NAMES

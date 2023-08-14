import csv
from collections import namedtuple

from src.downloader import COL_NAMES


Item = namedtuple("Item", COL_NAMES)


def read_data():
    with open("out/metadata.csv", "r") as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # skip the header
        for item in map(Item._make, reader):
            yield item

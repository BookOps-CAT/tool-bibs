import sys

from src.downloader import get_metadata
from src.producer import create_bibs


if __name__ == "__main__":
    get_metadata()
    last_sequence_no = sys.argv[1]
    create_bibs(last_sequence_no)

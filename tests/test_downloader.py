from contextlib import nullcontext as does_not_raise

import pytest

from src.downloader import get_metadata


def test_get_metadata():
    with does_not_raise():
        get_metadata()
# tests/test_extract_title.py
import pytest
from utils import extract_title, TitleNotFoundError


@pytest.mark.parametrize(
    "md,expected",
    [
        ("# Hello", "Hello"),
        ("#   Hello   ", "Hello"),
        ("   # Hello", "Hello"),
        ("#Hello", "Hello"),
        ("#   Hello World\n\nSome text", "Hello World"),
    ],
)
def test_extract_title_basic(md, expected):
    assert extract_title(md) == expected


def test_extract_title_missing():
    with pytest.raises(TitleNotFoundError):
        extract_title("No heading here\nJust *markdown*.")
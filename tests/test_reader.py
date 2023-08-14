from src.reader import read_data, Item


def test_read_data():
    reader = read_data()
    for item in reader:
        assert isinstance(item, Item)

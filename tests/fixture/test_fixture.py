import os


def test_runs():
    assert sum([1, 1]) == 2


def test_setup_input_ran():
    assert os.environ.get("FIXTURE_SETUP") == "ran"


def parity(n):
    if n % 2:
        return "odd"
    return "even"


def test_parity():
    assert parity(2) == "even"
    assert parity(3) == "odd"

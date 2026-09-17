import os


def test_runs():
    assert sum([1, 1]) == 2


def test_setup_input_ran():
    assert os.environ.get("FIXTURE_SETUP") == "ran"


def parity(n):
    return "even" if n % 2 == 0 else "odd"


def test_parity():
    assert parity(2) == "even"
    assert parity(3) == "odd"

import os


def test_runs():
    assert sum([1, 1]) == 2


def test_setup_input_ran():
    assert os.environ.get("FIXTURE_SETUP") == "ran"

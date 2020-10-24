import os

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
LOCUST_DIR = os.path.dirname(TESTS_DIR)
TESTCASES_DIR = os.environ.get("LOCUST_TESTCASES_DIR")
if TESTCASES_DIR is None:
    raise ValueError(
        "Cannot run tests without LOCUST_TESTCASES_DIR (environment variable)"
    )
TESTCASES_DIR = os.path.normpath(TESTCASES_DIR)

TESTCASES_REMOTE = os.environ.get("LOCUST_TESTCASES_REMOTE", "origin")

REPO_DIR_TOKEN = "#repo_dir#"

import os

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
LOCUST_DIR = os.path.dirname(TESTS_DIR)
TESTCASES_DIR = os.path.join(LOCUST_DIR, "testcases")
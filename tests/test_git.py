import json
import os
import unittest

from locust import git

from . import config


class TestLocustGit(unittest.TestCase):
    def test_git_run(self):
        repo_dir = config.TESTCASES_DIR
        initial = "test_git_initial"
        terminal = "test_git_terminal"

        expected_result_fixture = os.path.join(
            config.TESTS_DIR, "fixtures", "test_git.json"
        )
        with open(expected_result_fixture) as ifp:
            expected_result_json = json.load(ifp)

        result = git.run(repo_dir, initial, terminal)
        result_json = result.dict()

        self.assertDictEqual(result_json, expected_result_json)

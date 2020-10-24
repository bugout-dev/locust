import json
import os
import unittest

from locust import git

from . import config


class TestLocustGit(unittest.TestCase):
    def test_git_run(self):
        repo_dir = config.TESTCASES_DIR
        initial = f"{config.TESTCASES_REMOTE}/test_git_initial"
        terminal = f"{config.TESTCASES_REMOTE}/test_git_terminal"

        expected_result_fixture = os.path.join(
            config.TESTS_DIR, "fixtures", "test_git.json"
        )
        with open(expected_result_fixture) as ifp:
            expected_result_str = repo_dir.join(
                ifp.read().strip().split(config.REPO_DIR_TOKEN)
            )
        expected_result_json = json.loads(expected_result_str)

        result = git.run(repo_dir, initial, terminal)
        result_json = result.dict()

        self.assertDictEqual(result_json, expected_result_json)

import json
import os
import unittest

from locust import git, parse

from . import config


class TestLocustParse(unittest.TestCase):
    def test_parse_run(self):
        repo_dir = config.TESTCASES_DIR
        initial = f"{config.TESTCASES_REMOTE}/test_git_initial"
        terminal = f"{config.TESTCASES_REMOTE}/test_git_terminal"

        test_input_fixture = os.path.join(config.TESTS_DIR, "fixtures", "test_git.json")
        with open(test_input_fixture) as ifp:
            test_input_str = repo_dir.join(
                ifp.read().strip().split(config.REPO_DIR_TOKEN)
            )
        test_input_object = json.loads(test_input_str)
        test_input = git.RunResponse.parse_obj(test_input_object)

        expected_result_fixture = os.path.join(
            config.TESTS_DIR, "fixtures", "test_parse.json"
        )
        with open(expected_result_fixture) as ifp:
            expected_result_str = repo_dir.join(
                ifp.read().strip().split(config.REPO_DIR_TOKEN)
            )
        expected_result_json = json.loads(expected_result_str)

        result = parse.run(test_input)
        result_json = result.dict()

        self.assertDictEqual(result_json, expected_result_json)

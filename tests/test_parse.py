import json
import os
import unittest

from locust import git, parse

from . import config


class TestLocustGit(unittest.TestCase):
    def test_parse_run(self):
        repo_dir = config.TESTCASES_DIR
        initial = "test_git_initial"
        terminal = "test_git_terminal"

        test_input_fixture = os.path.join(config.TESTS_DIR, "fixtures", "test_git.json")
        with open(test_input_fixture) as ifp:
            test_input_object = json.load(ifp)

        test_input = git.RunResponse.parse_obj(test_input_object)

        expected_result_fixture = os.path.join(
            config.TESTS_DIR, "fixtures", "test_parse.json"
        )
        with open(expected_result_fixture) as ifp:
            expected_result_json = json.load(ifp)

        result = parse.run(test_input)
        result_json = result.dict()

        self.assertDictEqual(result_json, expected_result_json)
